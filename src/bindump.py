#!/usr/bin/env python3
#
#   bindump.py
#
#  (c) 2020 Dick Justice
#  Released under MIT license.

import sys
import os

def usage_bail():
    print( "usage: bindump [opts] fn [opts]")
    print( "Possible opts:" )
    print( "  -a : dump entire file. Otherwise dumps first 256 bytes only" )
    exit()

def main( argv ):
    mode_all = False
    fn = None

    for arg in argv[1:]:
        if arg=='-a':
            mode_all = True
        elif os.path.isfile( arg ):
            fn = arg
        else:
            print( "'%s' is neither an option nor a filename" % arg )
            usage_bail()

    if fn is None:
        print( "No file specified to dump" )
        usage_bail()            

    with open( fn, 'rb' ) as f:
        contents = f.read()

    if mode_all:
        print( "contents of entire file '%s':" % fn )
        nb_to_print = len(contents)
    else:
        if len(contents) <= 256:
            print( "contents of entire file '%s':" % fn )
            nb_to_print = len(contents)
        else:
            print( "beginning of file '%s':" % fn )
            nb_to_print = 256

    ix0 = 0;
    done=False
    while not done:
        print( "%3x: " % ix0, end='' )
        for i in range(16):
            ixx = ix0+i
            if ixx<nb_to_print:
                bval = contents[ixx]
                print( "%02x " % bval, end='' )
            else:
                print( "   ", end='' )
        print( "| ", end='')

        for i in range(16):
            ixx = ix0+i
            if ixx<nb_to_print:
                bval = contents[ixx]
                if bval >=0x20 and bval <= 0x7f:
                    bvalbinstr = contents[ixx: ixx+1]
                    str = bvalbinstr.decode( 'utf-8')
                    print( str, end='')
                else:
                    print( ".", end='')
            else:
                print( " ", end='')
        print( '')
        ix0+=16
        if ix0>= nb_to_print:
            done=True

#---------
if __name__ == "__main__":
    main( sys.argv)

