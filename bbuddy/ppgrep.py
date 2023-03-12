#!/usr/bin/env python3
'''
ppgrep.py
(c) 2020-2022 Dick Justice
Released under MIT license.
'''

import sys
import os
from pathlib import Path

PPGREP_VER='0.0.006'

RED="\033[1;31m"
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
RESET="\033[0;0m"
BOLD="\033[;1m"
BLUE="\033[1;34m"
MAGENTA="\033[1;35m"
BOLD_YELLOW  = "\033[1;33m"
BOLD_RED=  "\033[1;31m"


def problem(msg):
    print(f"{YELLOW}###{RESET} {msg}")

def colorize_it( name, what, pre=BOLD_RED, post=RESET  ) -> str:
    '''
    for all instantes of 'what' in 'name',
    replace the 'what' with {pre}{what}{post}
    returns the new string
    '''
    parts = name.split( what )
    jval = f"{pre}{what}{post}"
    return jval.join( parts )

def does_it_match( file, what ) -> bool:
    if what=='*':
        mval = ''
        matches = True
    elif what.startswith( '*' ) and what.endswith( '*' ):
        mval = what[1:-1]
        matches = mval in file

    elif what.startswith( '*' ):        # Example:  *.py
        mval = what[1:]
        matches = file.endswith( mval )

    elif what.endswith( '*' ):          # example: sammy*
        mval = what[:-1]
        matches = file.startswith( mval )
    else:
        # exact match required
        mval = what
        matches = file==mval
    return matches


def directory_is_excluded( root, d, exclude_dirs ) -> bool:
    for exx in exclude_dirs:
        if '/' in exx:
            if os.path.abspath(root+'/'+d) == os.path.abspath(exx):
                return True
        else:
            if d==exx:
                return True
    return False


def usage_bail():
    print( f"{sys.argv[0]} v {PPGREP_VER}" )
    print(  "Usage: ppgrep <what> [fn_match] [fn_match_2] .." )
    print(  "   Recursively searches for string <what> in files under local dir" )
    print(  "   If 'fn_match' not spcified, searches all files (uses '*') ")
    print(  "If file '.exclude' is present at any level, it excludes its listed folders")
    sys.exit(1)


def main():
    argv=sys.argv
    if len(argv)<2:
        usage_bail()

    what = argv[1]
    fn_match_list=[]

    fn_match_args = argv[2:]
    if len(fn_match_args)>0:
        for arg in fn_match_args:
            fn_match_list.append( arg )
    else:
        fn_match_list.append( '*' )

    exclude_dirs=[]
    searchfiles=[]
    for root, dirs, files in os.walk('.'):
        if '.exclude' in files:
            with open(root+'/.exclude', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                strippedline = line.strip()
                if len(strippedline)>0 and not strippedline.startswith( '#' ):
                    exclude_dirs.append( root+'/'+strippedline  )

        newdirs=[]
        for d in dirs:
            if not directory_is_excluded( root, d, exclude_dirs):
                newdirs.append(d)
        dirs[:] = newdirs

        for file in files:
            for where in fn_match_list:
                if does_it_match( file, where ):
                    searchfiles.append( (Path(root).as_posix() +'/'+ file) )


    for fn in searchfiles:
        if os.path.exists(fn):
            try:
                with open(fn,'rb') as f:
                    contents = f.read()
            except PermissionError as _:
                problem( f"No Permission to read: {fn}")
                continue
            except Exception as e:
                print( f"could not read {fn}: {str(e)}")
                continue
            lines_bin = contents.splitlines()
            for ix,line_bin in enumerate( lines_bin ):
                try:
                    line = line_bin.decode( 'utf-8')
                    if what in line:
                        #print( "%s (%d): %s" % (fn, ix+1,   colorize_it(line,what)  ))
                        print( f"{fn} ({ix+1}): {colorize_it(line,what)}" )
                except Exception as _:
                    #most of the time, no desire to print here.
                    #zip, binaries, etc cause issues
                    #print( "problem decoding in '%s'" % fn )
                    pass
    if len(exclude_dirs)>0:
        xdirs = [  Path(x).as_posix()+'/' for x in exclude_dirs ]
        print( "Note: These dirs excluded from search:",', '.join(xdirs) )


if __name__ == '__main__':
    main()
