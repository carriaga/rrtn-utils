'''
Pruebas de rendimiento:
- REFCAT vs CMUNICIPIO, POLIGONO, PARCELA
- version WFS
- maxFeatures=1

http://idena.navarra.es/ogc/wfs?filter=<ogc:PropertyIsEqualTo xmlns:ogc="http://www.opengis.net/ogc"><ogc:PropertyName>REFCAT</ogc:PropertyName><ogc:Literal>201061838</ogc:Literal></ogc:PropertyIsEqualTo>&request=GetFeature&typename=CATAST_Pol_ParcelaRusti&version=1.1.0&service=WFS

http://idena.navarra.es/ogc/wfs?filter=<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc"><ogc:And><ogc:And><ogc:PropertyIsEqualTo><ogc:PropertyName>CMUNICIPIO</ogc:PropertyName><ogc:Literal>201</ogc:Literal></ogc:PropertyIsEqualTo><ogc:PropertyIsEqualTo><ogc:PropertyName>POLIGONO</ogc:PropertyName><ogc:Literal>6</ogc:Literal></ogc:PropertyIsEqualTo></ogc:And><ogc:PropertyIsEqualTo><ogc:PropertyName>PARCELA</ogc:PropertyName><ogc:Literal>1838</ogc:Literal></ogc:PropertyIsEqualTo></ogc:And></ogc:Filter>&request=GetFeature&typename=CATAST_Pol_ParcelaRusti&version=1.1.0&service=WFS

http://idena.navarra.es/ogc/wfs?REQUEST=GetFeature&VERSION=2.0.0&TYPENAMES=IDENA:CATAST_Pol_ParcelaRusti&FILTER=<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0"><fes:PropertyIsEqualTo><fes:ValueReference>REFCAT</fes:ValueReference><fes:Literal>201061838</fes:Literal></fes:PropertyIsEqualTo></fes:Filter>&SERVICE=WFS

http://idena.navarra.es/ogc/wfs?REQUEST=GetFeature&VERSION=2.0.0&TYPENAMES=IDENA:CATAST_Pol_ParcelaRusti&SERVICE=WFS&FILTER=<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0"><fes:And><fes:And><fes:PropertyIsEqualTo><fes:ValueReference>CMUNICIPIO</fes:ValueReference><fes:Literal>201</fes:Literal></fes:PropertyIsEqualTo><fes:PropertyIsEqualTo><fes:ValueReference>POLIGONO</fes:ValueReference><fes:Literal>6</fes:Literal></fes:PropertyIsEqualTo></fes:And><fes:PropertyIsEqualTo><fes:ValueReference>PARCELA</fes:ValueReference><fes:Literal>1838</fes:Literal></fes:PropertyIsEqualTo></fes:And></fes:Filter>
'''

# refcat, version, maxFeat=1
layer = cargarParcela(
    codMunicipio, poligono, parcela, True, "1.1.0", True)
layer = cargarParcela(
    codMunicipio, poligono, parcela, True, "1.1.0", False)
layer = cargarParcela(
    codMunicipio, poligono, parcela, False, "1.1.0", True)
layer = cargarParcela(
    codMunicipio, poligono, parcela, False, "1.1.0", False)

layer = cargarParcela(
    codMunicipio, poligono, parcela, True, "2.0.0", True)
layer = cargarParcela(
    codMunicipio, poligono, parcela, True, "2.0.0", False)
layer = cargarParcela(
    codMunicipio, poligono, parcela, False, "2.0.0", True)
layer = cargarParcela(
    codMunicipio, poligono, parcela, False, "2.0.0", False)

def cargarParcela(codMunicipio, poligono, parcela, refcat, version, maxFeat):
    # Leyenda de la capa.
    leyenda = "Parcela: {0}, {1}, {2}".format(
        codMunicipio, poligono, parcela)

    # URL general
    uri_template = "srsname=EPSG:25830 typename=IDENA:{0} url=http://idena.navarra.es/ogc/wfs"
    uri_template += " version={0}".format(version)

    if maxFeat:
        uri_template += " maxNumFeatures=1"

    uri_template += " sql=SELECT * FROM {0} WHERE "

    # Si es verdadero consultamos REFCAT si no los campos separados.
    if refcat:
        uri_template += "REFCAT={0}".format(codMunicipio *
                                    1000000 + poligono * 10000 + parcela)
    else:
        uri_template += "CMUNICIPIO={0} AND POLIGONO={1} AND PARCELA={2}".format(
            codMunicipio, poligono, parcela)

    # Búsqueda en parcelas urbanas
    uri = uri_template.format("CATAST_Pol_ParcelaUrba")
    print(uri)
    vlayer = QgsVectorLayer(uri, leyenda, "WFS")

    if vlayer.featureCount() != 1:
        # Búsqueda en rústicas (201, 6, 1838).
        uri = uri_template.format("CATAST_Pol_ParcelaRusti")
        print(uri)
        vlayer = QgsVectorLayer(uri, leyenda, "WFS")

        if vlayer.featureCount() != 1:
            # Búsqueda en mixtas (201, 1, 1088).
            uri = uri_template.format("CATAST_Pol_ParcelaMixta")
            print(uri)
            vlayer = QgsVectorLayer(uri, leyenda, "WFS")

            if vlayer.featureCount() != 1:
                raise Exception(leyenda + ", NO ENCONTRADA.")

    return vlayer

'''
QgsFeatureRequest: obtener features sobre una capa ya creada.
'''

'''
    sql vs filter
'''

# URL general
uri_template = "srsname=EPSG:25830 typename=IDENA:{0} url=http://idena.navarra.es/ogc/wfs version=2.0.0"
'''
# Con SELECT podemos configurar los atributos de la Feature pero el WFS devuelve todos los atributos a QGIS.
uri_template += " sql=SELECT * FROM {0} WHERE "
uri_template += "CMUNICIPIO={0} AND POLIGONO={1} AND PARCELA={2}".format(
    codMunicipio, poligono, parcela)
'''
uri_template += " filter='CMUNICIPIO={0} AND POLIGONO={1} AND PARCELA={2}'".format(
    codMunicipio, poligono, parcela)

# Búsqueda en parcelas urbanas
uri = uri_template.format("CATAST_Pol_ParcelaUrba")
