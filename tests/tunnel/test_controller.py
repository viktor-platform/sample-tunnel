import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from munch import munchify
from viktor.geometry import GeoPoint
from viktor.geometry import GeoPolyline
from viktor.views import MapResult
from viktor.views import PDFResult

from app.tunnel.controller import TunnelController


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

        self.controller = TunnelController()

    @staticmethod
    def generate_xml_input_mock():
        """ Mocks returning the xml files.
        This is necessary since viktor.external.scia.Model.generate_xml_input uses an api call."""
        xml_path = Path(__file__).parent.parent / 'fixtures' / 'viktor.xml'
        def_path = Path(__file__).parent.parent / 'fixtures' / 'viktor.xml.def'
        return open(xml_path, 'r'), open(def_path, 'r')

    def scia_analysis_execute_mock(self, timeout):
        """ We do not want to execute the app.tunnel.controller.SciaAnalysis.execute because that uses an api call."""
        pass

    @staticmethod
    def scia_analysis_get_engineering_report_mock(as_file):
        """ Mock the engineering report by just returning an empty pdf file. """
        return open('report.pdf', 'w')

    def test_visualizing_tunnel(self):
        """ Tests step 1 of the TunnelController"""
        map_result = self.controller.visualize_tunnel(self.controller, params=self.params)
        self.assertIsInstance(map_result, MapResult)

    def test_size_of_geometry_group(self):
        """ Tests creating the geometry visualisation.
        It does this asserting the number of objects is equal to 3 + the number op sections.
        (floor, roof, left side and for every section another wall) """
        geometry_group = self.controller.create_visualization_geometries(self.params)
        self.assertEqual(3 + self.params.step1.segments, len(geometry_group.children))

    def test_calculating_length(self):
        """ Tests if for these mocked params the length is around 550 meter."""
        length = self.controller.get_segment_length(self.params)
        self.assertAlmostEqual(550.0, length, delta=5)

    @patch('viktor.external.scia.Model.generate_xml_input', generate_xml_input_mock)
    @patch('app.tunnel.controller.SciaAnalysis.execute', scia_analysis_execute_mock)
    @patch('app.tunnel.controller.SciaAnalysis.get_engineering_report', scia_analysis_get_engineering_report_mock)
    def test_a(self):
        """ Test TunnelController.execute_scia_analysis. It mocks some methods since they are using API calls."""
        pdf_result = self.controller.execute_scia_analysis(self.controller, params=self.params)
        self.assertIsInstance(pdf_result, PDFResult)
