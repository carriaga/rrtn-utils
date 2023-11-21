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
 *   it under the terms of the Eclipse Public License - v 1.0              *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
from qgis.core import QgsCoordinateReferenceSystem, QgsProject, QgsMapLayer, QgsRasterLayer, QgsVectorLayer, QgsRectangle, QgsFeature, QgsVectorFileWriter, Qgis, QgsWkbTypes
from qgis.gui import QgsRubberBand

import urllib.request, urllib.parse, urllib.error
import time

from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant, QRegExp, QUrl
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox, QInputDialog, QDialog, QPushButton
from qgis.PyQt.QtGui import QIcon, QColor, QRegExpValidator

from qgis.PyQt.QtWebKitWidgets import QWebView

# Initialize Qt resources from file resources.py
from . import resources

# Import the code for the DockWidget
from .rrtn_utils_dockwidget import RrtnUtilsDockWidget, RrtnUtilsCompleter, RrtnUtilsStringListModel
from .rrtn_gml import RrtnGmlWriter
import os.path

# @DEBUG
# import traceback
# traceback.print_exc() -> print stacktrace.


# Definición de campos de la capa de trabajo.
from .rrtn_gml import LOCALID_FIELDNAME
from .rrtn_gml import LOCALID_FIELDLENGTH
from .rrtn_gml import NAMESPACE_FIELDNAME
from .rrtn_gml import NAMESPACE_FIELDLENGTH
from .rrtn_gml import AREA_FIELDNAME

# CRS for the RRTN
RRTN_CRS = 'EPSG:25830'
# Legend layer name
RRTN_WMS_LAYER_NAME = u"RRTN @ WMS IDENA"
# Nombre capa de trabajo.
WORKING_LAYER_NAME = u"Parcelas actuación"

# Valores de namespaces para features de la capa de trabajo.
CP_RRTN_NAMESPACE = 'ES.RRTN.CP'
CP_USER_NAMESPACE = 'ES.LOCAL.CP'

# Nombres de campos en IDENA
IDENA_REFCAT_FIELD = 'REFCAT'
IDENA_CMUNICIPIO_FIELD = 'CMUNICIPIO'
IDENA_MUNICIPIO_FIELD = 'MUNICIPIO'
IDENA_POLIGONO_FIELD = 'POLIGONO'
IDENA_PARCELA_FIELD = 'PARCELA'

# USER SETTING KEYS
SETTING_CRS_KEY = 'rrtnUtils/crs'
SETTING_WMS_KEY = 'rrtnUtils/wms'

# Eliminar acentos (Python 2.7)
import unicodedata

class RrtnUtils(object):
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
        # iface.rrtnPlugin = self

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

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        # print "** CLOSING RrtnUtils"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        self.dockwidget.btnLocalizarParcela.clicked.disconnect(
            self.onBtnLocalizarParcelaClick)
        self.dockwidget.btnInfoParcela.clicked.disconnect(
            self.onBtnInfoParcelaClick)
        self.dockwidget.btnNewWorkingLayer.clicked.disconnect(
            self.onBtnNewWorkingLayerClick)
        self.dockwidget.btnSelectWorkingLayer.clicked.disconnect(
            self.onBtnSelectWorkingLayerClick)
        self.dockwidget.btnAddParcelaSel.clicked.disconnect(
            self.onBtnAddParcelaSelClick)
        self.dockwidget.btnExportGml.clicked.disconnect(
            self.onBtnExportGmlClick)
        self.dockwidget.chkCrs.stateChanged.disconnect(
            self.onChkCrsStateChange)
        self.dockwidget.chkWms.stateChanged.disconnect(
            self.onChkWmsStateChange)

        btnDraw = [x for x in self.iface.mapNavToolToolBar(
        ).actions() if x.objectName() == 'mActionDraw'][0]
        btnDraw.triggered.disconnect(self.onActionDraw)

        # Capturar la descarga de capas.
        QgsProject.instance().layerWillBeRemoved.disconnect(
            self.onLayerWillBeRemoved)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        # print("** UNLOAD RrtnUtils")

        # hasattr: previene error del Plugin Reloader que llama a unload.
        # Los atributos podrían no estar creados.
        if hasattr(self, "parcelaLocalizada"):
            # Limpiar la selección del mapa y la información asociada.
            self.limpiarSeleccion()

        # Get plugin accesible for @DEBUG purposes.
        #if hasattr(self.iface, "rrtnPlugin"):
        #   self.iface.rrtnPlugin = None

        # Limpirar atributo para almacenar la capa de trabajo.
        if hasattr(self, "workingLayer"):
            self.workingLayer = None

        # Navegador web integrado.
        if hasattr(self, "browser"):
            self.browser = None

        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&RRTN Utils'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        # del self.toolbar

    # --------------------------------------------------------------------------

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

            # RECUPERAR SETTINGS USUARIO
            crs = QSettings().value(SETTING_CRS_KEY, "true") == "true" # True si no esta definida o si vale "true"
            wms = QSettings().value(SETTING_WMS_KEY, "true") == "true" # True si no esta definida o si vale "true"

            self.dockwidget.chkCrs.setChecked(crs)
            self.dockwidget.chkWms.setChecked(wms)

            # Asignar EPSG:25830 si no está asignado.
            if crs:
                self.fijarSrsRrtn()

            # Cargar WMS RRTN @ IDENA si no está cargado.
            if wms:
                self.cargarWmsCatastroIdena()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # Signal handlers.
            self.dockwidget.btnLocalizarParcela.clicked.connect(
                self.onBtnLocalizarParcelaClick)
            self.dockwidget.btnInfoParcela.clicked.connect(
                self.onBtnInfoParcelaClick)
            self.dockwidget.btnNewWorkingLayer.clicked.connect(
                self.onBtnNewWorkingLayerClick)
            self.dockwidget.btnSelectWorkingLayer.clicked.connect(
                self.onBtnSelectWorkingLayerClick)
            self.dockwidget.btnAddParcelaSel.clicked.connect(
                self.onBtnAddParcelaSelClick)
            self.dockwidget.btnExportGml.clicked.connect(
                self.onBtnExportGmlClick)

            self.dockwidget.chkCrs.stateChanged.connect(
                self.onChkCrsStateChange)
            self.dockwidget.chkWms.stateChanged.connect(
                self.onChkWmsStateChange)

            # Capturar la pulsación del botón refrescar.
            btnDraw = [x for x in self.iface.mapNavToolToolBar(
            ).actions() if x.objectName() == 'mActionDraw'][0]
            btnDraw.triggered.connect(self.onActionDraw)
            # Capturar la descarga de capas.
            QgsProject.instance().layerWillBeRemoved.connect(self.onLayerWillBeRemoved)

            # Cargar ComboBox de municipios si no está ya cargado.
            if self.dockwidget.cmbMunicipios.count() == 0:
                # Lista de municipios a mostrar al usuario
                municipiosMostrar = self.datosMunicipios()
                # Lista de municipios por la que ordenar municipiosMostrar, tiene una tupla con (nombre, número)
                # Si es una facería: nombre = 'FACERIA' y número es un entero con el número de la facería
                # Si no lo es: nombre = nombreMunicipio y número = -1
                municipiosOrdenar = []
                for feature in municipiosMostrar:
                    # Transformar nombres de municipios sin acentos y en mayúsculas
                    nombreMunicipio = (
                        unicodedata.normalize("NFD", feature[IDENA_MUNICIPIO_FIELD])
                        .encode("ascii", "ignore")
                        .upper()
                        .decode("utf-8")
                    )
                    # Si es una facería, extraer su numero
                    if nombreMunicipio[0].isdigit() or nombreMunicipio.startswith("FACERIA"):
                        regexp = QRegExp("[0-9]+")
                        regexp.indexIn(nombreMunicipio)
                        numeroFaceria = int(regexp.cap(0))
                        municipiosOrdenar.append(("FACERIA", numeroFaceria))
                    else:
                        municipiosOrdenar.append((nombreMunicipio, -1))

                municipiosMostrar = zip(municipiosOrdenar, municipiosMostrar)
                # Ordenar alfabeticamente y si es faceria ordenar por su numero
                municipiosMostrar = [x for _, x in sorted(municipiosMostrar, key=lambda e: (e[0][0], e[0][1]))]
                municipiosConTilde = []
                for feature in municipiosMostrar:
                    # HorizontalPolicy: Ignored -> evitar que se expanda todo al ancho del texto de municipio más largo.
                    # nombreMunicipio = unicodedata.normalize('NFD', feature[IDENA_MUNICIPIO_FIELD]).encode('ascii', 'ignore').upper().decode("utf-8")
                    self.dockwidget.cmbMunicipios.addItem(
                        feature[IDENA_MUNICIPIO_FIELD], feature[IDENA_CMUNICIPIO_FIELD]
                    )
                    municipiosConTilde.append(feature[IDENA_MUNICIPIO_FIELD])

                # El autocompletado del ComboBox se realiza sin tener en cuenta las tildes ni las mayúsculas.
                completerSinTildes = RrtnUtilsCompleter()
                modelo = RrtnUtilsStringListModel()
                completerSinTildes.setModel(modelo)
                completerSinTildes.setCompletionRole(modelo.rolSinTildes())
                modelo.setStringList(municipiosConTilde)  # Lista con los municipios con tilde
                self.dockwidget.cmbMunicipios.setCompleter(completerSinTildes)

            # Poner validadores a los campos de códigos localizadores.
            # Enteros de 1 a 99
            self.dockwidget.lePoligono.setValidator(
                QRegExpValidator(QRegExp('[1-9]\\d{0,1}')))
            # Enteros de 1 a 9999
            self.dockwidget.leParcela.setValidator(
                QRegExpValidator(QRegExp('[1-9]\\d{0,3}')))

            #############################################################################
            #                                                                           #
            #                      Inicialización de propiedades.                       #
            #                                                                           #
            #############################################################################

            # Inicializar información parcela seleccionada.
            self.parcelaLocalizada = None

            # Ruta base del usuario para salvar archivos.
            self.userDir = "~"
            #self.userDir = "c:/tmp"

            # Iniciar atributo para almacenar la capa de trabajo.
            self.workingLayer = None

            # Navegador web integrado.
            self.browser = None
            #
            #############################################################################

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def onChkCrsStateChange(self, state):
        """ Evento de cambio de estado del checkBox CRS  """

        checked = state == Qt.Checked
        if checked:
            self.fijarSrsRrtn()

        # Persistir el estado del check.
        QSettings().setValue(SETTING_CRS_KEY, checked)

    def onChkWmsStateChange(self, state):
        """ Evento de cambio de estado del checkBox WMS  """

        checked = state == Qt.Checked
        if checked:
            self.cargarWmsCatastroIdena()

        # Persistir el estado del check.
        QSettings().setValue(SETTING_WMS_KEY, checked)

    def onLayerWillBeRemoved(self, layerId):
        """ Evento previo a la eliminación de una capa de la leyenda  """

        if self.workingLayer and self.workingLayer.id() == layerId:
            self.workingLayer = None
            self.dockwidget.leWorkingLayer.clear()
            self.dockwidget.leWorkingLayer.setToolTip(u"")
            # Actualizar estado de los controles de la Ui tras el cambio de estado.
            self.actualizarUi()

    def datosMunicipios(self):
        """ Obtener la lista de municipios de Navarra """

        # Esta uri no permite controlar la proyección de campos (no lo traslada al GET).
        # Tiene el problema añadido del TYPENAMES (que el servidor de IDENA no procesa correctamente).
        #uri = "srsname=EPSG:25830 typename=IDENA:CATAST_Pol_Municipio url=http://idena.navarra.es/ogc/wfs version=2.0.0 sql=SELECT CMUNICIPIO,MUNICIPIO FROM CATAST_Pol_Municipio"

        # De esta manera obtenemos únicamente los dos campos necesarios. Tampoco funciona con 1.1.0. Ver llamadas con Fiddler.
        uri = "http://idena.navarra.es/ogc/wfs?typename=IDENA:CATAST_Pol_Municipio&version=1.0.0&request=GetFeature&service=WFS&propertyname={0},{1}".format(
            IDENA_CMUNICIPIO_FIELD, IDENA_MUNICIPIO_FIELD)
        layer = QgsVectorLayer(uri, "data", "WFS")

        return list(layer.getFeatures())

    def fijarSrsRrtn(self):
        """ Fijar el SRS necesario para el RRTN """

        canvas = self.iface.mapCanvas()
        crs = QgsCoordinateReferenceSystem(RRTN_CRS)
        canvas.setDestinationCrs(crs)

    def cargarWmsCatastroIdena(self):
        """ Cargar WMS Catastro de IDENA """

        params = {
            # 14/10/2017: antes era 'IDENA:catastro'.
            'layers': 'catastro',
            'styles': '',
            'format': 'image/png',
            'crs': RRTN_CRS,
            'dpiMode': '7',
            'url': 'http://idena.navarra.es/ogc/wms'
        }

        # Comprobar que no esté ya cargada.
        for layer in list(QgsProject.instance().mapLayers().values()):
            if layer.type() == QgsMapLayer.RasterLayer and params['url'] in layer.dataProvider().dataSourceUri():
                return

        uri = urllib.parse.unquote(urllib.parse.urlencode(params))

        rlayer = QgsRasterLayer(uri, RRTN_WMS_LAYER_NAME, 'wms')
        if not rlayer.isValid():

            self.iface.messageBar().pushMessage(
                u"Ha ocurrido un error al cargar la capa WMS de Catastro de IDENA.", Qgis.Critical, 10)
        else:
            self.iface.messageBar().pushMessage(
                u"Entorno para el acceso al RRTN inicializado.", Qgis.Success, 5)
            QgsProject.instance().addMapLayer(rlayer)

    def limpiarSeleccion(self):
        """
        Eliminar los elementos para la selección de parcelas (resaltado).
        """

        if self.parcelaLocalizada:
            canvas = self.iface.mapCanvas()
            resaltado = self.parcelaLocalizada[1]
            canvas.scene().removeItem(resaltado)
            self.dockwidget.leParcelaSel.clear()
            self.parcelaLocalizada = None
            # Actualizar estado de los controles de la Ui tras el cambio de estado.
            self.actualizarUi()

    def onActionDraw(self):
        """ Captura del botón Refresh para borrar la lista de seleccionadas """
        self.limpiarSeleccion()

    def onBtnSelectWorkingLayerClick(self):
        """Seleccionar una de las capas entre las cargadas"""

        # Obtener las capas compatibles de la ToC que no sean igual a la de trabajo.
        compatibleLayers = list()
        for layer in list(QgsProject.instance().mapLayers().values()):
            # QgsWkbTypes.Polygon: sólo geometrías poligonales simples.
            if layer != self.workingLayer and layer.type() == QgsMapLayer.VectorLayer and layer.geometryType() == QgsWkbTypes.Polygon:
                # Ver si es compatible.
                fields = list(layer.fields())
                if fields[0].name() == LOCALID_FIELDNAME and fields[0].type() == QVariant.String and fields[0].length() == LOCALID_FIELDLENGTH and fields[1].name() == NAMESPACE_FIELDNAME and fields[1].type() == QVariant.String and fields[1].length() == NAMESPACE_FIELDLENGTH and fields[2].name() == AREA_FIELDNAME and fields[2].type() == QVariant.Double:
                    compatibleLayers.append(layer)

        if not compatibleLayers:
            self.iface. Bar().pushMessage(
                u"No hay cargada ninguna capa compatible para seleccionar.", Qgis.Warning, 6)
        else:
            layerNames = [u"{0} ({1})".format(layer.name(), layer.dataProvider(
            ).dataSourceUri().split('|')[0]) for layer in compatibleLayers]
            (item, ok) = QInputDialog.getItem(self.dockwidget, u"Selección de capa de trabajo",
                                              "Lista de capas compatibles:", layerNames, 0, False)
            if ok:
                index = layerNames.index(item)
                self.setWorkingLayer(compatibleLayers[index])

    def onBtnNewWorkingLayerClick(self):
        """ Crear una nueva capa de trabajo para la edición de parcelas """

        try:
            fileName = QFileDialog.getSaveFileName(self.dockwidget, u"Seleccionar ubicación archivo SHP de trabajo", os.path.expanduser(
                self.userDir + "/parcelas_actuacion.shp"), u"Shapefiles (*.shp)")[0]

            if fileName == "":
                return

            # Almacenar el directorio seleccionado para la próxima vez.
            self.userDir = os.path.dirname(fileName)

            # Comprobar si está intentando sustituir a un archivo ya cargado.
            layersToRemove = list()
            for layer in list(QgsProject.instance().mapLayers().values()):
                if fileName == layer.dataProvider().dataSourceUri().split('|')[0]:
                    layersToRemove.append(layer)

            if len(layersToRemove) > 0:
                reply = QMessageBox.question(self.dockwidget, u"Aviso",
                                             u"El fichero seleccionado se encuentra entre las capas cargadas y éstas será sustituido si decide continuar. ¿Desea continuar?", QMessageBox.Yes, QMessageBox.No)

                if reply == QMessageBox.Yes:
                    # Descargar las capas cargadas.
                    for layer in layersToRemove:
                        QgsProject.instance().removeMapLayer(layer)
                else:
                    # Salir sin cargar.
                    return

            templateLayer = QgsVectorLayer(
                'Polygon?crs=' + RRTN_CRS + '&field={0}:string({1})&field={2}:string({3})&field={4}:double&index=yes'.format(
                    LOCALID_FIELDNAME, LOCALID_FIELDLENGTH, NAMESPACE_FIELDNAME, NAMESPACE_FIELDLENGTH, AREA_FIELDNAME
                ), WORKING_LAYER_NAME, 'memory')
            provider = templateLayer.dataProvider()

            # Crear una archivo shape con la estructura de la plantilla. Nota: machaca el fichero existente.
            error = QgsVectorFileWriter.writeAsVectorFormat(
                templateLayer, fileName, provider.encoding(), provider.crs(), "ESRI Shapefile")[0]

            if error != QgsVectorFileWriter.NoError:
                raise Exception(
                    u"Error al crear el fichero {0}.".format(fileName))

            # Cargar el nuevo archivo en el mapa.
            vlayer = QgsVectorLayer(fileName, WORKING_LAYER_NAME, "ogr")

            if not vlayer.isValid():
                raise Exception(
                    u"Error al crear el fichero {0}.".format(fileName))

            # Conservar como nueva capa de trabajo y añadir a la ToC.
            self.setWorkingLayer(vlayer)
            QgsProject.instance().addMapLayer(self.workingLayer)

        except Exception as error:
            self.iface.messageBar().pushMessage(str(error), Qgis.Critical, 10)

    def onBtnAddParcelaSelClick(self):
        """ Añadir parcela seleccionada a la capa de trabajo """

        parcelaFeature = self.parcelaLocalizada[0]

        newFeat = QgsFeature()
        # pendingFields: es un alias.
        newFeat.setFields(self.workingLayer.fields())
        newFeat.setGeometry(parcelaFeature.geometry())
        newFeat[LOCALID_FIELDNAME] = "00{0}".format(parcelaFeature[IDENA_REFCAT_FIELD])[-9:]
        newFeat[NAMESPACE_FIELDNAME] = CP_RRTN_NAMESPACE
        newFeat[AREA_FIELDNAME] = newFeat.geometry().area()

        if not self.workingLayer.isEditable():
            self.workingLayer.startEditing()

        # Agregar feature a la capa de trabajo (el segundo valor de retorno es una lista de las features añadidas).
        addedFeat = self.workingLayer.dataProvider().addFeatures([newFeat])[1][0]
        self.workingLayer.updateExtents()
        self.limpiarSeleccion()
        # print(addedFeat.id()) # Se muestra en la consola de Python de QGIS.
        #print()
        self.workingLayer.selectByIds([addedFeat.id()])

    def onBtnExportGmlClick(self):
        """Exportar la capa de trabajo a GML"""
        gmlOutputPath = self.userDir + "/parcelas_actuacion.gml"
        coordScale = 3
        gmlWriter = RrtnGmlWriter(gmlOutputPath, coordScale)
        features = list(self.workingLayer.getFeatures())
        gmlWriter.writeGml(features)
        self.iface.messageBar().pushMessage(
            "Capa de trabajo exportada a GML correctamente.", Qgis.Success, 5
        )

    def setWorkingLayer(self, vlayer):
        """ Almacena una capa como capa de trabajo y lo refleja en la UI """

        self.workingLayer = vlayer
        fileName = vlayer.dataProvider().dataSourceUri().split('|')[0]
        self.dockwidget.leWorkingLayer.setText(vlayer.name())
        self.dockwidget.leWorkingLayer.setToolTip(fileName)

        # Fijar etiquetado si no lo tiene configurado.
        if not self.workingLayer.customProperty("labeling"):
            self.workingLayer.setCustomProperty("labeling", u"pal")
            self.workingLayer.setCustomProperty("labeling/fieldName", u"namespace + '.' + localid")
            self.workingLayer.setCustomProperty("labeling/isExpression", True)
            self.workingLayer.setCustomProperty("labeling/fontFamily", u"MS Shell Dlg 2")
            self.workingLayer.setCustomProperty("labeling/fontSize", u"8.25")
            self.workingLayer.setCustomProperty("labeling/placement", u"1")
            self.workingLayer.setCustomProperty("labeling/enabled", True)
            if self.workingLayer.featureCount() > 0:
                self.iface.mapCanvas().refresh()

        # Actualizar estado de los controles de la Ui tras el cambio de estado.
        self.actualizarUi()

        if not self.workingLayer.isEditable():
            self.workingLayer.startEditing()

    def obtenerCodigosLocalizadores(self):
        """ Devulve los códigos localizadores introducidos por el usuario """

        # Obtener el código de municipio.
        muniText = self.dockwidget.cmbMunicipios.currentText()

        # Si se ha introducido un número tratamos de usarlo como código de municipio.
        if muniText.isdigit():
            codMun = int(muniText)
        else:
            idx = self.dockwidget.cmbMunicipios.currentIndex()
            idxText = self.dockwidget.cmbMunicipios.itemText(idx)

            # Comprobar si el texto coincide con el valor de la selección actual del combo.
            if muniText == idxText:
                codMun = self.dockwidget.cmbMunicipios.itemData(idx)
            else:
                return

        # Obtener el resto de códigos localizadores
        codPol = self.dockwidget.lePoligono.text()
        codPar = self.dockwidget.leParcela.text()

        if not codPol.isdigit() or not codPar.isdigit():
            return

        codPol = int(codPol)
        codPar = int(codPar)

        return (muniText, codMun, codPol, codPar)

    def onBtnLocalizarParcelaClick(self):
        """ Localizar una parcela catastral en el mapa """

        try:
            canvas = self.iface.mapCanvas()

            # Comprobar que se ha abierto un mapa.
            if canvas.isHidden():
                raise Exception(
                    u"NO HAY NINGUN MAPA INICIALIZADO. Crea un nuevo mapa e inténtalo de nuevo.")

            codigosLocalizadores = self.obtenerCodigosLocalizadores()
            if not codigosLocalizadores:
                return

            (muniText, codMun, codPol, codPar) = codigosLocalizadores

            (selectedLayer, parcelaFeature) = self.cargarParcela(
                codMun, codPol, codPar, muniText)
            parcelaGeom = parcelaFeature.geometry()

            # Crear un resaltado para la parcela seleccionada.
            # import QgsRubberBand
            # Eliminar resaltados anteriores.
            self.limpiarSeleccion()
            r = QgsRubberBand(canvas, Qgis.GeometryType.Polygon)  # True = a polygon
            # Se le indica la capa de la que tomar el SRS.
            r.setToGeometry(parcelaGeom, selectedLayer)
            r.setColor(QColor(255, 0, 0))
            # 63 -> Alpha usado por QgsHighlight.
            r.setFillColor(QColor(255, 0, 0, 63))
            r.setWidth(2)
            # Almacenar la info de resaltado para poder borrar.
            # Almacenar la parcela localizada por si se quiere copiar a la capa de trabajo.
            self.parcelaLocalizada = (parcelaFeature, r)
            # Mostrar la parcela seleccionada y habilitar el botón de copiado.
            self.dockwidget.leParcelaSel.setText(
                "{0} ({1}), {2}, {3}".format(muniText, codMun, codPol, codPar))
            # Actualizar estado de los controles de la Ui tras el cambio de estado.
            self.actualizarUi()

            # Copiar la extensión de la parcela para poderla ampliar.
            parcelaExtent = QgsRectangle(parcelaGeom.boundingBox())
            parcelaExtent.grow(2)

            canvas.setExtent(parcelaExtent)
            canvas.refresh()

        except Exception as error:
            self.iface.messageBar().pushMessage(
                str(error), Qgis.Warning, 6)

    def actualizarUi(self):
        """ Actualiza la UI en función del estado del widget """

        self.dockwidget.btnAddParcelaSel.setEnabled(
            self.parcelaLocalizada != None and self.workingLayer != None)

    def onBtnInfoParcelaClick(self):
        """ Obtener información de una parcela en el RRTN """

        try:
            codigosLocalizadores = self.obtenerCodigosLocalizadores()
            if not codigosLocalizadores:
                return

            (muniText, codMun, codPol, codPar) = codigosLocalizadores

            # Abrir la página de datos de parcela del RRTN.
            if not self.browser:
                self.browser = QDialog(self.dockwidget)
                self.browser.setWindowTitle(u"Datos de la parcela en el RRTN")
                wv = QWebView(self.browser)
                # QPushButton(u"Aceptar", self.browser)
            else:
                wv = self.browser.findChildren(QWebView)[0]

            capa, _ = self.cargarParcela(codMun, codPol, codPar, muniText)
            sourceCapa = capa.source()
            if "Urba" in sourceCapa:
                uri_template = "https://catastro.navarra.es/ref_catastral/unidades.aspx?C={0}&PO={1}&PA={2}&lang=es"
            elif "Rusti" in sourceCapa or "Mixta" in sourceCapa:
                uri_template = "https://catastro.navarra.es/ref_catastral/subparcelas.aspx?C={0}&PO={1}&PA={2}&lang=es"
            uri = uri_template.format(codMun, codPol, codPar)

            # Cargar la página.
            wv.load(QUrl(uri))

            # Mostrar el QDialog
            if self.browser.isHidden():
                self.browser.show()
                self.browser.adjustSize()

        except Exception as error:
            self.iface.messageBar().pushMessage(str(error), Qgis.Warning, 6)

    def cargarParcela(self, codMun, codPol, codPar, muniText):
        # Leyenda de la capa.
        leyenda = u"Parcela: {0}, {1}, {2}".format(
            codMun, codPol, codPar)

        # URL general
        # NOTA: utilizo WFS 1.1.0 ya que la URL que genera con el parámetro TYPENAMES (propio de 2.0.0)
        # no se procesa bien por el servidor de IDENA (mientras no se arregle).
        uri_template = "srsname=" + RRTN_CRS + \
            " typename=IDENA:{0} url=http://idena.navarra.es/ogc/wfs version=1.1.0"
        uri_template += " filter='{0}={1} AND {2}={3} AND {4}={5}'".format(
            IDENA_CMUNICIPIO_FIELD, codMun, IDENA_POLIGONO_FIELD, codPol, IDENA_PARCELA_FIELD, codPar)

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
                        muniText, codPol, codPar))

        return (vlayer, features[0])
