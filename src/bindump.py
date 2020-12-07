#!/usr/bin/env python3
#
#   bindump.py
#
#  (c) 2020 Dick Justice
#  Released under MIT license.

import sys
import os

def exit_fail( msg ):
    print( "FAIL: %s" % msg )
    exit()

def usage_bail():
    print( "usage: bindump [opts] fn [opts]")
    print( "Possible opts:" )
    print( "  -nb <bytes> : Dumps up to a number of bytes. 0 means full file." )
    print( "  -a : dump entire file.  Equivalient to '-nb 0' ") 
    print( "If no options are specified, prints first 256 bytes")
    exit()

#  if nb<=0, it means to print all of it
def dumpmem( contents, descr='data', nb=0 ):
    mode_all= True if nb<=0 else False

    if mode_all:
        print( "all %s:" % descr )
        nb_to_print = len(contents)
    else:
        if len(contents) <= nb:
            print( "all %s:" % descr )
            #print( "contents of entire file '%s':" % fn )
            nb_to_print = len(contents)
        else:
            print( "beginning of %s:" % descr )
            #print( "beginning of file '%s':" % fn )
            nb_to_print = nb

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
                if bval >=0x20 and bval <= 0x7e:
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
    return

def main( argv ):
    mode = 'mode_none'
    fn = None
    nb = 256

    for arg in argv[1:]:
        if mode=='mode_none':
            if arg=='-a':
                nb=0
            elif arg=='-nb':
                mode='mode_nb' 
            elif os.path.isfile( arg ):
                fn=arg
            else:
                print( "'%s' is neither an option nor a filename" % arg )
                usage_bail()
        elif mode=='mode_nb':
            try:
                nb = int( arg, 0 )
            except:
                exit_fail( "'%s' not convertable to int" )
            mode='mode_none'
        else:
            exit_fail( "illegal mdoe '%s'" % mode )
    if fn is None:
        print( "No file specified to dump" )
        usage_bail()            

    with open( fn, 'rb' ) as f:
        contents = f.read()

    dumpmem( contents, descr="file '%s'"%fn, nb=nb )
    return

#---------
if __name__ == "__main__":
    main( sys.argv)

