#!/usr/bin/env python3
#
#  git_consolidate.py
#
#  This will:
#       - tag where we are as something like 'autotag_001'
#       - create a new branch like 'consolidated_001'
#       - That new branch will be the consolidated change since the source_point
#
#  Example of operation:
#
#   From branch 'feature_99_work', invoke with:
#
#   $git_consolidate master -m 'Checkin of complete feature 99'
#
#   After tetermining names, etc., will perform the following:
#
#      git branch consolidated_001
#      git checkout consolidated_001
#      git reset --soft master
#      git commit -m "Checkin of complete feature 99 - consolidation of autotag_001"
#      git checkout feature_99_work
#      git tag autotag_001

import sys,subprocess

def exit_fail( msg ):
    print( "FAIL: %s" % msg )
    exit()

def run( cmd ):
   p  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) 
   return( p.returncode,  p.stdout.decode( "utf-8" ),  p.stderr.decode( "utf-8" )  )

# run a command like normal, but abort if the return value indicates an error
# we don't worry about stderr because that is used in normal git operations that succeed
def run_git_cmd( cmd ):
    rr,oo,ee = run( cmd )
    if rr!=0:
        print('cmd:',cmd)
        print('rr:',rr)
        print('oo:',oo)
        print('ee:',ee)
        exit_fail( 'git command filed' )
    return rr,oo,ee

#  Check on the availability of tag names and return the to-be-used tag and branch names
#
#  formatters will be a dict like:
#  {
#    'tagname'    : 'autotag_%03d',
#    'branchname' : 'consolitation_%03d',
#  }
#  return will be a dict like:
#  {
#    'tagname'    : 'autotag_001',
#    'branchname' : 'consolitation_001',
#  }
def get_needed_names(  formatters  ):
    rr,oo,ee = run_git_cmd( 'git tag' )
    tags = oo.splitlines()

    # first autogenerated tag name will be like 'autotag_001'
    ix=1      
    while True:
        tagname = formatters['tagname']%ix
        if tagname not in tags:
            break
        ix+=1

    rval={
        'tagname'    : formatters['tagname']%ix,
        'branchname' : formatters['branchname']%ix,
    }
    return rval

# executes 'git branch'
# looks for a line like '* thebranch' to determine the present branch
#  in this example, returns 'thebranch'
def get_present_branch():
    rr,oo,ee = run_git_cmd( 'git branch' )
    lines=oo.splitlines()
    for line in lines:
        if line.startswith('*'):
            present_branch = line.split()[-1]
            return( present_branch )
    return( None )

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

    names = get_needed_names( {'tagname': 'autotag_%03d', 'branchname': 'consolitation_%03d' } )

    autotag_name = names['tagname']
    new_branch_name = names['branchname']
    present_branch = get_present_branch()
    commit_message += ' - consolidation of %s' % autotag_name

    print( "Perfomring git operations ..." )
    run_git_cmd( 'git branch %s'       % new_branch_name );
    run_git_cmd( 'git checkout %s'     % new_branch_name );
    run_git_cmd( 'git reset --soft %s' % source_point    );
    run_git_cmd( 'git commit -m "%s"'  % commit_message  );
    run_git_cmd( 'git checkout %s'     % present_branch );
    run_git_cmd( 'git tag %s'          % autotag_name );
    print( "done!" )

if __name__ == '__main__':
    main()
