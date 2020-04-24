#!/usr/bin/env python3
import sys,os,subprocess

Install_List = ( 'fffind', 'ppgrep', 'rreplace', 'bbuddy' )



RED="\033[1;31m"; YELLOW="\033[0;33m"; GREEN="\033[0;32m"; RESET="\033[0;0m"; BOLD="\033[;1m";BLUE="\033[1;34m"


def run( cmd ):
   checkprocess  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE  )  
   rr      = checkprocess.returncode 
   oo = checkprocess.stdout.decode( "utf-8" )
   ee = checkprocess.stderr.decode( "utf-8" )
   return(rr,oo,ee)

def am_i_root():
	return True if os.geteuid()==0 else False

def choose_best_dir( yes_root ):
	path_parts = path.split( ':')
	if yes_root:
		for dirr in ( '/usr/local/bin', '/usr/bin' ):
			if dirr in path_parts:
				return dirr
		return ''
	else:
		for dirr in (  home+'/.local/bin', '/usr/bin' ):
			if dirr in path_parts:
				return dirr
		return ''

def usage_bail():
	print( "Usage: ./install.py <dir> | auto" )
	print( "If <dir> is specified, install to that.")
	print( "If 'auto' is passed, install it to the best directory, determined automatically.")
	print( "  As normal (non-root) user:")
	print( "    auto will try to install to $HOME/.local/.bin then $/home/bin")
	print( "  As root/sudo user:")
	print( "    auto will try to install to /usr/local/bin then /usr/bin")
	bestdir = choose_best_dir(am_i_root())
	if len(bestdir)>0:
		print( "Execute "+BOLD+"./install.py auto"+RESET+" now to install into: %s" % bestdir )
	exit()

def main( argv ):
	global path,home
	try:
		path = os.environ.get('PATH')
		home = os.environ.get('HOME')
	except:
		print( "'PATH' and 'HOME' environment variables must be defined." )
		exit()

	if len(argv)!=2:
		usage_bail()


	if argv[1]=='auto':
		dest_dir = choose_best_dir(am_i_root())
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

	for program in Install_List:


		cmd = "cp %s.py %s/%s"  % (program, dest_dir, program)
		rr,oo,ee = run( cmd )
		print( "executing: '%s'" % cmd )
		if rr!=0 or len(ee)>0:
			print( "Failed msg:", ee )
			print( "Install aborted.")
	print( "Install done.")			


#---------
if __name__ == "__main__":
    main( sys.argv)


