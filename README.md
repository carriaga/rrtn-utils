# QGIS RRTN Plugin
Utilidades de acceso al [Registro de la Riqueza Territorial de Navarra](https://catastro.navarra.es) (RRTN o Catastro de Navarra) en forma de plugin QGIS.

## TO DO list
0. Controles:
- Controlar el cambio de nombre de la capa de trabajo.
- Que la superficie se mantenga...? no tiene mucho sentido salvo que se pueda poner como campo calculado. Al exportar comprobar. Actualizarla poniendo la capa como editable. En todo caso no es relevante de cara a una RGA.
- Comprobaciones al exportar GML: campos, que no sea MULTI. Ver efecto de tener cambios en curso.
- Visualización de parcelas seleccionadas con huecos.

1. Comprobar que la proyección del mapa es la de Navarra (canvas.mapRenderer().destinationCrs().authid()):
Al seleccionar capa de trabajo. Preguntar y poner.

2. Plantear funcionamiento capa edición.
2.1 Agregar parcelas a la capa de trabajo:
- Importar GML CP RRTN.
- Detectar parcelas compatibles: WMS, del WFS...

2.2 Exportar a GML:
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

4. Colores para la validación de los inputs:
https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/