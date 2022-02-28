import unittest

from app.tunnel.controller import TunnelController


class TestTunnelController(unittest.TestCase):
    @mock_ParamsFromFile(TunnelController)
    def test_calculating_length(self):
        self.assertTrue(True)
