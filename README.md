# json2rdf
A generic json to rdf converter using python, with ability to generate Class/Property info and retain list sequence. 

## Usage
```
usage: converter.py [-h] [-b] [-c CLASSES] [-d DOMAIN] [-e ENCODING]
                    [-f FORMAT] [-n NAMESPACE] [-o OUTPUT] [-s] [-x EXTENSION]
                    input [input ...]

Generic JSON to RDF converter

positional arguments:
  input

optional arguments:
  -h, --help            show this help message and exit
  -b, --bnode           Use BNode instead of random generated instances for
                        objects
  -c CLASSES, --classes CLASSES
                        Specify root class name to generate class and property
                        declarations
  -d DOMAIN, --domain DOMAIN
                        Specify URI domain prefix (default: http://localhost/)
  -e ENCODING, --encoding ENCODING
                        Specify character encoding for input and output
                        (default: utf-8)
  -f FORMAT, --format FORMAT
                        Specify output format for RDF. Supported formats: xml,
                        n3, turtle, nt, pretty-xml, trix, trig, nquads
                        (default: turtle)
  -n NAMESPACE, --namespace NAMESPACE
                        Specify prefix name for domain (default: domain)
  -o OUTPUT, --output OUTPUT
                        Redirect output directory (default: output will be
                        saved in the same folder as input)
  -s, --sequence        Retain sequence information for json lists using
                        rdf:Seq
  -x EXTENSION, --extension EXTENSION
                        Specify custom file extension (without dot)
```
