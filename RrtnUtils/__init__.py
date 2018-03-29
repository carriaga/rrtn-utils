# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RrtnUtils
                                 A QGIS plugin
 Utilidades de acceso a los servicios del RRTN (Catastro de Navarra)
                             -------------------
        begin                : 2016-12-06
        copyright            : (C) 2016 by César Arriaga
        email                : -
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the Eclipse Public License - v 1.0              *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RrtnUtils class from file RrtnUtils.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .rrtn_utils import RrtnUtils
    return RrtnUtils(iface)
