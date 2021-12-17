# generic json converter
import sys
import json
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import XSD, OWL, RDF, RDFS
from urllib.parse import quote
from os import path
import argparse
import uuid


def node():
    if args.bnode:
        return BNode()
    else:
        return URIRef(args.domain + str(uuid.uuid4()))


def iterate(graph: Graph, stack: list, prop: str, entity, tree: dict, parent: str, list_id: int):
    if type(entity) == dict:
        stack.append(node())
        if args.classes is not None and not args.bnode:
            graph.add((stack[-1], RDF.type, URIRef(args.domain + (args.classes + "_" + quote(parent)).strip("_"))))
        if len(stack) > 1:
            if list_id>0:
                graph.add((stack[-2], URIRef(str(RDF)+"_"+str(list_id)), stack[-1]))
            else:
                if args.classes is None:
                    graph.add((stack[-2], URIRef(args.domain + quote(prop)), stack[-1]))
                else:
                    graph.add((stack[-2], URIRef(args.domain + quote(parent.strip("_"))), stack[-1]))
        for k, v in entity.items():
            if prop not in tree:
                tree[prop] = {}
            iterate(graph, stack, k, v, tree[prop], parent + k + "_", 0)
        del stack[-1]
    elif type(entity) == list:
        if args.sequence:
            stack.append(node())
            if args.classes is not None and not args.bnode:
                graph.add((stack[-1], RDF.type, RDF.Seq))
            if len(stack) > 1:
                if args.classes is None:
                    graph.add((stack[-2], URIRef(args.domain + quote(prop)), stack[-1]))
                else:
                    graph.add((stack[-2], URIRef(args.domain + quote(parent.strip("_"))), stack[-1]))
            for i in range(len(entity)):
                iterate(graph, stack, prop, entity[i], tree, parent, i+1)
            del stack[-1]
        else:
            for item in entity:
                iterate(graph, stack, prop, item, tree, parent, 0)
    else:
        const = None
        if type(entity) == str:
            tree[prop] = XSD.string
            const = Literal(entity)
        elif type(entity) == int:
            tree[prop] = XSD.integer
            const = Literal(entity, datatype=XSD.integer)
        elif type(entity) == float:
            tree[prop] = XSD.double
            const = Literal(entity, datatype=XSD.double)
        elif type(entity) == bool:
            tree[prop] = XSD.boolean
            const = Literal(entity, datatype=XSD.boolean)
        else:
            print("Unknown type " + str(type(entity)), file=sys.stderr)
        if const is not None:
            if len(stack) > 0:
                if list_id > 0:
                    graph.add((stack[-1], URIRef(str(RDF)+"_"+str(list_id)), const))
                else:
                    if args.classes is None:
                        graph.add((stack[-1], URIRef(args.domain + quote(prop)), const))
                    else:
                        graph.add((stack[-1], URIRef(args.domain + quote(parent.strip("_"))), const))

            else:
                print("RDF conversion is only possible when root element is object or array", file=sys.stderr)


def parse_tree(graph, root, parent, tree: dict):
    for k, v in tree.items():
        if type(v) == dict:
            graph.add((URIRef(args.domain + parent + quote(k)), RDF.type, OWL.ObjectProperty))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.label, Literal(k)))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.domain, URIRef(args.domain + (root + parent).strip("_"))))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.range, URIRef(args.domain + root + parent + k)))
            graph.add((URIRef(args.domain + root + parent + quote(k)), RDF.type, OWL.Class))
            graph.add((URIRef(args.domain + root + parent + quote(k)), RDFS.label, Literal(k)))
            parse_tree(graph, root, parent + quote(k) + "_", v)
        else:
            graph.add((URIRef(args.domain + parent + quote(k)), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.label, Literal(k)))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.domain, URIRef(args.domain + root + parent.strip("_"))))
            graph.add((URIRef(args.domain + parent + quote(k)), RDFS.range, v))


def outname(input, directory, format):
    if args.extension is not None:
        ext = "."+args.extension
    else:
        ext = extensions[format]
    if directory is not None:
        return path.join(directory, path.splitext(path.basename(input))[0] + ext)
    else:
        return path.splitext(input)[0] + ext


extensions = {
    "xml": ".xml",
    "n3": ".n3",
    "turtle": ".ttl",
    "nt": ".nt",
    "pretty-xml": ".xml",
    "trix": ".trix",
    "trig": ".trig",
    "nquads": ".nq"
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generic JSON to RDF converter')
    parser.add_argument('input', nargs='+')
    parser.add_argument('-b', '--bnode', action='store_true',
                        help="Use BNode instead of random generated instances for objects")
    parser.add_argument('-c', '--classes', help="Specify root class name to generate class and property declarations")
    parser.add_argument('-d', '--domain', help="Specify URI domain prefix (default: %(default)s)",
                        default="http://localhost/")
    parser.add_argument('-e', '--encoding',
                        help="Specify character encoding for input and output (default: %(default)s)", default="utf-8")
    parser.add_argument('-f', '--format',
                        help="Specify output format for RDF. Supported formats: xml, n3, turtle, nt, pretty-xml, "
                             "trix, trig, nquads (default: %(default)s)", default="turtle")
    parser.add_argument('-n', '--namespace', help="Specify prefix name for domain (default: %(default)s)",
                        default="domain")
    parser.add_argument('-o', '--output',
                        help="Redirect output directory (default: output will be saved in the same folder as input)")
    parser.add_argument('-s', '--sequence', action='store_true',
                        help="Retain sequence information for json lists using rdf:Seq")
    parser.add_argument('-x', '--extension', help="Specify custom file extension (without dot)")
    args = parser.parse_args()

    if args.format not in extensions:
        print("Unsupported format: " + args.format)
        exit(-1)

    if args.domain[-1] != "#":
        args.domain += "#"

    for file in args.input:
        with open(file, encoding=args.encoding) as f:
            obj = json.load(f)
        g = Graph()
        g.bind(args.namespace, args.domain)
        g.bind("owl", OWL)
        g.bind("rdf", RDF)
        g.bind("rdfs", RDFS)
        objstack = []
        objtree = {}
        iterate(g, objstack, "root", obj, objtree, "", 0)
        if args.classes is not None:
            g.add((URIRef(args.domain), RDF.type, OWL.Ontology))
            g.add((URIRef(args.domain + quote(args.classes)), RDF.type, OWL.Class))
            g.add((URIRef(args.domain + quote(args.classes)), RDFS.label, Literal(args.classes)))
            parse_tree(g, args.classes + "_", "", objtree["root"])
        g.serialize(destination=outname(file, args.output, args.format), encoding=args.encoding, format=args.format)
