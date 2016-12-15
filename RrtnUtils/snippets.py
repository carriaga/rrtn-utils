# canvas.mapRenderer().destinationCrs().authid()

"""
Code snipets.

        loaded = False
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if layer.type() == QgsMapLayer.RasterLayer:
                print(layer.name()) 
            
        not [x for x in layer.dataProvider().dataSourceUri().split("&") if "http://idena.navarra.es/ogc/wms" in x.split("=") ]

'restrictToRequestBBOX=\'1\' srsname=\'EPSG:25830\' typename=\'IDENA:CATAST_Pol_ParcelaUrba\' url=\'http://idena.navarra.es/ogc/wfs\' version=\'auto\' table="" sql='

'restrictToRequestBBOX=\'1\' srsname=\'EPSG:25830\' typename=\'IDENA:CATAST_Pol_ParcelaUrba\' url=\'http://idena.navarra.es/ogc/wfs\' version=\'auto\' table="" sql=SELECT * FROM CATAST_Pol_ParcelaUrba WHERE REFCAT=\'201010001\''


""
