from qgis.gui import QgsMessageBar, QgsHighlight, QgsRubberBand

layer = self.iface.activeLayer()

def agregarResaltados(selectedLayer, pGeom, canvas):
    """
    Esta técnica permite agregar un resaltado a una geometría de una capa. Se mantendrá visible mientras el objeto QgsHighlight esté referenciado.
    Para que funcione la extensión de la vista debe contener al elmento resaltado.
    """
    parcelaExtent = QgsRectangle(pGeom.boundingBox())
    parcelaExtent.grow(2)
    # Centrar el mapa sobre la parcela.
    canvas.setExtent(parcelaExtent)
    canvas.refresh()

    # Crear un resaltado para la parcela seleccionada.
    # import QgsHighlight, import QColor
    h = QgsHighlight(canvas, pGeom, selectedLayer) 
    h.setColor(QColor(255,0,0,255))
    # Vaciar la lista de seleccionadas.
    del self.parcelasSeleccionadas[:]
    self.parcelasSeleccionadas.append(h)


def agregarCapaWFS(wfsLayer)
    """
    Agregar en una capa WFS una parcela buscada mediante una query a un WFS. No parece buena idea. Mejor copiar a una capa en memoria. Ya que entre ejecuciones de QGIS (si salvamos el mapa) no se conservan los filtros aplicados a las capas WFS.
    """

    # Agregar el registro al final (tras haber cambiado la extensión del canvas) ya que provoca refresco del mapa.
    layer.rendererV2().symbols()[0].setAlpha(0.5)
    
    QgsMapLayerRegistry.instance().addMapLayer(layer)
    # Esto evita alguna de las siguientes:
    # layer.triggerRepaint() -> Investigar.
    # canvas.refresh()

def agregarCapaMemoria(parcelaFeature):
    """
    Ejemplo de adición de una nueva capa de features en memoria.
    """
    # Agregar a una capa en memoria.
    searchedParcelsLayerCreated = False
    if not hasattr(self, "searchedParcelsLayer"):
        self.searchedParcelsLayer = QgsVectorLayer("Polygon?crs=" + RRTN_CRS, u"Reparcelación", "memory")
        self.searchedParcelsLayer.rendererV2().symbols()[0].setAlpha(0.5)
        searchedParcelsLayerCreated = True

    memFeat = QgsFeature()
    memFeat.setGeometry(parcelaFeature.geometry())
    self.searchedParcelsLayer.dataProvider().addFeatures([memFeat])
    self.searchedParcelsLayer.updateExtents()

    if searchedParcelsLayerCreated:
        QgsMapLayerRegistry.instance().addMapLayer(self.searchedParcelsLayer)
    else:
        canvas.refresh()

# Ejemplos de creación de capas en memoria.
vectorLyr = QgsVectorLayer('Polygon?crs=epsg:25830&field=localId:string(9)&field=namespace:string&field=area:double&index=yes', u"Parcelas actuación" , 'memory')
vectorLyr.isValid()
QgsMapLayerRegistry.instance().addMapLayer(vectorLyr)

"""
The memory data provider is used to construct in memory data, for example scratch data or data generated from spatial operations such as contouring. There is no inherent persistent storage of the data. The data source uri is constructed. The url specifies the geometry type ("point", "linestring", "polygon", "multipoint","multilinestring","multipolygon"), optionally followed by url parameters as follows:

crs=definition Defines the coordinate reference system to use for the layer. definition is any string accepted by QgsCoordinateReferenceSystem::createFromString()
index=yes Specifies that the layer will be constructed with a spatial index
field=name:type(length,precision) Defines an attribute of the layer. Multiple field parameters can be added to the data provider definition. type is one of "integer", "double", "string".

An example url is "Point?crs=epsg:4326&field=id:integer&field=name:string(20)&index=yes"
"""
# Exportar a shape
error = QgsVectorFileWriter.writeAsVectorFormat(cLayer, "c:\tmp\prueba.shp", provider.encoding(), provider.crs(),"ESRI Shapefile")

Sobrecargas:
QgsVectorFileWriter.writeAsVectorFormat(QgsVectorLayer, QString, QString, QgsCoordinateReferenceSystem, QString driverName="ESRI Shapefile", bool onlySelected=False, QString errorMessage=None, QStringList datasourceOptions=QStringList(), QStringList layerOptions=QStringList(), bool skipAttributeCreation=False, QString newFilename=None, QgsVectorFileWriter.SymbologyExport symbologyExport=QgsVectorFileWriter.NoSymbology, float symbologyScale=1, QgsRectangle filterExtent=None, QgsWKBTypes.Type overrideGeometryType=QgsWKBTypes.Unknown, bool forceMulti=False, bool includeZ=False, list-of-int attributes=QgsAttributeList(), QgsVectorFileWriter.FieldValueConverter fieldValueConverter=nullptr)

QgsVectorFileWriter.writeAsVectorFormat(QgsVectorLayer, QString, QString, QgsCoordinateTransform, QString driverName="ESRI Shapefile", bool onlySelected=False, QString errorMessage=None, QStringList datasourceOptions=QStringList(), QStringList layerOptions=QStringList(), bool skipAttributeCreation=False, QString newFilename=None, QgsVectorFileWriter.SymbologyExport symbologyExport=QgsVectorFileWriter.NoSymbology, float symbologyScale=1, QgsRectangle filterExtent=None, QgsWKBTypes.Type overrideGeometryType=QgsWKBTypes.Unknown, bool forceMulti=False, bool includeZ=False, list-of-int attributes=QgsAttributeList(), QgsVectorFileWriter.FieldValueConverter fieldValueConverter=nullptr)

QgsVectorFileWriter.writeAsVectorFormat(QgsVectorLayer, QString, QgsVectorFileWriter.SaveVectorOptions, QString newFilename=nullptr, QString errorMessage=nullptr)


