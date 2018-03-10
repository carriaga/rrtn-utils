# QGIS RRTN Plugin
Utilidades de acceso al [Registro de la Riqueza Territorial de Navarra](https://catastro.navarra.es) (RRTN o Catastro de Navarra) en forma de plugin QGIS.

## Change log
2018/03/10:
Incorporada la funcionalidad de inicializar el mapa al WMS de IDENA y al CRS 25830 mediante la configuración de usuario/checkboxes (eliminado botón inicializar mapa).

Poner validador de expresión regular a los campos de polígono y parcela.

Agregar funcinalidad para consultar datos de la parcela en la web del RRTN en un QWebView integrado en un QDialog.

Bug: no cargar WMS IDENA si ya está en la ToC.

Refactorización: obtención de códigos localizadores en un método común.

2018/02/18:
Agregados checkboxes para asignar el CRS 25830 y cargar WMS RRTN @ IDENA al inicio almancenando los valores indicados por el usuario en settings (QSettings).

2018/02/10:
Funcionamiento completo del botón que permite seleccionar una capa de trabajo entre las que hay cargadas (sin tener en cuenta la que se pueda tener ya seleccionada).

2018/02/02:
Detecta si se ha eleminado de la ToC la capa de trabajo para dejar de referenciarla.

2018/01/28: 
Nuevo botón para permitir seleccionar una capa de trabajo compatible entre las capas cargadas. Desarrollado parcialmente: localizar capas compatibles para mostrarlas al usuario.

2018/01/27: 
Nuevo icono para la barra de plugins.

Al recargar el plugin limpiar parcela resaltada.

Crear una capa de trabajo que sea un archivo shape. Se trata de tener  dentificada la capa de trabajo que tiene que cumplir una determinada estructura (los campos imprescindibles para generar un GML CP 4.0).

2017/12/17:
Corregido error en mensajes de error con acentos poniendo el prefijo _u_ en las cadenas de texto. Nuevo botón para la creación de una capa de trabajo en memoria (para las parcelas de trabajo).

2017/11/11:
El resaltado de la parcela localizada se hace mediante QgsRubberBand (sin necesidad de agregar capas a la layenda). El resaltado se mantiene mientras no se localice otra o se realice la acción **Refresh**.

La localización de parcelas controla que haya un mapa cargado, de lo contrario no se hace y se avisa al usuario.

2017/10/29: 
Obtener la lista de municipios de Navarra para presentarla en un ComboBox. Así se permite seleccionar un municipio por nombre o teclear el código de municipio a la hora de realizar una búsqueda de parcela.

2017/10/15: 
Cambiar la llamada WFS en una única llamada: finalmente no, ya que QgsVectorLayer no está preparado para acceder simultáneamente a varias capas (typenames).

Al agregar la capa WFS se produce una llamada _DescribeFeatureType_.
Se ha reducido el total de llamadas a 2, evitando llamar a _featureCount_.

## TO DO list
1. Realizar las acciones de los checks de WMS y CRS.
Comprobar que la proyección del mapa es la de Navarra (canvas.mapRenderer().destinationCrs().authid()):

2. Plantear funcionamiento capa edición.
2.1 Agregar parcelas a la capa de trabajo:
- Importar archivos de trabajo existentes, cambiar la capa de trabajo.
- También se puede seleccionar como capa de trabajo al añadir al ToC.
- Función que permita validar la estructura de la capa de trabajo seleccionada: capa_trabajo_compatible.
- Agregar la parcela localizada en la búsqueda.
- Importar GML CP RRTN.

2.2 Exportar a GML:
- Configurar etiquetado por referencia catastral y activar por defecto.
- Posibilidad de poner editores con valores cerrados.
- Exportar a GML Navarra: 
    - Opción de sólo la parcela seleccionada.
    - Verificación de atributos.
    - Mensaje de resumen de identificadores y superficies a exportar.
- Asistente para parcelas de otras capas que reconozca atributos necesarios.
- Ver interés de usar **QgsFeatureRequest** para obtener features en memoria y copiar a capa virtual.
- Mantener el campo Superficie actualizado.

3. Otros:
- Compatibilidad con la última LTE (urls servicios WMS y WFS). Revisar valores constantes.
- Resaltar parcela vía WMS: son tres capas...
- Que agregar parcela como capa sea opcional.
- Búsquedas:
    - Habilitar sólo si CRS Navarra y municipios cargados.
    - Cargar lista de municipios en un combo en un hilo aparte tras mostrar plugin.
