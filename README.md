# QGIS RRTN Plugin
Utilidades de acceso al [Registro de la Riqueza Territorial de Navarra](https://catastro.navarra.es) (RRTN o Catastro de Navarra) en forma de plugin QGIS.

## To do list
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

## Ayudas para debuggear
```
import inspect
inspect.getmembers(layer)
dir(layer)
k for k in dir(layer) if "url" in k.lower()]
```
Guardar un dato en 'iface':
```
self.iface.datos = error
```

Desde la consola accedemos a _iface.datos_ directamente.
