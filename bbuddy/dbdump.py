#!/usr/bin/env python3
"""
dbdummp.py - code to dump an sqlite database file

(c) 2022 Dick Justice
Released under MIT license.

"""
import os
import sys
import sqlite3
import textwrap

#pylint: disable=C0209 #(consider-using-f-string)


DBDUMP_VER = '0.0.002'

VERB_SILENT  = 0
VERB_TERSE   = 1
VERB_NORMAL  = 2
VERB_VERBOSE = 3
VERB_DEBUG   = 4

RED     = "\033[1;31m"
YELLOW  = "\033[0;31m"
RESET   = "\033[0;0m"

def err_msg( msg ):
    print( RED+"Err"+RESET+": "+msg )

def get_table_all_column_names(  curs, table_name ):
    cmd =  "select * from %s;" % table_name
    cursor = curs.execute( cmd )
    names = list( map( lambda x: x[0], cursor.description ))
    return names


def field_descr( colval, shorten_long_strings=False, width=80 ):
    tname = type(colval).__name__
    if tname == 'str':
        if shorten_long_strings:
            descr = "'%s'" %  textwrap.shorten(colval, width=width)
        else:
            descr = "'%s'" % colval
    elif tname == 'int':
        descr = "%d" % colval
    elif tname == 'float':
        descr = "%f" % colval
    elif tname == 'bytes':
        descr = "%d bytes" % len(colval)
    elif tname == 'NoneType':
        descr = 'nonetype?'
    else:
        print( "unrecog type '%s'\n"%  tname )
        sys.exit(1)
    return descr


def dump_db_row( row, cnt, start='', printrownum=True, width=80,
        verb=VERB_NORMAL, longlinehandle='wrap' ):
    if verb>=VERB_DEBUG:
        print( "raw row:", row )

    linestart = '  '
    if printrownum:
        linestart += 'Row %d: ' % (cnt)
        #linestart += '%sRow %d%s: ' % (BOLD,cnt,RESET)
    ix=0

    vals =[]
    for colval in row:
        descr = field_descr(colval, width=width)
        vals.append( descr)
        ix+=1
    line = linestart + ', '.join(vals)

    if longlinehandle=='wrap':
        wrappedlines = textwrap.wrap( line, width=width, subsequent_indent='    ' )
        for ll in wrappedlines:
            print( start + ll )
    elif longlinehandle=='shorten':
        ll = textwrap.shorten(line, width=width, placeholder=" ...")
        print( '  ' + start + ll )  #textwrap.shorten() removes spaces so we add them back

    elif longlinehandle=='clamp':
        if len( line ) > width:
            line = line[0:width-4] + ' ...'
        print( start + line )

    else:
        print( line )

def dump_db_table( c, table_name, start='', width=80, names_of_columns_to_get=None,
         max_lines_to_get=0, longlinehandle='wrap' ):
    #line = "Table '%s': " % (BOLD+table_name+RESET)
    line = "Table '%s': " % (table_name)

    if names_of_columns_to_get is None:
        names_of_columns_to_get=[]

    if len(names_of_columns_to_get)>0:
        colnames = names_of_columns_to_get
    else:
        colnames = get_table_all_column_names(  c, table_name )

    #print( "colnames:", colnames)

    #colnames = ('user_id','user_name')
    fetch_rowid=False
    if table_name.startswith('msgs'):
        fetch_rowid=True


    if fetch_rowid:
        colnames.append( 'ROWID')
    collist = ', '.join(colnames)

    line += "Col names: %s. " % collist

    if max_lines_to_get==0:
        cmd = "select %s from %s;" % (collist,table_name)
    else:
        cmd = "select %s from %s where ROWID<=%d;"%(collist,table_name, max_lines_to_get)

    try:
        _ = c.execute( cmd)
        cc  = c.fetchall()

        line += "nrows: %d"% len(cc)
        wrappedlines = textwrap.wrap( line, width=width, subsequent_indent='    ' )
        for ll in wrappedlines:
            #print( start + ll )
            print( ll )

        cnt=0
        for row in cc:
            dump_db_row(row, cnt, start=start, width=width, longlinehandle=longlinehandle)
            cnt+=1
    except Exception as e:
        err_msg( f"A db access error occurred: {e}")
        print( "TODO: figure out how to print real complaint")

    #print( "db table access done")
    return()


def db_fetch_all_table_names_fetchall( c, verb=VERB_NORMAL ):
    c.execute( "select name from sqlite_master where type = 'table';" )
    t = c.fetchall()
    alltables=[]
    for row in t:
        tname = row[0]
        alltables.append( tname )
        if verb >= VERB_DEBUG:
            print( row )
    return alltables

#  same as other one, but using fetchone()
def db_fetch_all_table_names_using_fetchone( c, verb=VERB_NORMAL ):
    c.execute( "select name from sqlite_master where type = 'table';" )
    alltables=[]
    done = False
    while not done:
        row = c.fetchone()
        if row is None:
            done=True
        else:
            tname = row[0]
            alltables.append( tname )
            if verb >= VERB_DEBUG:
                print( row )
    return alltables

def db_fetch_all_table_names( c, verb=VERB_NORMAL ):
    return db_fetch_all_table_names_using_fetchone(c,verb)




# valid values for:
#   id_table_name          |  Meaning
#  ------------------------+--------------------------------------
#   '_all_tables_'         |  all tables, default
#   '_table_with_num_ num' |  table specified by index number num
#    other                 |  table specified by name

def db_dump( fn_db, start='', top_lev_only=False, id_table_name="_all_tables_",
        verb=VERB_NORMAL, specified_column_names=None, max_table_lines=0,
        longlinehandle='wrap', width=80 ):
    print( "dump_db:" )

    if specified_column_names is None:
        specified_column_names=[]

    conn = sqlite3.connect( fn_db )
    c = conn.cursor()
    report_all_tables = False

    id_table_num = -1  #default, meaning all
    if id_table_name == '_all_tables_':
        report_all_tables = True
    elif id_table_name.startswith( '_table_with_num_' ):
        id_table_num = int(id_table_name.split()[1])
    else:
        id_table_num = -2   #meaning specified by name

    alltables = db_fetch_all_table_names( c, verb=verb)

    bad_table=False
    if id_table_num==-2:
        for ix in range( len(alltables) ):
            if id_table_name == alltables[ix]:
                id_table_num = ix
        if id_table_num <0:
            print( RED+"Error"+RESET+": ", end='' )
            print( "Table named '%s' not in database! " % id_table_name )
            bad_table=True
    if id_table_num >= len(alltables) :
        print( RED+"Error"+RESET+": ", end='' )
        print( "Table number (%d) too big. must be less than %d !" %
            (id_table_num,len(alltables) ) )

    if verb>=VERB_NORMAL or bad_table:
        ix=0
        ddd=[]
        for tblname in alltables:
            descr = '%s(%d)' % (tblname, ix)
            ddd.append( descr)
            ix+=1

        tablestring=  "Tables in db: " + ', '.join(ddd)
        #longlinehandle='wrap'
        if longlinehandle=='full':
            print( tablestring )
        else:
            #width=60
            print( "-" * width )
            wrappedlines = textwrap.wrap(tablestring, width=width, subsequent_indent='  ')
            for ll in wrappedlines:
                print( start + ll )

    if bad_table:
        return

    if top_lev_only:
        return

    for i in range( len( alltables) ):
        table_name = alltables[i]
        if report_all_tables or (i==id_table_num):

            #print( "- "* int(width/2))
            ttt = YELLOW + "Table %d"%i + RESET
            print( "== %s : '%s'" % (ttt,table_name))
            dump_db_table( c, table_name, start=start,
                names_of_columns_to_get  = specified_column_names,
                max_lines_to_get=max_table_lines,
                longlinehandle=longlinehandle,
                width=width
                )
            print( "== Table %d END ==" % i)

    conn.close()

def dump_db_incoming( receiver_name, receiver_color, from_text, fn_db ):
    print('⌐' + '-'*30)
    print('| ' + from_text + " --> " +receiver_color+ receiver_name + RESET +": ", end='')
    db_dump( fn_db, start='| '  )
    print('⌙' + '-'*30)

def dump_db_outgoing( sender_name, sender_color, to_text, fn_db ):
    print('⌐' + '-'*30)
    print('| ' + sender_color + sender_name +RESET+ " --> "+to_text +": ", end='')
    db_dump( fn_db, start='| ' )
    print('⌙' + '-'*30)

#pylint: disable=C0301 #(line-too-long)
def usage_bail():
    cmd = sys.argv[0]
    print( "%s v %s - tool to dump an sqlite database" % (cmd,DBDUMP_VER) )
    print( "usage: %s fn [more]" % cmd )
    print( "  extra options:")
    print( "    -top           : show top level only"    )
    print( "    -table TBL     : table index number or its name"    )
    print( "    -col FIELDNAME : table column name to get. May be multiple of these"    )
    print( "    -mtl num       : specify maximum entries per table to display")
    print( "    -wrap*, -full, -shorten, -clamp:  for each row in a database, how to handle long lines"  )
    print( "         -wrap is default, showing all data with human readable presentation"  )
    print( "         -full shows all data using long lines per table line"  )
    print( "         -shorten and -clamp reduce the data shown"  )
    print( "    -width num     : width of display in characters.  Overrides window width.")
    sys.exit(1)
#pylint: enable=C0301 #(line-too-long)
#=======================================

# valid values for:
#   id_table_name          |  Meaning
#  ------------------------+--------------------------------------
#   '_all_tables_'         |  all tables, default
#   '_table_with_num_ num' |  table specified by index number num
#    other                 |  table specified by name

def main():
    argv=sys.argv
    top_lev_only=False
    if len(argv)<2:
        usage_bail()
    fn_db =  argv[1]
    specified_column_names = []
    max_table_lines=0

    id_table_name = '_all_tables_'
    working_on_table=False
    working_on_col=False
    working_on_mtl=False
    working_on_width=False
    longlinehandle='wrap'

    # if all else fails, assume hte widht is 80 chars
    width=80

    # if we can read the console's width, subtract 5 and use that
    # pad it a little bit because of special characters
    _, columns = os.popen('stty size', 'r').read().split()
    ccc = int(columns)
    if ccc>10 and ccc<1000:
        width=ccc-5


    for arg in argv[2:]:
        if working_on_table:
            try:
                xxx=int(arg)
                id_table_name= '_table_with_num_ %d' % xxx
            except Exception as _:
                id_table_name=arg
            working_on_table=False
        elif working_on_col:
            specified_column_names.append( arg )
            working_on_col=False
        elif working_on_mtl:
            working_on_mtl=False
            max_table_lines=int(arg)
        elif working_on_width:
            width = int(arg)
            working_on_width=False
        else:
            if arg=='-top':
                top_lev_only=True
            elif arg=='-table':
                working_on_table=True
            elif arg=='-col':
                working_on_col=True
            elif arg=='-mtl':
                working_on_mtl=True
            elif arg=='-wrap':
                longlinehandle='wrap'
            elif arg=='-shorten':
                longlinehandle='shorten'
            elif arg=='-clamp':
                longlinehandle='clamp'
            elif arg=='-full':
                longlinehandle='full'
            elif arg=='-width':
                working_on_width=True
            else:
                usage_bail()
    if working_on_col:
        err_msg( "arg must follow -col" )
        usage_bail()
    if working_on_table:
        err_msg( "arg must follow -table" )
        usage_bail()

    if not os.path.exists( fn_db ):
        print( "file '%s' does not exist" % fn_db )
        sys.exit(1)

    db_dump( fn_db, top_lev_only=top_lev_only, id_table_name=id_table_name,
        specified_column_names=specified_column_names,
        max_table_lines=max_table_lines, longlinehandle=longlinehandle, width=width)

if __name__ == "__main__":
    main()
