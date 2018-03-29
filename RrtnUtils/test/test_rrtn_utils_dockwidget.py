# coding=utf-8
"""DockWidget test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from __future__ import absolute_import

__author__ = '-'
__date__ = '2016-12-06'
__copyright__ = 'Copyright 2016, César Arriaga'

import unittest

from qgis.PyQt.QtWidgets import QDockWidget

from rrtn_utils_dockwidget import RrtnUtilsDockWidget

from .utilities import get_qgis_app

QGIS_APP = get_qgis_app()


class RrtnUtilsDockWidgetTest(unittest.TestCase):
    """Test dockwidget works."""

    def setUp(self):
        """Runs before each test."""
        self.dockwidget = RrtnUtilsDockWidget(None)

    def tearDown(self):
        """Runs after each test."""
        self.dockwidget = None

    def test_dockwidget_ok(self):
        """Test we can click OK."""
        pass

if __name__ == "__main__":
    suite = unittest.makeSuite(RrtnUtilsDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

