# Checkpoint Migration tool 
This Python 3 script converts XML exported with Check Point Webvisuals to the new R80 API.

```
$ ./xml2r80.py  -h
usage: xml2r80.py [-h] [-l LAYER] [-p PACKAGE] [-t TAG] [-o] [-r] [-s] [-n]
                 policy nat object services

 exportamos la politicas de Checkpoint

positional arguments:
  policy                fichero xml con las politicas
  nat                   fichero xml con los reglas de NAT
  object                fichero xml con los objetos
  services              fichero xml con los servicios

optional arguments:
  -h, --help            show this help message and exit
  -l LAYER, --layer LAYER policy layer
  -p PACKAGE, --package PACKAGE  policy package
  -t TAG, --tag TAG     tag
  -o, --objectsexport   export objects
  -r, --rulesexport     export rules
  -s, --servicesexport  export services
  -n, --natexport       export nat rules
 ```
# Notes
- Big objects and services files may required procces by smaller batchs
- Take note of missed objects when you import rules. Check object, delete policy packge and try again.
