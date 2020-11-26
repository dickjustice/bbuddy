#!/usr/bin/env python3
import sys,os,subprocess,string
from pathlib import Path


RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m"

def run( cmd ):
   p  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) 
   rr = p.returncode 
   oo = p.stdout.decode( "utf-8" )
   ee = p.stderr.decode( "utf-8" )
   return(rr,oo,ee)

def convert_path_to_posix( the_path ):
   # replace backslashes with forward slashes
   pp = Path(the_path).as_posix()
   # replace "C:/" with "/c/" for example
   rval = pp
   for drive_letter in list( string.ascii_uppercase ):
      if pp.startswith(   drive_letter + ":/" ):
         rval =  '/' + drive_letter.lower() + pp[2:] 
   return rval

def choose_best_dir():
   system_is_linux=False
   try:
      uid = os.geteuid()
      yes_root = True if uid==0 else False
      system_is_linux=True
   except:
      # system is assumed to be windows
      pass

   if system_is_linux:
      path_parts = path.split( ':')
   else:
      path_parts = path.split( ';')

   # or windows, convert the backslash to forward slash and replace "C:/" with "/c/" 
   path_parts = [ convert_path_to_posix(pp) for pp in path_parts ]

   if system_is_linux:
      if yes_root:
            if dirr in path_parts:
               return dirr
      else:
         for dirr in (  home+'/.local/bin', home+'/bin' ):
            if dirr in path_parts:
               return dirr
   else:
      for dirr in ( home+'/bin', '/usr/local/bin', '/usr/bin' ):
         if dirr in path_parts:
            return dirr
   return ''

def usage_bail():
   print( "Usage: ./install.py <dir> | auto" )
   print( "If <dir> is specified, install to that.")
   print( "If 'auto' is passed, install it to the best directory, determined automatically.")
   print( "If installing on linux:")
   print( "  As normal (non-root) user:")
   print( "    auto will try to install to $HOME/.local/.bin then $/home/bin")
   print( "  As root/sudo user:")
   print( "    auto will try to install to /usr/local/bin then /usr/bin")
   print( "If installing on windows:" )
   print( "    auto will try to install to $HOME/bin then /usr/local/bin then /usr/bin" )

   bestdir = choose_best_dir()
   if len(bestdir)>0:
      print( "Execute "+BOLD+"./install.py auto"+RESET+" now to install into: %s" % bestdir )
   else:
      print( "Not able to determine a valid location for automatic install.")
   exit()

def main( argv ):
   global path,home
   try:
      path = os.environ.get('PATH')
      home = os.environ.get('HOME')
      home = convert_path_to_posix( home )
   except:
      print( "'PATH' and 'HOME' environment variables must be defined." )
      exit()

   if len(argv)!=2:
      usage_bail()


   if argv[1]=='auto':
      dest_dir = choose_best_dir()
      if len(dest_dir)==0:
         print( "Unable to choose a destination dir automatically." )
         exit()
   else:
      dest_dir = argv[1]
      if not os.path.isdir( dest_dir ):
         print( "'%s' is not a directory.  Cannot install." % dest_dir )
         exit()

      path_parts = path.split( ':')
      if dest_dir not in path_parts:
         print( "Warning: directory '%s' is not in the PATH" % dest_dir )

   print( "installing to '%s/' ..." % dest_dir )
   dir_src = 'src'
   src_files = os.listdir( dir_src )
   print( "files:", src_files )


   for fn_src in src_files:
      fn_dest = fn_src[:-3] if fn_src.endswith( '.py' ) else fn_src


      cmd = "cp %s/%s %s/%s"  % (dir_src, fn_src, dest_dir, fn_dest)
      rr,oo,ee = run( cmd )
      print( "executing: '%s'" % cmd )
      if rr!=0 or len(ee)>0:
         print( "Failed msg:", ee )
         print( "Install aborted.")
   print( "Install done.")       

#---------
if __name__ == "__main__":
    main( sys.argv)


