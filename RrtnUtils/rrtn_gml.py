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

"""

timeStamp="{0}": 2018-04-02T15:18:35Z
numberMatched="{1}" numberReturned="{1}": 1


<cp:CadastralParcel gml:id="{0}.{1}">: ES.RRTN.CP.217050626
<gml:lowerCorner>{2}</gml:lowerCorner>: 616307.238 4710901.596
<gml:upperCorner>{3}</gml:upperCorner>: 616417.786 4711030.065
<cp:areaValue uom="m2">{4}</cp:areaValue>: 2308.49
<gml:Surface gml:id="{0}.{1}.S.1" srsName="urn:ogc:def:crs:EPSG::25830">

<base:localId>{1}</base:localId>
<base:namespace>{0}</base:namespace>
<cp:label>{2}</cp:label>: 626
<cp:nationalCadastralReference>{1}</cp:nationalCadastralReference>

"""

"""
Validaciones: no admitimos parcelas multiparte.

Casos de prueba:
- Parcela con varios agujeros.
"""

#from qgis.core import QgsVectorLayer#, QgsFeature
from builtins import range
from builtins import object
from datetime import datetime

# Bloques para la construcción del GML de salida.
# {0}: timeStamp, {1}: featNumber
GML_HEAD = '<?xml version="1.0" encoding="utf-8"?><wfs:FeatureCollection timeStamp="{0}" numberMatched="{1}" numberReturned="{1}" xmlns:wfs="http://www.opengis.net/wfs/2.0" xmlns:cp="http://inspire.ec.europa.eu/schemas/cp/4.0" xmlns:base="http://inspire.ec.europa.eu/schemas/base/3.3" xmlns:gml="http://www.opengis.net/gml/3.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.opengis.net/wfs/2.0 http://schemas.opengis.net/wfs/2.0/wfs.xsd http://inspire.ec.europa.eu/schemas/cp/4.0 http://inspire.ec.europa.eu/schemas/cp/4.0/CadastralParcels.xsd">'

# {0}: namespace, {1}: localId, {2}: lowerCorner, {3}: upperCorner, {4}: area
GML_CP_HEAD = '<wfs:member><cp:CadastralParcel gml:id="{0}.{1}"><gml:boundedBy><gml:Envelope srsName="urn:ogc:def:crs:EPSG::25830"><gml:lowerCorner>{2}</gml:lowerCorner><gml:upperCorner>{3}</gml:upperCorner></gml:Envelope></gml:boundedBy><cp:areaValue uom="m2">{4}</cp:areaValue><cp:beginLifespanVersion xsi:nil="true" nilReason="template"/><cp:geometry><gml:Surface gml:id="{0}.{1}.S.1" srsName="urn:ogc:def:crs:EPSG::25830"><gml:patches><gml:PolygonPatch>'

GML_EXT_RING_HEAD = '<gml:exterior>'
GML_EXT_RING_FOOT = '</gml:exterior>'

GML_INT_RING_HEAD = '<gml:interior>'
GML_INT_RING_FOOT = '</gml:interior>'

# Dimensión (2) es constante (X, Y). {0}: numCoord
GML_RING_HEAD = '<gml:LinearRing><gml:posList srsDimension="2" count="{0}">'
GML_RING_FOOT = '</gml:posList></gml:LinearRing>'

# {0}: namespace, {1}: localId, {2}: label
GML_CP_FOOT = '</gml:PolygonPatch></gml:patches></gml:Surface></cp:geometry><cp:inspireId><base:Identifier><base:localId>{1}</base:localId><base:namespace>{0}</base:namespace></base:Identifier></cp:inspireId><cp:label>{2}</cp:label><cp:nationalCadastralReference>{1}</cp:nationalCadastralReference><cp:validFrom xsi:nil="true" nilReason="template"/></cp:CadastralParcel></wfs:member>'
GML_FOOT = '</wfs:FeatureCollection>'


# Definición de datos de features compatibles.
LOCALID_FIELDNAME = u'localId'
LOCALID_FIELDLENGTH = 9
NAMESPACE_FIELDNAME = u'namespace'
NAMESPACE_FIELDLENGTH = 20
AREA_FIELDNAME = u'area'

class RrtnGmlWriter(object):
    """ Clase para la generación de GML INSPIRE CP 4.0 compatibles con RRTN """

    def __init__(self, gmlOutputPath, coordScale):
        """ Inicializar ruta de salida y número de decimales (coordScale) """
        self.gmlOutputPath = gmlOutputPath
        self.coordScale = coordScale

    def writeGml(self, features):
        """ Escribe el fichero GML en la ruta indicada """

        # Timestamp (hora generación).
        timeStamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        # Número de features a exportar.
        featNumber = len(features)

        with open(self.gmlOutputPath, 'w') as gmlOutputFile:
            # Escribir la cabecera del fichero.
            gmlOutputFile.write(GML_HEAD.format(timeStamp, featNumber))

            for feature in features:
                # Calcular cp:Envelope.
                ext = feature.geometry().boundingBox()
                xmin = round(ext.xMinimum(), self.coordScale)
                ymin = round(ext.yMinimum(), self.coordScale)
                xmax = round(ext.xMaximum(), self.coordScale)
                ymax = round(ext.yMaximum(), self.coordScale)

                lowerCorner = "{0} {1}".format(xmin, ymin)
                upperCorner = "{0} {1}".format(xmax, ymax)

                area = round(feature[AREA_FIELDNAME], 2) if type(feature[AREA_FIELDNAME]) == float else 0.0
                # {0}: namespace, {1}: localId, {2}: lowerCorner, {3}: upperCorner, {4}: area
                gmlOutputFile.write(GML_CP_HEAD.format(feature[NAMESPACE_FIELDNAME], feature[LOCALID_FIELDNAME], lowerCorner, upperCorner, area))
                
                # Obtener los anillos del polígono (MultiPolygon con un unico poligono).
                geom = feature.geometry()
                if not geom.isMultipart():
                    rings = geom.asPolygon()
                else:
                    rings = geom.asMultiPolygon()[0]
                
                # Escribir anillo exterior (siempre hay). Según Simple Features debe ir Counter Clockwise.
                ring = rings[0]
                if self.isCW(ring):
                    ring.reverse()

                gmlOutputFile.write(GML_EXT_RING_HEAD)
                gmlOutputFile.write(self.getRingData(ring))
                gmlOutputFile.write(GML_EXT_RING_FOOT)

                # Escribir los anillos interiores en caso de que existan.
                if len(rings) > 1:
                    
                    for i in range(1, len(rings)):
                        ring = rings[i]
                        
                        # Anilllos interiores deben ir Clockwise según Simple Features.
                        if not self.isCW(ring):
                            ring.reverse()
                    
                        gmlOutputFile.write(GML_INT_RING_HEAD)
                        gmlOutputFile.write(self.getRingData(ring))
                        gmlOutputFile.write(GML_INT_RING_FOOT)

                # Escribir el final de la CP.
                try:
                    label = int(feature[LOCALID_FIELDNAME][-4:])
                except ValueError:
                    label = feature[LOCALID_FIELDNAME]
                # {0}: namespace, {1}: localId, {2}: label
                gmlOutputFile.write(GML_CP_FOOT.format(feature[NAMESPACE_FIELDNAME], feature[LOCALID_FIELDNAME], label))

            # Escribir el final del fichero.
            gmlOutputFile.write(GML_FOOT.format(timeStamp, featNumber))

    def getRingData(self, ring):
        """ Obtener el texto del LineaRing """
                
        numCoord = len(ring)
        # Dimensión (2) es constante (X, Y). {0}: numCoord
        linearRingText = GML_RING_HEAD.format(numCoord)

        # Escribir las coordenadas
        for i in range(numCoord - 1):
            x = round(ring[i][0], self.coordScale)
            y = round(ring[i][1], self.coordScale)
            linearRingText += "{0} {1} ".format(x, y)
        
        x = round(ring[numCoord - 1][0], self.coordScale)
        y = round(ring[numCoord - 1][1], self.coordScale)
        linearRingText += "{0} {1}".format(x, y)

        linearRingText += GML_RING_FOOT

        return linearRingText

    def isCW(self, ring):
        """ Indica si los vértices del polígono están orientados en el sentido de las agujas del reloj (clockwise). Ref.: http://mathworld.wolfram.com/PolygonArea.html """
    
        sum = 0
        
        for i in range(len(ring) - 1):
            j = i +1
            
            xi = ring[i][0]
            yi = ring[i][1]
            xj = ring[j][0]
            yj = ring[j][1]
            
            sum += xi * yj - xj * yi
        
        return sum < 0

# Prueba exportación.
# 217, 5, 626

if __name__ == "__main__" or __name__ == "__console__":
    gmlWriter = RrtnGmlWriter("c:\\tmp\\prueba.gml", 3)
    features = list()
    
    # # Simulación de feature.
    # feature = dict()
    # feature[LOCALID_FIELDNAME] = '217050626'
    # feature[NAMESPACE_FIELDNAME] = 'ES.RRTN.CP'
    # feature[AREA_FIELDNAME] = 100.126
    
    # Feature seleccionada en el mapa.
    #    feature = ifeature
    #    features.append(feature)
    #    gmlWriter.writeGml(features)

    # Capa de trabajo.
    layer = iface.activeLayer()
    gmlWriter.writeGml(tuple(layer.getFeatures()))
