# pylint:disable=line-too-long                                 # Allows for longer line length inside a Parametrization
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
from viktor.parametrization import DownloadButton
from viktor.parametrization import GeoPolylineField
from viktor.parametrization import LineBreak
from viktor.parametrization import NumberField
from viktor.parametrization import Parametrization
from viktor.parametrization import Step


class TunnelParametrization(Parametrization):
    """Defines the input fields in left-side of the web UI in the Sample entity (Editor)."""
    step1 = Step('Select tunnel location', views='visualize_tunnel')
    step1.geo_polyline = GeoPolylineField('Location of tunnel')
    step1.segments = NumberField('Number of segments', default=5)

    step2 = Step('Define cross section', views='visualize_tunnel_segment')
    step2.width = NumberField('Total width', default=40, suffix='m')
    step2.height = NumberField('Total height', default=12, suffix='m')
    step2.number_of_sections = NumberField('Number of sections', default=2)
    step2.floor_thickness = NumberField('Floor thickness', default=1.5, suffix='m')
    step2.roof_thickness = NumberField('Roof thickness', default=2, suffix='m')
    step2.wall_thickness = NumberField('Wall thickness', default=1.2, suffix='m')

    step3 = Step('Create SCIA model', views='visualize_tunnel_structure')
    step3.roof_load = NumberField('Roof load', default=1, suffix='kN/m2')
    step3.soil_stiffness = NumberField('Soil stiffness', default=400, suffix='MN/m')
    step3.ln_break0 = LineBreak()
    step3.input_xml_btn = DownloadButton('viktor.xml', method='download_scia_input_xml')
    step3.input_def_btn = DownloadButton('viktor.xml.def', method='download_scia_input_def')
    step3.input_esa_btn = DownloadButton('model.esa', method='download_scia_input_esa')

    step4 = Step('Analyse engineering report', views='execute_scia_analysis')
