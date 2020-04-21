#!/usr/bin/env python3
import sys,os,time,subprocess
from datetime import datetime
from pathlib import Path

PPGREP_VER='0.0.001'

RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m";MAGENTA="\033[1;35m"
BOLD_YELLOW  = "\033[1;33m"
BOLD_RED=  "\033[1;31m"

#
#
#
def colorize_it( file, what  ):
   parts = file.split( what )
   jval = BOLD_RED + what + RESET
   rval = jval.join( parts )
   return( rval )

def does_it_match( file, what ):
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
   return( matches )



def usage_bail():
   print( "ppgrep v %s"% PPGREP_VER )
   print( "Usage: ppgrep <what> [fn_match] [fn_match_2] .." )
   print( "   Recursively searches for string <what> in files under local dir" )
   print( "   If 'fn_match' not spcified, searches all files (uses '*') ")
   exit()

def main( argv ):
   if len(argv)<2:
      usage_bail()

   what = argv[1]
   wherelist=[]

   where_args = argv[2:]
   if len(where_args)>0:
      for arg in where_args:
         wherelist.append( arg )
   else:
      wherelist.append( '*' )


   searchfiles=[]
   for root, dirs, files in os.walk('.'):
      root_good = Path(root).as_posix()   #deal with windows paths

      for file in files:
         for where in wherelist:
            if does_it_match( file, where ):
               searchfiles.append( (root +'/'+ file) )

   #print( "matching files:", searchfiles)

   for fn in searchfiles:
      if os.path.exists(fn):
         f=open(fn,'rb')
         contents=f.read()
         f.close()
         lines_bin = contents.splitlines()
         for ix,line_bin in enumerate( lines_bin ):
            try:
               line = line_bin.decode( 'utf-8')
               if what in line:
                  print( "%s (%d): %s" % (fn, ix+1,   colorize_it(line,what)  ))
            except:
               #most of the time, no desire to print here. zip, other binaries, etc cause issues
               #print( "problem decoding in '%s'" % fn )
               pass

if __name__ == '__main__':
   main( sys.argv )






