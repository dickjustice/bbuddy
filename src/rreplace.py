#!/usr/bin/env python3
#
#   rreplace.py
#
#  (c) Dick Justice
#  Released under MIT license.

import sys,os,time,subprocess
from datetime import datetime
from pathlib import Path

RREPLACE_VER='0.0.001'

RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m";MAGENTA="\033[1;35m"
BOLD_YELLOW  = "\033[1;33m"
BOLD_RED=  "\033[1;31m"
BOLD_GREEN = "\033[1;32m"

#  returns the colorized version of the line (like froma grep)
def colorize_it( line, what  ):
   parts = line.split( what )
   jval = BOLD_RED + what + RESET
   rval = jval.join( parts )
   return( rval )

# returns (non-colored line, colored line)
def replace_in_line( line, text_from, text_to  ):
   try:
      parts = line.split( text_from )
      new_line = text_to.join( parts )
      green_text = BOLD_GREEN + text_to + RESET
      colored_new_line = green_text.join( parts )
   except Exception as e:
      print( "fixme")
      print( e )
      exit()
   return( new_line, colored_new_line )

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
   print( "rreplace v %s" % RREPLACE_VER )
   print( "Usage: rreplace [flags] <from> <to> [fn_match [fn_match_2] ..]" )
   print( "   fn_match may be like 'main.c', '*.py' 'abc*', '*xyz*', or '*'." )
   print( "   If 'fn_match' not spcified, uses '*'.")
   print( "   Values for flags:")
   print( "     -f  : force (i.e. complete the operation)")
   print( "           without -f (default): does not modify file. Only informs.")
   print( "     -v  : verbose mode")
   print( "Replaces all instances of <from> with <to>")
   exit()


def main( argv ):
   global force_mode, verbose_mode
   force_mode=False
   verbose_mode=False

   if len(argv)<3:
      usage_bail()
   args_left = argv[1:]

   done_with_flags=False
   while not done_with_flags:
      arg=args_left[0]
      if arg=='-f':
         force_mode=True
         args_left = args_left[1:]
      elif arg=='-v':
         verbose_mode=True
         args_left = args_left[1:]
      else:
         done_with_flags=True         

   text_from = args_left[0]
   text_to   = args_left[1]
   args_left = args_left[2:]

   wherelist=[]
   if len(args_left)>0:
      for arg in args_left:
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

   if verbose_mode:
      print( "files that will be searched:")
      print( searchfiles)
      print( '----------------')

   total_files=0; matched_files=0; changed_lines=0
   for fn in searchfiles:
      total_files+=1

      if os.path.exists(fn):
         f=open(fn,'rb')
         contents=f.read()
         f.close()

         lines_bin = contents.splitlines()
         lines_bin_new = []
         file_contained_matches=False
         for ix,line_bin in enumerate( lines_bin ):
            line_bin_new = line_bin

            try:
               line = line_bin.decode( 'utf-8')
               if text_from in line:
                  #print( "%s (%d): %s" % (fn, ix+1,   colorize_it(line,text_from)  ))

                  print( "%s (%d):" % (fn, ix+1) )
                  print( "   %s" % (colorize_it(line,text_from)) )
                  new_line, colored_new_line = replace_in_line( line, text_from, text_to )
                  print( "   %s" % colored_new_line )
                  file_contained_matches=True
                  changed_lines+=1

                  line_bin_new = new_line.encode( 'utf-8' )


            except:
               #most of the time, no desire to print here. zip, other binaries, etc cause issues
               #print( "problem decoding in '%s'" % fn )
               pass

            lines_bin_new.append( line_bin_new )

         if file_contained_matches:
            matched_files+=1
            print( "need to change '%s'" % fn)


            if verbose_mode:
               for line in lines_bin_new:
                  print( "   ", line )   

            if force_mode:
               print( "overwriting '%s'" % fn )
               f=open(fn,'wb')
               for line in lines_bin_new:
                  contents=f.write( line + b'\n' )
               f.close()
            else:
               print( "Not overwriting '%s'.  Use '-f' to force." % fn )
            print( '------------')

   print( "%d of %d files with %d lines matched" % (matched_files, total_files,  changed_lines) )
   exit()

if __name__ == '__main__':
   main( sys.argv )






