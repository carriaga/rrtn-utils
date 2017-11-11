from qgis.gui import QgsMessageBar, QgsHighlight, QgsRubberBand

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
    Agregar en una capa WFS. No parece buena idea. Mejor copiar a una capa en memoria. Ya que entre ejecuciones de QGIS (si salvamos el mapa) no se conservan los filtros aplicados a las capas WFS.
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
        self.searchedParcelsLayer = QgsVectorLayer("MultiPolygon?crs=" + RRTN_CRS, "Parcelas localizadas", "memory")
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
