"""Copyright (c) 2022 VIKTOR B.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

VIKTOR B.V. PROVIDES THIS SOFTWARE ON AN "AS IS" BASIS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from shapely.geometry import LineString
from shapely.ops import substring

from viktor.core import ViktorController
from viktor.external.scia import Material as SciaMaterial
from viktor.external.scia import Model as SciaModel
from viktor.geometry import Extrusion
from viktor.geometry import GeoPoint
from viktor.geometry import GeoPolygon
from viktor.geometry import GeoPolyline
from viktor.geometry import Group
from viktor.geometry import Line
from viktor.geometry import Material
from viktor.geometry import Point
from viktor.views import GeometryResult
from viktor.views import GeometryView
from viktor.views import MapPolygon
from viktor.views import MapPolyline
from viktor.views import MapResult
from viktor.views import MapView
from .parametrization import TunnelParametrization


class TunnelController(ViktorController):
    """Controller class which acts as interface for the Sample entity type."""
    label = "Tunnel"
    parametrization = TunnelParametrization
    viktor_convert_entity_field = True

    @MapView('Map', duration_guess=2)
    def visualize_tunnel(self, params, **kwargs) -> MapResult:
        """Set the map view on which the line can be drawn for the tunnel and segments are filled in"""
        if not params.step1.geo_polyline:
            return MapResult([])

        features = []

        line_string = LineString([pt.rd for pt in params.step1.geo_polyline.points])
        segment_length = line_string.length / params.step1.segments
        for i in range(0, params.step1.segments):
            begin = i * segment_length
            end = (i + 1) * segment_length
            line_string_sub = substring(line_string, begin, end)
            left_line = line_string_sub.parallel_offset(40, 'left')
            right_line = line_string_sub.parallel_offset(40, 'right')
            linestring_points = list(left_line.coords) + list(right_line.coords)
            polygon = GeoPolygon(*[GeoPoint.from_rd(pt) for pt in linestring_points])
            features.append(MapPolygon.from_geo_polygon(polygon))

        features.append(MapPolyline.from_geo_polyline(params.step1.geo_polyline))
        return MapResult(features)

    @GeometryView("3D", duration_guess=1)
    def visualize_tunnel_segment(self, params, **kwargs):
        """"create a SCIA model and views it as a 3D model"""
        scia_model = self.create_scia_model(params)
        geometry_group = self.create_visualization_geometries(params, scia_model)
        return GeometryResult(geometry_group)

    def create_scia_model(self, params) -> SciaModel:
        model = SciaModel()

        # create floor slab
        line_string = LineString([pt.rd for pt in params.step1.geo_polyline.points])
        length = line_string.length / params.step1.segments

        width = params.step2.width
        height = params.step2.height
        floor_thickness = params.step2.floor_thickness
        roof_thickness = params.step2.roof_thickness

        node_floor_1 = model.create_node('node_floor_1', 0, 0, 0)  # origin
        node_floor_2 = model.create_node('node_floor_2', 0, length, 0)
        node_floor_3 = model.create_node('node_floor_3', width, length, 0)
        node_floor_4 = model.create_node('node_floor_4', width, 0, 0)
        floor_nodes = [node_floor_1, node_floor_2, node_floor_3, node_floor_4]
        material = SciaMaterial(0, 'concrete_slab')
        model.create_plane(floor_nodes, floor_thickness, name='floor slab', material=material)

        node_roof_1 = model.create_node('node_roof_1', 0, 0, height)
        node_roof_2 = model.create_node('node_roof_2', 0, length, height)
        node_roof_3 = model.create_node('node_roof_3', width, length, height)
        node_roof_4 = model.create_node('node_roof_4', width, 0, height)
        roof_nodes = [node_roof_1, node_roof_2, node_roof_3, node_roof_4]
        model.create_plane(roof_nodes, roof_thickness, name='roof slab', material=material)

        return model


    def create_visualization_geometries(self, params, scia_model):
        """The SCIA model is converted to VIKTOR geometry here"""
        geometry_group = Group([])
        # for node in scia_model.nodes:
        #     node_obj = Sphere(Point(node.x, node.y, node.z), 1)
        #     node_obj.material = Material('node', color=Color(0, 255, 0))
        #     geometry_group.add(node_obj)

        floor_points = [
            Point(scia_model.nodes[0].x, scia_model.nodes[0].y, scia_model.nodes[0].z),
            Point(scia_model.nodes[1].x, scia_model.nodes[1].y, scia_model.nodes[1].z),
            Point(scia_model.nodes[2].x, scia_model.nodes[2].y, scia_model.nodes[2].z),
            Point(scia_model.nodes[3].x, scia_model.nodes[3].y, scia_model.nodes[3].z),
            Point(scia_model.nodes[0].x, scia_model.nodes[0].y, scia_model.nodes[0].z)
        ]

        floor_thickness = params.step2.floor_thickness
        floor_slab_obj = Extrusion(floor_points, Line(Point(0, 0, 0), Point(0, 0, floor_thickness)))
        slab_material = Material('slab', threejs_roughness=1, threejs_opacity=0.3)
        floor_slab_obj.material = slab_material
        geometry_group.add(floor_slab_obj)
        #
        # roof_points = [
        #     Point(scia_model.nodes[4].x, scia_model.nodes[4].y, scia_model.nodes[4].z),
        #     Point(scia_model.nodes[5].x, scia_model.nodes[5].y, scia_model.nodes[5].z),
        #     Point(scia_model.nodes[6].x, scia_model.nodes[6].y, scia_model.nodes[6].z),
        #     Point(scia_model.nodes[7].x, scia_model.nodes[7].y, scia_model.nodes[7].z),
        #     Point(scia_model.nodes[4].x, scia_model.nodes[4].y, scia_model.nodes[4].z)
        # ]
        #
        # print(roof_points)

        roof_thickness = params.step2.roof_thickness
        roof_slab_obj = Extrusion(floor_points, Line(Point(0, 0, scia_model.nodes[4].z - roof_thickness), Point(0, 0, scia_model.nodes[4].z)))
        roof_slab_obj.material = slab_material
        geometry_group.add(roof_slab_obj)

        return geometry_group
