# Notas
Apuntes y notas relacionadas con el desarrollo de este plugin.

## Ayudas para debuggear
```
import inspect
inspect.getmembers(layer)
dir(layer)
[k for k in dir(layer) if "url" in k.lower()]
```
Guardar un dato en 'iface':
```
self.iface.datos = error
```
Desde la consola accedemos a _iface.datos_ directamente.

Current layer:
cl = iface.mapCanvas().currentLayer()

## Cargar capas en memoria
https://gis.stackexchange.com/questions/70135/how-can-i-define-the-layer-crs-for-a-memory-layer-in-pyqgis
https://gis.stackexchange.com/questions/120385/drawing-some-points-in-qgis-2-4-using-python

Y QgsHighlight:
https://webgeodatavore.github.io/pyqgis-samples/gui-group/QgsHighlight.html
https://gis.stackexchange.com/questions/245150/how-to-flash-selected-feature-using-pyqgis


## Consulta WFS IDENA
1. Capas a consultar: &typename=IDENA:CATAST_Pol_ParcelaUrba,IDENA:CATAST_Pol_ParcelaRusti,IDENA:CATAST_Pol_ParcelaMixta
 
En el orden indicado para obtener una mejor respuesta.
 
2. Limitar número de features a 1: NO APLICAR.
El campo REFCAT es único por lo tanto la búsqueda devolverá como máximo una feature.
El tiempo de respuesta empeora con WFS 1.1.0. Parece que trabaja más por incluir maxFeatures=1.
No parece que tenga sentido si se busca por un campo clave o de resultados reducidos.

Con WFS 2.0.0 no parece tener incidencia, y en algunos casos mejora.
 
En WFS 1.1.0 añadir &maxFeatures=1
 
3. Propiedades a devolver: &propertyname=*
O propiedades específicas.

4. srsname (tema menor): &srsname=urn:x-ogc:def:crs:EPSG:25830
Puede obviarse para Navarra por ser el SRS por defecto.  
Ejemplo de URL: http://idena.navarra.es/ogc/wfs?filter=<ogc:PropertyIsEqualTo xmlns:ogc="http://www.opengis.net/ogc"><ogc:PropertyName>REFCAT</ogc:PropertyName><ogc:Literal>201061838</ogc:Literal></ogc:PropertyIsEqualTo>&request=GetFeature&typename=CATAST_Pol_ParcelaUrba,CATAST_Pol_ParcelaRusti,CATAST_Pol_ParcelaMixta&version=1.1.0&propertyname=the_geom&service=WFS&maxFeatures=1

<ogc:Filter xmlns:ogc="http://www.opengis.net/ogc"><ogc:And><ogc:And><ogc:PropertyIsEqualTo><ogc:PropertyName>CMUNICIPIO</ogc:PropertyName><ogc:Literal>201</ogc:Literal></ogc:PropertyIsEqualTo><ogc:PropertyIsEqualTo><ogc:PropertyName>POLIGONO</ogc:PropertyName><ogc:Literal>6</ogc:Literal></ogc:PropertyIsEqualTo></ogc:And><ogc:PropertyIsEqualTo><ogc:PropertyName>PARCELA</ogc:PropertyName><ogc:Literal>1838</ogc:Literal></ogc:PropertyIsEqualTo></ogc:And></ogc:Filter>

2.0.0:
<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0"><fes:PropertyIsEqualTo><fes:ValueReference>REFCAT</fes:ValueReference><fes:Literal>201061838</fes:Literal></fes:PropertyIsEqualTo></fes:Filter>

<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0"><fes:And><fes:And><fes:PropertyIsEqualTo><fes:ValueReference>CMUNICIPIO</fes:ValueReference><fes:Literal>201</fes:Literal></fes:PropertyIsEqualTo><fes:PropertyIsEqualTo><fes:ValueReference>POLIGONO</fes:ValueReference><fes:Literal>6</fes:Literal></fes:PropertyIsEqualTo></fes:And><fes:PropertyIsEqualTo><fes:ValueReference>PARCELA</fes:ValueReference><fes:Literal>1838</fes:Literal></fes:PropertyIsEqualTo></fes:And></fes:Filter>

Sin **srsname** y sólo campo geométrico (the_geom).
 
WFS 1.1.0 lleva aparejado GML 3.1.1 por defecto. 
GML 3.2.1 puede obtenerse con WFS 1.1.0 indicando el parámetro outputFormat=gml32.
WFS 2.0 lleva GML 3.2.1 por defecto.

 GML 3.2.1 el srsname se indica con el namespace **urn:ogc:…**, es decir, urn:ogc:def:crs:EPSG:25830.  GML 3.2.1 en vez de una Feature Collection devuelve tres, una por cada capa solicitada, aunque dos estarán vacías en el caso del ejemplo.  Para pedir WFS 2.0: omitir &version o poner el valor &version=2.0. En GeoServer, tirando de Shapes va mucho más lento (distinta implementación).

### Consulta desde QGIS
Al indicarle varias capas en **typename** deja de funcionar. Puede ser lógico ya que por ejemplo con WFS 2.0 obtendríamos varias FeatureCollection (una por capa) y esto puede no ser adecuado para la clase [QgsVectorLayer](https://qgis.org/api/classQgsVectorLayer.html).

```
The url can be a HTTP url to a WFS server (legacy, e.g. http://foobar/wfs?TYPENAME=xxx&SRSNAME=yyy[&FILTER=zzz]), or, starting with QGIS 2.16, a URI constructed using the QgsDataSourceUri class with the following parameters: 
* url=string (mandatory): HTTP url to a WFS server endpoint. e.g http://foobar/wfs 
* typename=string (mandatory): WFS typename 
* srsname=string (recommended): SRS like 'EPSG:XXXX' 
* username=string 
* password=string 
* authcfg=string 
* version=auto/1.0.0/1.1.0/2.0.0 
* sql=string: full SELECT SQL statement with optional WHERE, ORDER BY and possibly with JOIN if supported on server 
* filter=string: QGIS expression or OGC/FES filter 
* restrictToRequestBBOX=1: to download only features in the view extent (or more generally in the bounding box of the feature iterator) 
* maxNumFeatures=number 
* IgnoreAxisOrientation=1: to ignore EPSG axis order for WFS 1.1 or 2.0 
* InvertAxisOrientation=1: to invert axis order 
* hideDownloadProgressDialog=1: to hide the download progress dialog
* 
```

## Resultados comparativas WFS IDENA
Se comprueba que la búsqueda por los campos CMUNICIPIO, POLIGONO, PARCELA, es **hasta tres veces** más rápida que la búsqueda por REFCAT.

Limitar el número de features devueltas a 1: en WFS 1.1.0 empeora los tiempos y en WFS 2.0.0 no parece incidir, y en algún caso mejora, pero no parece directamente achacable a este parámetro.

Aparentemente no hay diferencia entre WFS 1.1.0 y 2.0.0 en parcelas urbanas al realizar las llamadas desde QGIS. Tampoco en rústicas. Si acaso mejora algo con WFS 2.0.0. Desde PostMan siempre va mejor con WFS 1.1.0.

15.10.2017: dejo la búsqueda basada en los tres campos y WFS 2.0.0. No pongo el maxFeatures=1.
