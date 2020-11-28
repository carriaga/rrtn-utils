# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the Eclipse Public License - v 1.0

"""

__author__ = '-'
__date__ = '2016-12-06'
__copyright__ = 'Copyright 2016, César Arriaga'

import unittest

from qgis.PyQt.QtGui import QIcon



class RrtnUtilsDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Test we can click OK."""
        path = ':/plugins/RrtnUtils/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(RrtnUtilsResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



