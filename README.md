# QGIS RRTN Plugin
Utilidades de acceso al [Registro de la Riqueza Territorial de Navarra](https://catastro.navarra.es) (RRTN o Catastro de Navarra) en forma de plugin QGIS.

## To do list
1. Listado de municipios.
2. Plantear funcionamiento capa edición y ver interés de usar **QgsFeatureRequest** para obtener features en memoria y copiar a capa virtual.

- Botón para eliminar todas las capas vectoriales de parcela cargada.
- Alternativa: copiar a capa en memoria la parcela seleccionada...
- Comprobar que la proyección del mapa es la de Navarra (canvas.mapRenderer().destinationCrs().authid()):
    - Asignar CRS Navarra como check. Pestaña general.
    - Cargar WMS Catastro como check. Pestaña general.
    - Check (marcar todas).
- Compatibilidad con la última LTE (urls servicios WMS y WFS). Revisar valores constantes.
- Resaltar parcela vía WMS: son tres capas...
- Que agregar parcela como capa sea opcional.
- Búsquedas:
    - Habilitar sólo si CRS Navarra y municipios cargados.
    - Cargar lista de municipios en un combo en un hilo aparte tras mostrar plugin.

- Capa de parcelas en memoria.

## Done
1. Cambiar la llamada WFS en una única llamada: finalmente no, ya que QgsVectorLayer no está preparado para acceder simultáneamente a varias capas (typenames).

Al agregar la capa WFS se produce una llamada _DescribeFeatureType_.
Se ha reducido el total de llamadas a 2, evitando llamar a _featureCount_.