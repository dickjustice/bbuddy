#!/usr/bin/env python3
#
#  ppgrep.py
#
#  (c) 2020 Dick Justice
#  Released under MIT license.

import sys,os,time,subprocess
from datetime import datetime
from pathlib import Path

PPGREP_VER='0.0.005'

RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m";MAGENTA="\033[1;35m"
BOLD_YELLOW  = "\033[1;33m"
BOLD_RED=  "\033[1;31m"

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


def directory_is_excluded( root, d, exclude_dirs ):
   for exx in exclude_dirs:
      if '/' in exx:
         if os.path.abspath(root+'/'+d) == os.path.abspath(exx):
            return True
      else:
         if d==exx:
            return True
   return False


def usage_bail():
   print( "ppgrep v %s"% PPGREP_VER )
   print( "Usage: ppgrep <what> [fn_match] [fn_match_2] .." )
   print( "   Recursively searches for string <what> in files under local dir" )
   print( "   If 'fn_match' not spcified, searches all files (uses '*') ")
   print( "If file '.exclude' is present at any level, it excludes its listed directories")
   exit()

def main( argv ):
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
         with open(root+'/.exclude') as f:
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

      root_good = Path(root).as_posix()   #deal with windows paths

      for file in files:
         for where in fn_match_list:
            if does_it_match( file, where ):
               searchfiles.append( (Path(root).as_posix() +'/'+ file) )


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
   if len(exclude_dirs)>0:
      xdirs = [  Path(x).as_posix()+'/' for x in exclude_dirs ]   
      print( "Note: These dirs excluded from search:",', '.join(xdirs) )
if __name__ == '__main__':
   main( sys.argv )






