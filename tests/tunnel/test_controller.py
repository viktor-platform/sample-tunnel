import json
import unittest
from pathlib import Path

from munch import munchify
from viktor.geometry import GeoPoint
from viktor.geometry import GeoPolyline
from viktor.views import MapResult

from app import TunnelController


class TestTunnelController(unittest.TestCase):
    controller_type = TunnelController

    def setUp(self) -> None:
        params_path = Path(__file__).parent.parent / 'fixtures' / 'tunnel_example_1.json'
        with open(params_path, 'r') as params_file:
            self.params = munchify(json.load(params_file))

        line = GeoPolyline(
            GeoPoint(lat=5.210e+01, lon=4.626e+00),
            GeoPoint(lat=5.210e+01, lon=4.633e+00),
            GeoPoint(lat=5.210e+01, lon=4.641e+00),
            GeoPoint(lat=5.210e+01, lon=4.642e+00))
        self.params.step1.geo_polyline = line

        self.controller = TunnelController(params=self.params)

    def test_visualizing_tunnel(self):
        map_result = self.controller.visualize_tunnel(self.controller, params=self.params)
        self.assertIsInstance(map_result, MapResult)

    def test_size_of_geometry_group(self):
        geometry_group = self.controller.create_visualization_geometries(self.params)
        self.assertEqual(3+self.params.step1.segments, len(geometry_group.children))

    def test_calculating_length(self):
        length = self.controller.get_segment_length(self.params)
        self.assertAlmostEqual(550.0, length, delta=5)
