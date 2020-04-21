#!/usr/bin/env python3
#
#   fffind.py
#
#  (c) Dick Justice
#  Released under MIT license.  See LICENSE.txt

import sys,os,subprocess

FFFIND_VER = '0.0.001'


RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m"
BOLD_YELLOW  = "\033[1;33m"
BOLD_RED=  "\033[1;31m"

def run( cmd ):
   checkprocess  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE  )  
   rr = checkprocess.returncode 
   oo = checkprocess.stdout.decode( "utf-8" )
   ee = checkprocess.stderr.decode( "utf-8" )
   return(rr,oo,ee)

def colorize_it( file, what  ):
   parts = file.split( what )
   jval = BOLD_RED + what + RESET
   rval = jval.join( parts )
   return( rval )

def does_it_match( file, what ):
   if what.startswith( '*' ) and what.endswith( '*' ):
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
   return( matches, mval )


def does_it_match_and_please_colorize( file, root, what, colorize=True ):
   matchs=False
   czd_file = 'xxx'

   matches, mval = does_it_match( file, what )

   fn_w_path =  root + '/' + file 

   if colorize:
      fn_w_path = colorize_it( fn_w_path, mval  );

   return matches, fn_w_path 


def directory_is_excluded( root, d, exclude_dirs ):
   for exx in exclude_dirs:
      if '/' in exx:
         if os.path.abspath(root+'/'+d) == os.path.abspath(exx):
            return True
      else:
         if d==exx:
            return True
   return False

def colorcode_it( file, what ) :
   file_new = file
   return( file_new )



def usage_bail():
   print( "fffind v %s" % FFFIND_VER )
   print( "Usage: fffind [-f|-d] [-bw] [-x dir] <what>")
   print( "  <what> may be like:" ) 
   print( "     abc   : is abc" ) 
   print( "     abc*  : starts with abc" ) 
   print( "     *abc  : ends with abc" ) 
   print( "     *abc* : contains abc" ) 
   print( "  options:" ) 
   print( "     -f     : files only" )
   print( "     -d     : directories only")
   print( "     -bw    : black and white output")
   print( "     -x dir : exclude this directory. may be used multpiple times")
   print( "              if dir contains '/', only the one instance is excluded" )
   print( "              otherwise, any dir with that name found is excluded" )
   exit()

def main( argv ):
   exclude_dirs = []
   report_files=True
   report_dirs= True
   colorize=True

   if len(argv)<2:
      usage_bail()

   what = argv[-1]
   opts = argv[ 1:-1 ]
   exclude_opt_next=False
   for opt in opts:
      if exclude_opt_next:
         exclude_dirs.append( opt )
         exclude_opt_next=False
      else:
         if opt=='-d':
            report_files=False
         elif opt=='-f':
            report_dirs=False
         elif opt=='-x':
            exclude_opt_next=True
         elif opt=='-bw':
            colorize=False
         else:
            print( "invalid option '%s'" % opt )
            usage_bail()

   #print( "----------")
   for root, dirs, files in os.walk('.'):
      newdirs=[]
      for d in dirs:
         if directory_is_excluded( root, d, exclude_dirs):
            pass
         else:
            newdirs.append(d)
      dirs[:] = newdirs

      if report_files:
         for file in files:
            matches, fn_czd = does_it_match_and_please_colorize( file, root, what, colorize=colorize )
            if matches:
               print( fn_czd )

      if report_dirs:
         for dirr in dirs:
            matches, dir_czd = does_it_match_and_please_colorize( dirr, root, what, colorize=colorize )
            if matches:
               print( dir_czd )

#---------
if __name__ == "__main__":
    main( sys.argv)

