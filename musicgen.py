# !/usr/bin/env python

import os
import random
import sys


NOTES = ['kick', 'snare', 'hihat']

for note in 'ABCDEFG':
    for octave in '234567':
        NOTES.append('%s%s' % (note, octave))


def r_get(seq):
    return seq[random.randint(0, len(seq) - 1)]


def r_list(seq, n):
    return [r_get(seq) for x in xrange(n)]


if __name__ == "__main__":
    filename = sys.argv[-2]
    length = int(sys.argv[-1])

    if os.path.exists(filename):
        print >> sys.stderr, 'File exists, overwriting'

    with open(filename, 'w') as out:
        for index in xrange(length):
            note = r_get(NOTES)
            out.write(note)
            if index + 1 < length:
                if (index + 1) % 12 == 0:
                    out.write('\n')
                else:
                    out.write(' ')
