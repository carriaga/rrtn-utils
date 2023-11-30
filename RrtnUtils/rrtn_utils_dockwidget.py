# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RrtnUtilsDockWidget
                                 A QGIS plugin
 Utilidades de acceso a los servicios del RRTN (Catastro de Navarra)
                             -------------------
        begin                : 2016-12-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by César Arriaga
        email                : -
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the Eclipse Public License - v 1.0              *
 *                                                                         *
 ***************************************************************************/
"""

import os
import unicodedata

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, QStringListModel, Qt
from qgis.PyQt.QtWidgets import QDockWidget, QCompleter

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'rrtn_utils_dockwidget_base.ui'))


class RrtnUtilsDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(RrtnUtilsDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

class RrtnUtilsCompleter(QCompleter):
    
    def splitPath(self, path):
        return [strip_accents(path).lower()]
    
    def pathFromIndex(self, index):
        return index.data()
    
class RrtnUtilsStringListModel(QStringListModel):

    def __init__(self, *args, **kwargs):
        super(RrtnUtilsStringListModel, self).__init__(*args, **kwargs)
        self.setRolSinTildes(Qt.UserRole+10)

    def data(self, index, role):
        if role == self.rolSinTildes():
            valor = super(RrtnUtilsStringListModel, self).data(index, Qt.DisplayRole)
            return strip_accents(valor).lower()
        else:
            return super(RrtnUtilsStringListModel, self).data(index, role)

    def setRolSinTildes(self, rol):
        self.mrolSinTildes = rol

    def rolSinTildes(self):
        return self.mrolSinTildes
