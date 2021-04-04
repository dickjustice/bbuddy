#!/usr/bin/env python3
#
#  git_consolidate.py
#
#  This will:
#       - tag where we are as something like 'autotag_001'
#       - consolidate the difference from the source point to here'
#            and check in with passed message + extra info lines later
#

import sys,os,subprocess

def exit_fail( msg ):
    print( "FAIL: %s" % msg )
    exit()

def run( cmd ):
   p  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) 
   return( p.returncode,  p.stdout.decode( "utf-8" ),  p.stderr.decode( "utf-8" )  )

# run a command like normal, but abort if the return value indicates an error
# we don't worry about stderr because that is used in normal git operations that succeed
def run_git_cmd( cmd ):
    print( "| "+cmd )
    rr,oo,ee = run( cmd )
    if rr!=0:
        print('cmd:',cmd)
        print('rr:',rr)
        print('oo:',oo)
        print('ee:',ee)
        exit_fail( 'git command failed' )
    return rr,oo,ee


#  get the next free autotag name
#
#  formatter will be like: 'autotag_%03d'
#  swith     will be like: 'autotag'
#
#  returnval will be like: 'autotag_001'

def get_next_autotag_name( formatter, swith ):
    rr,oo,ee = run_git_cmd( 'git tag' )
    tags = oo.split()
    maxx=0;
    for tag in tags:
        if tag.startswith( swith ):
            try:
                val = int(  tag[ len(swith):  ] )
            except:
                val = 0
            if val>maxx:
                maxx=val

    rval= formatter%(maxx+1)
    return( rval )

# executes 'git branch' and parses to get curent branch
def get_present_branch():
    rr,oo,ee = run_git_cmd( 'git branch' )
    lines=oo.splitlines()
    for line in lines:
        if line.startswith('*'):
            return(  line.split()[-1]  )
    return( None )

def get_head_hash():
    rr,oo,ee = run_git_cmd( 'git rev-parse HEAD' )
    thehash = oo.split()[0]
    return( thehash )

def usage_bail():
    print('usage:')
    print("  git_consolidate source_point -m 'commit message'")  
    exit()

def main():
    argv=sys.argv
    if len(argv)!=4:
        usage_bail()

    source_point = argv[1]
    if argv[2]!='-m':
        usage_bail()
    commit_message = argv[3]

    autotag_name = get_next_autotag_name(  'autotag_%03d', 'autotag_' )
    present_branch = get_present_branch()
    head_hash = get_head_hash();

    fn_commit = '/tmp/commit_msg.txt'
    fd = open(fn_commit,'w')
    fd.write( commit_message+'\n\n')
    fd.write( 'Consolidated branch %s at terminus %s\n'%(present_branch,autotag_name)  )
    fd.write( '   with hash: %s\n'%head_hash)
    fd.close()

    run_git_cmd( 'git tag %s'          % autotag_name );
    run_git_cmd( 'git reset --soft %s' % source_point    );
    run_git_cmd( 'git commit -F %s'    % fn_commit  );

    os.remove( fn_commit )
    print( "done!" )

if __name__ == '__main__':
    main()
