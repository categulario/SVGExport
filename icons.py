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

    parser.add_argument("inputfile", type=argparse.FileType('r'), help="SVG file")
    parser.add_argument("-s", "--size",         type=int, help="Medida del cuadrado que rodea cada ícono, by default is the gcd of the SVGs with and height")
    parser.add_argument("-c", "--color",        type=Color, default="000000", help="New color for the icons")
    parser.add_argument("-b", "--basecolor",    type=Color, default="000000", help="Current color of the icons")
    parser.add_argument("-d", "--defaultname",  type=str,   default="image",  help="Default name for exported images")
    parser.add_argument("-o", "--output",       type=str,   default="./",     help="Output folder (won't be created, should exist previously)")
    parser.add_argument("-e", "--exportsize",   type=int,   action='append',  help="Sizes to wich export the icons")
    parser.add_argument("-f", "--files",        action="store_true",          help="Create only files instead of folders (the size is part of the filename)")
    parser.add_argument("-n", "--namesfile",    type=argparse.FileType('r'),  help="Names file for the icons, a normal txt file with a name per line, assigned from top to bottom and from left to right")

    args = parser.parse_args()

    inputfile =  args.inputfile
    secondinputfile = open(inputfile.name, 'r') # the buffer

    try:
        tree = ET.parse(inputfile)
    except ET.ParseError:
        print('%sEl archivo no es un XML válido o reconocible'%R)
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

    build_dir = os.path.join(args.output, 'build')
    if not os.path.isdir(build_dir) and not args.files:
        os.mkdir(build_dir)

    for i in range(0, filewidth//size):
        for j in range(fileheight//size-1, -1, -1):
            curname = next(namesgenerator)
            for s in sizes:
                size_dir = os.path.join(args.output, 'build', str(s))
                if not os.path.isdir(size_dir) and not args.files:
                    os.mkdir(size_dir)

                if args.files:
                    output = os.path.join(args.output, curname+'_'+str(s)+'.png')
                else:
                    output = os.path.join(args.output, 'build', str(s), curname+'.png')

                subprocess.check_call(
                    [
                        'inkscape',

                        '-e', output,

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