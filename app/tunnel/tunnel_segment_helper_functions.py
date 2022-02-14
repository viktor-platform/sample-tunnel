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
from typing import List
import numpy as np
from numpy import ndarray

from viktor.geometry import GeoPolyline


def create_segments_from_geo_polyline(geo_polyline: GeoPolyline, number_of_segments: int) -> List:
    points_table_rd = __create_rd_table_from_geo_polyline(geo_polyline)
    polyline_distances = __get_polyline_distances(points_table_rd)
    segments = __create_segments(points_table_rd, polyline_distances, number_of_segments)
    return segments


def __create_rd_table_from_geo_polyline(geo_polyline) -> ndarray:
    table = []
    for geo_point in geo_polyline.points:
        table.append(geo_point.rd)
    return np.array(table)


def __get_polyline_distances(points_table_rd):
    distance = []
    for i, point in enumerate(points_table_rd[:-1]):
        distance.append(np.linalg.norm(point - points_table_rd[i + 1]))
    return np.array(distance)


def __create_segments(points_table_rd, polyline_distances, number_of_segments):
    segment_distance = np.sum(polyline_distances) / number_of_segments
    current_segment_distance = segment_distance
    segment_index = 0

    segments = __get_first_segment_points(points_table_rd)
    for i, dis in enumerate(polyline_distances):
        current_distance = 0
        begin = points_table_rd[i]
        end = points_table_rd[i+1]
        while dis - current_distance >= current_segment_distance - 0.1:
            next_point_vector = (current_distance + current_segment_distance) / dis

            __add_point_to_segment(begin, end, next_point_vector, segment_index, segments)

            segment_index += 1
            current_distance += current_segment_distance
            current_segment_distance = segment_distance

        # add points to segment if segment is located on a bend
        if i < len(polyline_distances) - 1:
            vector_1 = (end - begin) / np.linalg.norm(begin - end)
            vector_2 = (points_table_rd[i+2] - end) / np.linalg.norm(end - points_table_rd[i+2])
            unity_vector_x, unity_vector_y = (vector_1 + vector_2) / 2
            perpendicular_vector = (unity_vector_y * 47, -unity_vector_x * 47)
            segments[segment_index].insert(1, end - perpendicular_vector)
            segments[segment_index].insert(1, end + perpendicular_vector)

        current_segment_distance = segment_distance - (dis - current_distance)

    segments.pop()
    return segments


def __add_point_to_segment(begin, end, next_point_vector, segment_index, segments):
    point_on_polyline = begin + ((end - begin) * next_point_vector)
    unity_vector_x, unity_vector_y = (end - begin) / np.linalg.norm(begin - end)
    perpendicular_vector = (unity_vector_y * 40, -unity_vector_x * 40)

    insert_index = 1 if len(segments[segment_index]) == 2 else 2
    segments[segment_index].insert(insert_index, point_on_polyline - perpendicular_vector)
    segments[segment_index].insert(insert_index, point_on_polyline + perpendicular_vector)
    segments.append([point_on_polyline + perpendicular_vector, point_on_polyline - perpendicular_vector])


def __get_first_segment_points(points_table_rd):
    begin = points_table_rd[0]
    end = points_table_rd[1]
    unity_vector_x, unity_vector_y = (end - begin) / np.linalg.norm(begin - end)
    perpendicular_vector = (unity_vector_y * 40, -unity_vector_x * 40)
    segments = [[begin + perpendicular_vector, begin - perpendicular_vector]]
    return segments
