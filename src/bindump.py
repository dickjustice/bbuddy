#!/usr/bin/env python3
#
#   bindump.py
#
#  (c) 2020 Dick Justice
#  Released under MIT license.

import sys
import os
import struct

RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m";MAGENTA="\033[1;35m"

def dump_line_of_ints( ix0,memm, formatt ):
    print( "%3x: " % ix0, end='' )
    done=False
    for i in range(4):
        data=memm[4*i:4*i+4]
        if len(data)==4:
            v = struct.unpack( formatt, data )
            print( '%08x ' % v, end='' )
        elif len(data)>0:
            ss = ('??'*len(data)).ljust(9)
            print( ss,end='')
        else:
            print( ' '*9, end='' )
    print( '' )

def le_32s( ix0, memm ):
    dump_line_of_ints( ix0, memm, '<I' )

def be_32s( ix0, memm ):
    dump_line_of_ints( ix0, memm, '>I' )

#  dump up to 16 bytes of data as both hex and ascii
def dump_ascii_line( ix0, memm ):
    nb=len(memm)
    print( "%3x: " % ix0, end='' )
    for i in range(nb):
        bval = memm[i]
        print( "%02x " % bval, end='' )
    for i in range(nb,16):
        print( "   ", end='' )
    print( "| ", end='')
    for i in range(nb):
        bval = memm[i]
        if bval >=0x20 and bval <= 0x7e:
            bstr = memm[i: i+1]
            strr = bstr.decode( 'utf-8')
            print( strr, end='')
        else:
            print('.', end='')
    for i in range(nb,16):
        print( " ", end='')

    print( '')
    return()

#  if nb<=0, it means to print all of it
def dumpmem( contents, descr='data', nb=0, formatt=dump_ascii_line ):
    mode_all= True if nb<=0 else False

    if mode_all:
        print( "All %s:" % descr )
        nb_to_print = len(contents)
    else:
        if len(contents) <= nb:
            print( "all %s:" % descr )
            nb_to_print = len(contents)
        else:
            print( "beginning of %s:" % descr )
            nb_to_print = nb
    print( "chars to print:", nb_to_print)
    data_to_print = contents[ :nb_to_print]

    done=False
    ix0=0
    while not done:
        printline = data_to_print[:16]
        if len(printline)>0 :
            formatt( ix0,  printline )
            #dump_ascii_line( ix0,  printline )
        else:
            done=True
        ix0+=16
        data_to_print = data_to_print[16:] 

    return


def usage_bail():
    print( "usage: bindump [opts] fn [opts]")
    print( "Possible opts:" )
    print( "  -a  : dump entire file. Otherwise dumps first 256 bytes only" )
    print( "  -le : dump data as array of 32-bit LE ints" )
    print( "  -be : dump data as array of 32-bit BE ints" )
    exit()


def main( argv ):
    fn = None
    nb = 256
    formatt=dump_ascii_line 

    for arg in argv[1:]:
        if arg=='-a':
            nb=0
        elif arg=='-le':
            formatt=le_32s
            pass
        elif arg=='-be':
            formatt=be_32s
            pass

        elif os.path.isfile( arg ):
            fn=arg
        else:
            print( "'%s' is neither an option nor a filename" % arg )
            usage_bail()

    if fn is None:
        print( "No file specified to dump" )
        usage_bail()            

    with open( fn, 'rb' ) as f:
        bindata = f.read()

    dumpmem( bindata, descr="file '%s'"%fn, nb=nb, formatt=formatt )
    return

#---------
if __name__ == "__main__":
    main( sys.argv)

