#!/usr/bin/env python3
"""
bindump.py
(c) 2020 Dick Justice
Released under MIT license.
"""

import sys
import os
import struct


#pylint: disable=C0209 #(consider-using-f-string)

def dump_line_of_ints( ix0,memm, formatt ):
    print( "%3x: " % ix0, end='' )
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



def dump_line_of_int_64s( ix0,memm, formatt ):
    print( "%3x: " % ix0, end='' )
    for i in range(2):
        data=memm[8*i:8*i+8]
        if len(data)==8:
            v = struct.unpack( formatt, data )
            print( '%016x ' % v, end='' )
        elif len(data)>0:
            ss = ('??'*len(data)).ljust(17)
            print( ss,end='')
        else:
            print( ' '*17, end='' )
    print( '' )



def le_64s( ix0, memm ):
    dump_line_of_int_64s( ix0, memm, '<Q' )

def be_64s( ix0, memm ):
    dump_line_of_int_64s( ix0, memm, '>Q' )



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
def dumpmem( contents, descr=None, nb=0, formatt=dump_ascii_line ):
    mode_all= True if nb<=0 else False

    if mode_all:
        if descr is not None:
            print( "All %s:" % descr )
        nb_to_print = len(contents)
    else:
        if len(contents) <= nb:
            if descr is not None:
                print( "all %s:" % descr )
            nb_to_print = len(contents)
        else:
            if descr is not None:
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
        else:
            done=True
        ix0+=16
        data_to_print = data_to_print[16:]


def usage_bail():
    print( "usage: bindump [opts] fn [opts]")
    print( "Possible opts:" )
    print( "  -a    : dump entire file. Otherwise dumps first 256 bytes only" )
    print( "  -le   : dump data as array of 32-bit LE ints" )
    print( "  -be   : dump data as array of 32-bit BE ints" )
    print( "  -le64 : dump data as array of 64-bit LE ints" )
    print( "  -be64 : dump data as array of 64-bit BE ints" )
    sys.exit(1)


def main():
    fn = None
    nb = 256
    formatt=dump_ascii_line

    for arg in sys.argv[1:]:
        if arg=='-a':
            nb=0
        elif arg=='-le':
            formatt=le_32s
        elif arg=='-be':
            formatt=be_32s
        elif arg=='-le64':
            formatt=le_64s
        elif arg=='-be64':
            formatt=be_64s

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

#---------
if __name__ == "__main__":
    main()

