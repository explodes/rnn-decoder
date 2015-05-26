# !/usr/bin/env python

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import functools
import math
import os
import sys


EOF = ""
METHODS = ['encode2', 'decode2', 'image_encode', 'image_decode']


def opens_files(func):
    @functools.wraps(func)
    def wrapped(in_filename, out_filename):
        with open(in_filename, 'rb') as in_file:
            with open(out_filename, 'wb') as out_file:
                return func(in_file, out_file)

    return wrapped


def prefix(byte, lowcode, highcode):
    if byte > 127:
        return '%s%s' % (highcode, chr(byte - 128))
    else:
        return '%s%s' % (lowcode, chr(byte))


def read_value(in_file, lowcode, highcode):
    prefix = in_file.read(1)
    if prefix == EOF:
        return EOF

    byte = in_file.read(1)
    if byte == EOF:
        return EOF
    else:
        byte = ord(byte)

    if prefix == highcode:
        return byte + 128
    elif prefix == lowcode:
        return byte
    else:
        return None


def image_encode(in_filename, out_filename):
    from PIL import Image

    image = Image.open(in_filename)
    image.convert("RGB")
    width, height = image.size
    with open(out_filename, 'wb') as out_file:
        for w in xrange(width):
            for h in xrange(height):
                r, g, b = image.getpixel((w, h))
                out_file.write(prefix(r, 'r', 'R'))
                out_file.write(prefix(g, 'g', 'G'))
                out_file.write(prefix(b, 'b', 'B'))


def image_decode(in_filename, out_filename):
    from PIL import Image

    buffer = StringIO.StringIO()
    with open(in_filename, 'rb') as in_file:
        for line in in_file.xreadlines():
            buffer.write(line)

    num_bytes = buffer.tell()

    # 6 = (prefix byte + value byte) * (R + G + B)
    side_length = int(math.sqrt(num_bytes / 6))

    num_pixels = side_length * side_length

    image = Image.new("RGB", (side_length, side_length))
    pixels = image.load()

    buffer.seek(0)
    index = -1

    print 'NUM BYTES:', num_bytes
    print 'NUM PIXELS:', num_pixels
    print 'SIDE LENGTH:', side_length

    while index < num_pixels:
        index += 1
        r = read_value(buffer, 'r', 'R')
        if r == EOF:
            print 'R is EOF'
            break
        elif r is None:
            print 'R is None'
            r = 0
        g = read_value(buffer, 'g', 'G')
        if g == EOF:
            print 'G is EOF'
            break
        elif g is None:
            print 'G is None'
            g = 0
        b = read_value(buffer, 'b', 'B')
        if b == EOF:
            print 'B is EOF'
            break
        elif b is None:
            print 'B is None'
            b = 0

        px = (0xff << 24) | (r << 16) | (g << 8) | b

        print 'Pixel: ', index, side_length, divmod(index, side_length)

        x, y = divmod(index, side_length)
        pixels[x, y] = px

    image.save(out_filename, 'PNG')


@opens_files
def encode2(in_file, out_file):
    while True:
        char = in_file.read(1)
        if char == EOF:
            break
        byte = ord(char)
        out_file.write(prefix(byte, 'l', 'h'))


@opens_files
def decode2(in_file, out_file):
    while True:
        value = read_value(in_file, 'l', 'h')
        if value == EOF:
            break
        if value:
            out_file.write(chr(value))


def usage():
    print 'usage: <format> <infile> <outfile>'
    print
    print 'formats: %s' % ' '.join(METHODS)
    sys.exit(0)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()

    method = sys.argv[-3]  # encode or decode
    in_filename = sys.argv[-2]
    out_filename = sys.argv[-1]

    if method not in METHODS:
        usage()

    if not os.path.exists(in_filename):
        print >> sys.stderr, 'Input file does not exist'
        sys.exit(1)

    if os.path.exists(out_filename):
        print >> sys.stderr, 'Output file already exists, overwriting'

    func = globals()[method]
    func(in_filename, out_filename)

