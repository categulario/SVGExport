#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import subprocess
import os
import xml.etree.ElementTree as ET
import re
from uuid import uuid1

class Color:
    """An hex color"""
    def __init__(self, base_string):
        if not re.match('^[a-fA-F0-9]{6}$', base_string):
            raise argparse.ArgumentTypeError(R+'Color inválido, use algo como a88f67')

        try:
            red   = int('0x'+base_string[1:][0:2], 16)
            green = int('0x'+base_string[1:][2:4], 16)
            blue  = int('0x'+base_string[1:][4:6], 16)
        except ValueError:
            raise argparse.ArgumentTypeError(R+'Color inválido, use algo, como a88f67')

        self.base_string = base_string
        self.red = red
        self.green = green
        self.blue = blue

    def __str__(self):
        return '#'+self.base_string

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Compila un archivo de iconos SVG en múltiples imágenes de diferentes tamaños")

    parser.add_argument("inputfile", type=argparse.FileType('r'), help="Archivo a leer")
    parser.add_argument("-o", "--output", type=str, help="Archivo de salida")
    parser.add_argument("-c", "--color", type=Color, help="Color para exportar los íconos", default="000000")
    parser.add_argument("-b", "--basecolor", type=Color, help="Color actual para cada ícono", default="000000")
    parser.add_argument("-e", "--exportsize", type=int, help="Tamaños (de ancho) a los cuales exportar los íconos", action='append')

    args = parser.parse_args()

    inputfile =  args.inputfile
    secondinputfile = file(inputfile.name, 'r') # the buffer

    try:
        tree = ET.parse(inputfile)
    except ET.ParseError:
        print '%sEl archivo no es un XML válido o reconocible'%R
        exit(1)
    root = tree.getroot()

    filewidth = int(root.attrib['width'])
    fileheight = int(root.attrib['height'])

    sizes = args.exportsize or [filewidth]

    color = args.color
    basecolor = args.basecolor

    tmpfilename = 'tmp' + str(uuid1())[-6:] + '.svg'

    if color.base_string != basecolor:
        with open(tmpfilename, 'w') as tmpFile:
            while True:
                line = secondinputfile.readline()
                if line:
                    newLine = line.replace(str(basecolor), str(color))
                    tmpFile.write(newLine)
                else:
                    break

    if args.output:
        output = args.output
    else:
        output = '.'.join(inputfile.name.split('.')[:-1])+'.png'

    for s in sizes:
        if not os.path.isdir('build/'+str(s)):
            os.mkdir('build/'+str(s))
        subprocess.check_call(
            [
                'inkscape',

                '-e', output,

                '-w', str(s),
                '-h', str(s*(fileheight/filewidth)),

                tmpfilename
            ]
        )

    if os.path.isfile(tmpfilename):
        os.remove(tmpfilename)