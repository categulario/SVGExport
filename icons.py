#!/usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import subprocess
import os
import xml.etree.ElementTree as ET
import re
from uuid import uuid1

#console colors
W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple
C  = '\033[36m' # cyan
GR = '\033[37m' # gray

def mcd(a, b):
    """máximo común divisor"""
    if b>a:
        a, b = b, a
    r = a%b
    if r == 0:
        return b
    else:
        return mcd(b, r)

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
    parser = argparse.ArgumentParser(description="Compila un archivo de iconos SVG en múltiples imágenes")

    parser.add_argument("inputfile", type=argparse.FileType('r'), help="Archivo a leer")
    parser.add_argument("-s", "--size", type=int, help="Medida del cuadrado que rodea cada ícono")
    parser.add_argument("-c", "--color", type=Color, help="Color para exportar los íconos", default="000000")
    parser.add_argument("-b", "--basecolor", type=Color, help="Color actual para cada ícono", default="000000")
    parser.add_argument("-n", "--namesfile", type=argparse.FileType('r'), help="Archivo de nombres de los íconos, asignados de arriba a abajo y de izquierda a derecha")
    parser.add_argument("-d", "--defaultname", type=str, help="Nombre por defecto para los archivos de imagen", default="image")
    parser.add_argument("-e", "--exportsize", type=int, help="Tamaños a los cuales exportar los íconos", action='append')

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

    if args.size:
        size = args.size
    else:
        size = mcd(filewidth, fileheight)

    sizes = args.exportsize or [size]

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

    namesfile = args.namesfile

    def names(nf):
        incremental = 1
        while True:
            if nf:
                nextname = nf.readline()
                if nextname.endswith('\n'): nextname = nextname[:-1]
                if nextname:
                    yield nextname
                else:
                    nf = None
                    yield args.defaultname+str(incremental)
                    incremental += 1
            else:
                yield args.defaultname+str(incremental)
                incremental += 1

    namesgenerator = names(namesfile)

    if not os.path.isdir('build'):
        os.mkdir('build')

    for i in range(0, filewidth/size):
        for j in range(fileheight/size-1, -1, -1):
            curname = namesgenerator.next()
            for s in sizes:
                if not os.path.isdir('build/'+str(s)):
                    os.mkdir('build/'+str(s))
                subprocess.check_call(
                    [
                        'inkscape',

                        '-e', os.path.join('build', str(s), curname+'.png'),

                        '-w', str(s),
                        '-h', str(s),

                        '-a',
                        '%d:%d:%d:%d'%(
                            i*size,
                            j*size,
                            (i+1)*size,
                            (j+1)*size,
                        ),

                        tmpfilename
                    ]
                )

    if os.path.isfile(tmpfilename):
        os.remove(tmpfilename)