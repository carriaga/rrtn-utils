# Notas migración QGIS 2.x a QGIS 3.x

## Enlaces
[Migración de plugins a QGIS3](https://github.com/qgis/QGIS/wiki/Plugin-migration-to-QGIS-3)
[QGIS Python API](https://qgis.org/pyqgis/3.10/)
[PyQGIS developer cookbook](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html)
[PyQGIS developer cookbook PDF](https://docs.qgis.org/testing/pdf/en/QGIS-testing-PyQGISDeveloperCookbook-en.pdf)

## Migración de código Python 2 a 3 v2
Utilizo un entorno específico para la migración.

Tal y como indican instalo el paquete _furure_.

Esta vez instalo y utilizo el paquete _qgis2to3_.

```
:: Ejecutar el Script qgis2to3 desde el entorno virtual con 'future'.
:: -w: modifica los ficheros creando ficheros .bak. Si no se indica sólo genera un 'diff'.
:: -n: no backups. No lo uso para poder comparar.
(rrtn-utils) C:\SRC\RRTN\rrtn-utils>python.exe C:\Users\carriaga\Anaconda3\envs\rrtn-utils\Scripts\qgis2to3 -w RrtnUtils
```

Errores de migración:
ImportError: cannot import name 'QgsMapLayerRegistry' from 'qgis.core' (C:/Dev/QGIS/QGIS310/apps/qgis-ltr/./python\qgis\core\__init__.py)
-> Cambiar a QgsProject en todas las ocurrencias de esa clase.

ImportError: cannot import name 'QGis' from 'qgis.core' (C:/Dev/QGIS/QGIS310/apps/qgis-ltr/./python\qgis\core\__init__.py)
-> Cambiar a Qgis en todas las ocurrencias.
-> QGis.Polygon -> QgsWkbTypes.Polygon

TypeError: qRegisterResourceData(int, bytes, bytes, bytes): argument 2 has unexpected type 'str'
-> Poner 'b' delante de las cadenas de texto tipo bytearray: qt_resource_name = b"\

AttributeError: module 'qgis.PyQt.QtGui' has no attribute 'QDockWidget'
-> Cambiar de 'QtGui.QDockWidget' a 'QDockWidget'

AttributeError: type object 'QgsMessageBar' has no attribute 'SUCCESS'
-> Cambiar a Qgis.Success, Qgis.Critical, Qgis.Warning. Eliminar import de QgsMessageBar.

 addItem(self, QIcon, str, userData: Any = None): argument 1 has unexpected type 'bytes'
-> Añadir unicodedata.normalize('NFD', feature[IDENA_MUNICIPIO_FIELD]).encode('ascii', 'ignore').upper()**.decode("utf-8")**

NameError: name 'QRegExpValidator' is not defined
-> Añadir import

En onBtnNewWorkingLayerClick:
AttributeError: 'ValueError' object has no attribute 'message'
-> Añadir getSaveFileName()[0] 

En onBtnAddParcelaSelClick:
AttributeError: 'QgsVectorLayer' object has no attribute 'setSelectedFeatures'
-> Cambiar a .selectByIds([s.id() for s in selection])

During handling of the above exception, another exception occurred:
    AttributeError: 'Exception' object has no attribute 'message'



## Migración de código Python 2 a 3 v1
Utilizo un entorno específico para la migración.

Tal y como indican instalo el paquete _furure_.

Para la migración de código **hay que usar** el _2to3_ de la instalación de QGIS por lo que me clono el repositorio de QGIS (1.9GB).
```
git clone git://github.com/qgis/QGIS.git
```

Si queremos clonar sólo la carpeta [Scripts](https://github.com/qgis/QGIS/tree/master/scripts)... aquí hay una [solución](http://link).

```
:: Ejecutar el Script 2to3 de QGIS desde el entorno virtual con 'future'.
:: -w: modifica los ficheros creando ficheros .bak. Si no se indica sólo genera un 'diff'.
:: -n: no backups.
(qgis300) PS C:\SRC\RRTNUtils\rrtn-utils> python.exe C:\SRC\QGIS\scripts\2to3 -w -n .\RrtnUtils\
```
