# QGIS RRTN Plugin
Utilidades de acceso al [Registro de la Riqueza Territorial de Navarra](https://catastro.navarra.es) (RRTN o Catastro de Navarra) en forma de plugin QGIS.

## TO DO list
1. Comprobar que la proyección del mapa es la de Navarra (canvas.mapRenderer().destinationCrs().authid()):
- Asignar CRS Navarra como check. Pestaña general: un texto en rojo, con tooltip, que al clicar sobre él pregunte si se quiere poner el SRS.
- Cargar WMS Catastro como check. Pestaña general. Pasarlo a la zona de abajo: "cargar WMS al entrar". Que recuerde el estado de la última ejecución...
- Check (marcar todas).

2. Plantear funcionamiento capa edición y ver interés de usar **QgsFeatureRequest** para obtener features en memoria y copiar a capa virtual.

- Compatibilidad con la última LTE (urls servicios WMS y WFS). Revisar valores constantes.
- Resaltar parcela vía WMS: son tres capas...
- Que agregar parcela como capa sea opcional.
- Búsquedas:
    - Habilitar sólo si CRS Navarra y municipios cargados.
    - Cargar lista de municipios en un combo en un hilo aparte tras mostrar plugin.

- Capa de parcelas en memoria.

## Change log
2017/11/11: el resaltado de la parcela localizada se hace mediante QgsRubberBand (sin necesidad de agregar capas a la layenda). El resaltado se mantiene mientras no se localice otra o se realice la acción **Refresh**.

La localización de parcelas controla que haya un mapa cargado, de lo contrario no se hace y se avisa al usuario.

2017/10/29: obtener la lista de municipios de Navarra para presentarla en un ComboBox. Así se permite seleccionar un municipio por nombre o teclear el código de municipio a la hora de realizar una búsqueda de parcela.

2017/10/15: Cambiar la llamada WFS en una única llamada: finalmente no, ya que QgsVectorLayer no está preparado para acceder simultáneamente a varias capas (typenames).

Al agregar la capa WFS se produce una llamada _DescribeFeatureType_.
Se ha reducido el total de llamadas a 2, evitando llamar a _featureCount_.
