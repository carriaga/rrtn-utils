# -*- coding: utf-8 -*-
"""
/***************************************************************************
 RrtnUtils
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
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.core import QgsCoordinateReferenceSystem, QgsMapLayerRegistry, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsRectangle, QgsFeature, QgsVectorFileWriter
from qgis.gui import QgsMessageBar, QgsRubberBand

import urllib

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QColor, QFileDialog, QMessageBox
# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from rrtn_utils_dockwidget import RrtnUtilsDockWidget
import os.path

# CRS for the RRTN
RRTN_CRS = 'EPSG:25830'
# Legend layer name
RRTN_WMS_LAYER_NAME = u"RRTN @ WMS IDENA"
# Nombre capa de trabajo.
WORKING_LAYER_NAME = u"Parcelas actuación"

# Eliminar acentos (Python 2.7)
import unicodedata


class RrtnUtils:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # Get plugin accesible for @DEBUG purposes.
        #iface.rrtnPlugin = self

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'RrtnUtils_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&RRTN Utils')
        # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'RrtnUtils')
        # self.toolbar.setObjectName(u'RrtnUtils')

        # print "** INITIALIZING RrtnUtils"

        self.pluginIsActive = False
        self.dockwidget = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('RrtnUtils', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Añadir al toolbar de plugins.
            self.iface.addToolBarIcon(action)
            # self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/RrtnUtils/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mostrar panel RRTN Utils...'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # print "** CLOSING RrtnUtils"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget.btnInitMap.clicked.disconnect(self.onBtnInitMapClick)
        self.dockwidget.btnBuscar.clicked.disconnect(self.onBtnBuscarClick)
        self.dockwidget.btnInitWorkingLayer.clicked.disconnect(
            self.onBtnInitWorkingLayerClick)
        btnDraw = [x for x in self.iface.mapNavToolToolBar(
        ).actions() if x.objectName() == 'mActionDraw'][0]
        btnDraw.triggered.disconnect(self.onActionDraw)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        # print "** UNLOAD RrtnUtils"

        # Limpiar la selección del mapa.
        self.limpiarSeleccion()

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&RRTN Utils'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        # del self.toolbar

    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING RrtnUtils"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = RrtnUtilsDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # Signal handlers.
            self.dockwidget.btnInitMap.clicked.connect(self.onBtnInitMapClick)
            self.dockwidget.btnBuscar.clicked.connect(self.onBtnBuscarClick)
            self.dockwidget.btnInitWorkingLayer.clicked.connect(
                self.onBtnInitWorkingLayerClick)
            # Capturar la pulsación del botón refrescar.
            btnDraw = [x for x in self.iface.mapNavToolToolBar(
            ).actions() if x.objectName() == 'mActionDraw'][0]
            btnDraw.triggered.connect(self.onActionDraw)

            # Cargar ComboBox de municipios si no está ya cargado.
            if self.dockwidget.cmbMunicipios.count() == 0:
                for feature in self.datosMunicipios():
                    # Añadir nombres de municipios sin acentos y en mayúsculas.
                    # import unicodedata
                    # HorizontalPolicy: Ignored -> evitar que se expanda todo al ancho del texto de municipio más largo.
                    self.dockwidget.cmbMunicipios.addItem(
                        unicodedata.normalize('NFD', feature["MUNICIPIO"]).encode('ascii', 'ignore').upper(), feature["CMUNICIPIO"])

            # Lista de parcelas seleccionadas.
            self.parcelasResaltadas = list()

            # Ruta base del usuario para salvar archivos.
            self.userDir = "~"
            #self.userDir = "c:/tmp"

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def datosMunicipios(self):
        """ Obtener la lista de municipios de Navarra """

        # Esta uri no permite controlar la proyección de campos.
        #uri = "srsname=EPSG:25830 typename=IDENA:CATAST_Pol_Municipio url=http://idena.navarra.es/ogc/wfs version=2.0.0 sql=SELECT CMUNICIPIO,MUNICIPIO FROM CATAST_Pol_Municipio"

        # De esta manera obtenemos únicamente los dos campos necesarios.
        uri = "http://idena.navarra.es/ogc/wfs?typename=IDENA:CATAST_Pol_Municipio&version=1.0.0&request=GetFeature&service=WFS&propertyname=CMUNICIPIO,MUNICIPIO"
        layer = QgsVectorLayer(uri, "data", "WFS")

        return list(layer.getFeatures())

    def inicializarMapa(self):
        # Fijar el SRS necesario para el RRTN.

        canvas = self.iface.mapCanvas()
        crs = QgsCoordinateReferenceSystem(RRTN_CRS)
        canvas.setDestinationCrs(crs)

        # Cargar WMS Catastro de IDENA.
        params = {
            # 14/10/2017: antes era 'IDENA:catastro'.
            'layers': 'catastro',
            'styles': '',
            'format': 'image/png',
            'crs': RRTN_CRS,
            'dpiMode': '7',
            'url': 'http://idena.navarra.es/ogc/wms'
        }

        uri = urllib.unquote(urllib.urlencode(params))

        rlayer = QgsRasterLayer(uri, RRTN_WMS_LAYER_NAME, 'wms')
        if not rlayer.isValid():

            self.iface.messageBar().pushMessage(
                u"Ha ocurrido un error al cargar la capa WMS de Catastro de IDENA.", QgsMessageBar.CRITICAL, 10)
        else:
            self.iface.messageBar().pushMessage(
                u"Entorno para el acceso al RRTN inicializado.", QgsMessageBar.SUCCESS, 5)
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)

    def onBtnInitMapClick(self):
        """Map initialization signal handler"""
        self.inicializarMapa()

    def limpiarSeleccion(self):
        """
        Eliminar los elementos para la selección de parcelas (resaltado).
        """
        if hasattr(self, "parcelasResaltadas"):
            canvas = self.iface.mapCanvas()

            for r in self.parcelasResaltadas:
                canvas.scene().removeItem(r)

            del self.parcelasResaltadas[:]

    def onActionDraw(self):
        """ Captura del botón Refresh para borrar la lista de seleccionadas """
        self.limpiarSeleccion()

    def onBtnInitWorkingLayerClick(self):
        """Crear una nueva capa de trabajo para la edición de parcelas"""

        try:
            fileName = QFileDialog.getSaveFileName(self.dockwidget, u"Seleccionar ubicación archivo SHP de trabajo", os.path.expanduser(
                self.userDir + "/parcelas_actuacion.shp"), u"Shapefiles (*.shp)")

            if fileName == "":
                return

            # Almacenar el directorio seleccionado para la próxima vez.
            self.userDir = os.path.dirname(fileName)

            # Comprobar si está intentando sustituir a un archivo ya cargado.
            layersToRemove = list()
            for layer in QgsMapLayerRegistry.instance().mapLayers().values():
                if fileName == layer.dataProvider().dataSourceUri().split('|')[0]:
                    layersToRemove.append(layer)

            if len(layersToRemove) > 0:
                reply = QMessageBox.question(self.dockwidget, u"Aviso", 
                 u"El fichero seleccionado se encuentra entre las capas cargadas y éstas serán sustituidas si decide continuar. ¿Desea continuar?", QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # Descargar las capas cargadas.
                    for layer in layersToRemove:
                        QgsMapLayerRegistry.instance().removeMapLayer(layer)
                else:
                    # Salir sin cargar.
                    return

            templateLayer = QgsVectorLayer(
                'Polygon?crs=' + RRTN_CRS + '&field=localId:string(9)&field=namespace:string(20)&field=area:double&index=yes', WORKING_LAYER_NAME, 'memory')
            provider = templateLayer.dataProvider()

            # Crear una archivo shape con la estructura de la plantilla. Nota: machaca el fichero existente.
            error = QgsVectorFileWriter.writeAsVectorFormat(
                templateLayer, fileName, provider.encoding(), provider.crs(), "ESRI Shapefile")

            if error != QgsVectorFileWriter.NoError:
                raise Exception(u"Error al crear el fichero {0}.".format(fileName))

            # Cargar el nuevo archivo en el mapa.
            vlayer = QgsVectorLayer(fileName, WORKING_LAYER_NAME, "ogr")

            if not vlayer.isValid():
                raise Exception(u"Error al crear el fichero {0}.".format(fileName))

            # Conservar como nueca capa de trabajo y añadir a la ToC.
            self.dockwidget.leWorkingLayer.setText(u"{0} ({1})".format(WORKING_LAYER_NAME, fileName))
            self.workingLayer = vlayer
            self.workingLayer.startEditing()
            QgsMapLayerRegistry.instance().addMapLayer(self.workingLayer)

        except Exception as error:
            self.iface.messageBar().pushMessage(error.message, QgsMessageBar.CRITICAL, 10)

    def onBtnBuscarClick(self):
        """Localizar una parcela catastral en el mapa """

        try:
            canvas = self.iface.mapCanvas()

            # Comprobar que se ha abierto un mapa.
            if canvas.isHidden():
                raise Exception(
                    u"NO HAY NINGUN MAPA INICIALIZADO. Crea un nuevo mapa e inténtalo de nuevo.")

            # Obtener el código de municipio.
            muniText = self.dockwidget.cmbMunicipios.currentText()

            # Si se ha introducido un número tratamos de usarlo como código de municipio.
            if muniText.isdigit():
                codMunicipio = int(muniText)
            else:
                idx = self.dockwidget.cmbMunicipios.currentIndex()
                idxText = self.dockwidget.cmbMunicipios.itemText(idx)

                # Comprobar si el texto coincide con el valor de la selección actual del combo.
                if muniText == idxText:
                    codMunicipio = self.dockwidget.cmbMunicipios.itemData(idx)
                else:
                    return

            # Obtener la referencia catastral de la UI.
            poligono = int(self.dockwidget.lePoligono.text())
            parcela = int(self.dockwidget.leParcela.text())

            (selectedLayer, parcelaFeature) = self.cargarParcela(
                codMunicipio, poligono, parcela, muniText)
            parcelaGeom = parcelaFeature.geometry()

            # Crear un resaltado para la parcela seleccionada.
            # import QgsRubberBand
            # Eliminar resaltados anteriores.
            self.limpiarSeleccion()
            r = QgsRubberBand(canvas, True)  # True = a polygon
            # Se le indica la capa de la que tomar el SRS.
            r.setToGeometry(parcelaGeom, selectedLayer)
            r.setColor(QColor(255, 0, 0))
            # 63 -> Alpha usado por QgsHighlight.
            r.setFillColor(QColor(255, 0, 0, 63))
            r.setWidth(2)
            self.parcelasResaltadas.append(r)

            # Copiar la extensión de la parcela para poderla ampliar.
            parcelaExtent = QgsRectangle(parcelaGeom.boundingBox())
            parcelaExtent.grow(2)

            canvas.setExtent(parcelaExtent)
            canvas.refresh()

        except Exception as error:
            self.iface.messageBar().pushMessage(
                error.message, QgsMessageBar.WARNING, 6)

    def cargarParcela(self, codMunicipio, poligono, parcela, muniText):
        # Leyenda de la capa.
        leyenda = u"Parcela: {0}, {1}, {2}".format(
            codMunicipio, poligono, parcela)

        # URL general
        uri_template = "srsname=" + RRTN_CRS + \
            " typename=IDENA:{0} url=http://idena.navarra.es/ogc/wfs version=2.0.0"
        uri_template += " filter='CMUNICIPIO={0} AND POLIGONO={1} AND PARCELA={2}'".format(
            codMunicipio, poligono, parcela)

        # Búsqueda en parcelas urbanas
        uri = uri_template.format("CATAST_Pol_ParcelaUrba")
        vlayer = QgsVectorLayer(uri, leyenda, "WFS")
        # En vez de llamar a featureCount tratamos de obtener la feature. Evitamos un acceso WFS.
        features = list(vlayer.getFeatures())

        if len(features) != 1:
            # Búsqueda en rústicas (201, 6, 1838).
            uri = uri_template.format("CATAST_Pol_ParcelaRusti")
            vlayer = QgsVectorLayer(uri, leyenda, "WFS")
            features = list(vlayer.getFeatures())

            if len(features) != 1:
                # Búsqueda en mixtas (201, 6, 1089).
                uri = uri_template.format("CATAST_Pol_ParcelaMixta")
                vlayer = QgsVectorLayer(uri, leyenda, "WFS")
                features = list(vlayer.getFeatures())

                if len(features) != 1:
                    raise Exception(u"PARCELA NO ENCONTRADA ({0}, {1}, {2})".format(
                        muniText, poligono, parcela))

        return (vlayer, features[0])
