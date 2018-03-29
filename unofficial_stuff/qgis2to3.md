# Notas migración QGIS 2.x a QGIS 3.x

## Enlaces
[Migración de plugins a QGIS3](https://github.com/qgis/QGIS/wiki/Plugin-migration-to-QGIS-3)
[QGIS Python API](http://python.qgis.org/api/)
[PyQGIS developer cookbook](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/intro.html)
[PyQGIS developer cookbook PDF](https://docs.qgis.org/testing/pdf/en/QGIS-testing-PyQGISDeveloperCookbook-en.pdf)

## Migración de código Python 2 a 3
Utilizo un entorno específico para la migración.

Tal y como indican instalo el paquete _furure_.

Para la migración de código **hay que usar** el _2to3_ de la instalación de QGIS por lo que me clono el repositorio de QGIS (1.9GB).
```
git clone git://github.com/qgis/QGIS.git
```

Si queremos clonar sólo la carpeta [Scripts](https://github.com/qgis/QGIS/tree/master/scripts)... aquí hay una [solución](http://link).

```
:: Ejecutar el Script 2to3 de QGIS desde el entorno virtual con 'future'.
:: -w: modifica los ficheros creando ficheros .bak.
:: -n: no backups.
(qgis300) PS C:\SRC\RRTNUtils\rrtn-utils> python.exe C:\SRC\QGIS\scripts\2to3 -w -n .\RrtnUtils\
```
