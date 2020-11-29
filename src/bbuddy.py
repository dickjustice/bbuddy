#!/usr/bin/env python3


import sys,os,subprocess,signal,json,threading,time


from PyQt5 import QtCore, QtWidgets, QtGui

from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, 
                             QLineEdit, QMessageBox, QTreeWidget , QLabel)

from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtGui import QFont

QString=type("")


VER='v0.0.02'


NUM_CMDS = 10
MS_PER_KEYSTROKE_MAX = 100
MS_TOTAL_MAX = 500


XDOTOOL = 'xdotool'
fn_settings_old     = os.environ['HOME']+'/.bbuddy.conf'
fn_settings_new = os.environ['HOME']+'/.bbuddy_settings.conf'
default_lines = [ "ls -l", "ps", "ps -e", 'pwd' ]


greens = { 'normal':'#65c974', 'hover':'#7de88d', 'pressed':'#bbdefb' }
oranges= { 'normal':'#ccc266', 'hover':'#f5eda6', 'pressed':'#bbdefb' }
blues  = { 'normal':'#6994f0', 'hover':'#93b2f5', 'pressed':'#bbdefb' }

purples = { 'normal':'#a884bd', 'hover' :'#c273f0', 'pressed':'#f54cb1', }

lavender='#f6b2f7'

whites      = { 'normal':'#ffffff' }
near_whites = { 'normal':'#cccccc' }



ButtonStyles = {
    '.dobtn'  : { 'color' :  greens,  },
    '.style_btn_ud'  : { 'color' :  oranges, },
    '.style_btn_lu'  : { 'color' :  purples, },     # lock/unlock buttons
    '.style_btn_undo_save'  : { 'color' :  blues, },
    '.style_status_val'    : { 'color'   :  blues, },
} 

def gen_style_sheet():
    ss = ''
    for style in ButtonStyles:
        color = ButtonStyles[style]['color']
        ss += '%s { background-color: %s; }\n' % (style,color['normal'])

        if 'hover' in color:
            ss += '%s:hover { background-color: %s; }\n' % (style,color['hover'])
        if 'pressed' in color:
            ss += '%s:pressed { background-color: %s; }\n' % (style,color['pressed'])

        ss += '%s[disabled=disabled],%s:disabled { background-color: %s; }\n' % (style,style,'#aaaaaa')
        ss += '%s[disabled=disabled],%s:disabled { color: %s; }\n' % (style,style,'#888888')

    ss += 'QLineEdit { background-color: #ffffff; }\n'
    ss += 'QLineEdit[readOnly="true"] { background-color: #fffefa; }\n'
    ss += 'QLineEdit[flashing="true"] { background-color: #e229f0; }\n'
   
    return( ss )


def run( cmd ):
   p  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE ) 
   return( p.returncode,  p.stdout.decode( "utf-8" ),  p.stderr.decode( "utf-8" )  )



def calc_ms_delay_per_key( sendcmd ):
   delay_ms = MS_PER_KEYSTROKE_MAX 
   if len(sendcmd)>0:
      delay_ms = MS_TOTAL_MAX/len(sendcmd)
      if delay_ms>MS_PER_KEYSTROKE_MAX:
         delay_ms=MS_PER_KEYSTROKE_MAX
   return( delay_ms )

def execute_do(  sendcmd ):
   delay_ms = calc_ms_delay_per_key(sendcmd) 
   bb_window_id = int(  run('%s getactivewindow' % XDOTOOL )[1] )
   run( "%s windowfocus %d"  % (XDOTOOL, window_id) )
   run( "%s type --delay %d '%s'"  % (XDOTOOL, delay_ms, sendcmd) )
   run( "%s key Return"  % (XDOTOOL) )
   run( "%s windowfocus %d"  % (XDOTOOL, bb_window_id) )
   run( "%s windowfocus %d"  % (XDOTOOL, window_id) )

def execute_do_async( sendcmd ):
   t = threading.Thread(target=execute_do, args=(sendcmd,), kwargs=None )
   t.start()


class BBuddyWidget(QWidget):
    AllRows = []
    AllBottomStuff = {}
    presently_locked=False

    def __init__(self):
        super().__init__()
        self.initUI()

    def set_button_enabled_state( self, btn, state ):
        btn.setEnabled(state)
        return

    def any_lines_have_changed( self ):
        for i,row  in enumerate(self.AllRows):
            if lines_as_saved[i] !=  row['entrywidget'].text():
                return True
        return False


    def refresh_the_bottom_buttons( self ):

        if fully_installed:
            havechanged=self.any_lines_have_changed()
            for name in ( 'undo', 'save' ):
                try:
                    btn = self.AllBottomStuff[name]
                    self.set_button_enabled_state( btn, havechanged )
                except:
                    pass
            # for now, we will bail if the lock/unlock buttons are disabled
            if 'lock' not in self.AllBottomStuff:
                return



            '''
            ub = self.AllBottomStuff[ 'unlock' ]
            unlock_btn_state = True if self.presently_locked else False
            self.set_button_enabled_state( ub['button'], unlock_btn_state,  ub['colors'] )
            lb = self.AllBottomStuff[ 'lock' ]
            lock_btn_state = True if (not self.presently_locked) and (not havechanged) else False
            self.set_button_enabled_state( lb['button'], lock_btn_state, lb['colors'] )
            '''

            '''
            for i in range( NUM_CMDS ):
                ee =  self.AllRows[i]['entrywidget']
                if self.presently_locked:
                    ee['disabledbackground'] =  yellowish
                    ee['disabledforeground'] =  black
                    ee['state'] = 'disabled'
                else:
                    ee['background'] =  white
                    ee['state'] = 'normal'
            
            '''
            ltext = 'LOCKED' if self.presently_locked else 'UNLOCKED'
            self.AllBottomStuff['lock_state_lbl'].setText( ltext )

        return

    def refresh_all_normal_rows( self ):
        if not fully_installed:
            return

        for ix,row in enumerate(self.AllRows):
            do_enabled=True;  up_enabled=True;  down_enabled=True
            e = row['entrywidget']
            if len( e.text() ) <=0:
                do_enabled=False
                down_enabled=False
                up_enabled=False
            if ix==0:
                up_enabled=False
            if ix==NUM_CMDS-1:
                down_enabled=False
            if self.presently_locked:
                down_enabled=False
                up_enabled=False
            self.set_button_enabled_state( row['upbtn'],   up_enabled   )
            self.set_button_enabled_state( row['downbtn'], down_enabled )
            self.set_button_enabled_state( row['dobtn'],   do_enabled   )

            '''
            style = '.style_entry_locked' if self.presently_locked else  '.style_entry_unlocked'
            e = row['entrywidget']
            prop = e.property( 'class')
            if ix==0:
                    print( "existing prop:", prop)
                    print( "new style:", style)        
            e.setProperty("class", style );
            '''
            
            #e.setProperty( "flashing", False )

            e.setReadOnly( self.presently_locked )
            e.setStyleSheet(self.GlobalStyleSheet)        




    def refresh_all_buttons( self ):
        self.refresh_the_bottom_buttons()
        self.refresh_all_normal_rows()

    # returns an array of bools where true means that value changed
    def execute_undo_changes( self ):
        rval=[]
        for i,row in enumerate(self.AllRows):
            e = row['entrywidget']
            was_different = True if e.text()!=lines_as_saved[i] else False
            rval.append(was_different)
            e.setText(  lines_as_saved[i] )
        return rval

    def execute_save( self ):
        global lines_as_saved
        lines=[ row['entrywidget'].text() for row in self.AllRows ]
        #print( "saving old format")
        with open( fn_settings_old, 'w' ) as f:
            for line in lines:
                f.write(  line+'\n' )
        #print( "saving new format")
        with open( fn_settings_new, 'w' ) as f:
            mysavedinfo = {
                'creator' : 'bbuddy v %s' % VER,
                'commands' : lines
            }
            f.write( json.dumps( mysavedinfo,indent=4 ) )
        lines_as_saved = lines



    def swap_entry_contents( self, ix0, ix1 ):
        try:
            e0 = self.AllRows[ix0]['entrywidget']
            e1 = self.AllRows[ix1]['entrywidget']
        except:
            #throw out the case where it is going off the rails
            return
        s0 = e0.text()
        s1 = e1.text()
        e1.setText( s0 )
        e0.setText( s1 )


    def blink_row( self, ix, nloops, secs ):  
        e = self.AllRows[ix]['entrywidget']
        for i in range(nloops):
            #e['flashing'] = True;
            e.setProperty( "flashing", True )

            time.sleep( 0.2 ) 
            #e['flashing'] = False;
            e.setProperty( "flashing", False )
            time.sleep( 0.2 ) 

        #e.setProperty( "flashing", True )
        print( "==done blinking==")
    def blink_row_async( self, ix,  nloops, secs ):
        t = threading.Thread(target=self.blink_row, args=(ix,nloops,secs), kwargs=None )
        t.start()

    # generic button click handler
    def btn_clicked(self, btn):
        sending_button = self.sender()
        fullname = str(sending_button.objectName())
        parts = fullname.split('_')
        base=parts[0]
        try:
            num = int(parts[1])
        except:
            num=0
        ix=num
        if base=='do':
            # this blinking does not presntly work
            #self.blink_row_async(ix, 2, 0.1)
            cmd = self.AllRows[ix]['entrywidget'].text()
            execute_do_async( cmd )
        elif base=='up':
            self.swap_entry_contents( ix, ix-1)
        elif base=='dn':
            self.swap_entry_contents( ix, ix+1)
        elif base=='lock':
            self.presently_locked=True
        elif base=='unlock':
            self.presently_locked=False
        elif base=='undo':
            whichdiff = self.execute_undo_changes()
            print( whichdiff)
            for j,chgd in enumerate(whichdiff):
                if chgd:
                    #blink_row_async(j, lavender, 1, 0.25)
                    pass

        elif base=='save':
            self.execute_save()

        else:
            print( "Unhandled '%s' %d"% (base,num))
        self.refresh_all_buttons()


    #---------------------------------------------
    #  begin of all gui creation code


    # common creation function for all buttons
    def gui_create_pb( self, usertext, id_, class_,  delta_width=0, delta_font_points=0 ):
        objname = id_
        btn =    QPushButton(  usertext,  objectName=objname )
        btn.setProperty("class", class_ );
        font = btn.font();
        font.setPointSize(   font.pointSize()+delta_font_points );
        btn.setFont(font);
        rect =  btn.fontMetrics().boundingRect(usertext)
        w = rect.width() + delta_width
        btn.setFixedWidth(w)
        btn.setStyleSheet(self.GlobalStyleSheet)        
        btn.clicked.connect(lambda:self.btn_clicked(btn) )
        return( btn )

    # create all the normal rows
    def gui_create_normal_row( self, id_row ):
        i=id_row

        hboxx = QHBoxLayout()
        hboxx.setSpacing(1) 
        hboxx.setContentsMargins(0,0,0,0)

        row_info={}
        btn = self.gui_create_pb( "DO", "do_%02d"%i, 'dobtn', delta_width=6, delta_font_points=-2 )
        row_info['dobtn']=btn
        hboxx.addWidget( btn )

        e1 = QLineEdit( lines_as_saved[i] )
        e1.setProperty("class", "style_entry_locked" );
        e1.setProperty("class", "style_entry_unlocked" );


        max_to_show = "this_is_a_very_log_command_indeed_with_many_characters"
        width = e1.fontMetrics().boundingRect(max_to_show).width()
        e1.setMinimumWidth( width )
        e1.setMaximumWidth( width )
        e1.setContentsMargins(0,0,0,0)
        row_info['entrywidget']=e1
        e1.textChanged.connect(self.refresh_all_buttons)

        e1.setStyleSheet(self.GlobalStyleSheet)        

        hboxx.addWidget( e1 )

        btn = self.gui_create_pb( '▲','up_%02d'%i, 'style_btn_ud',  delta_width=6, delta_font_points=-2 )
        row_info['upbtn']=btn
        hboxx.addWidget( btn )

        btn = self.gui_create_pb( '▼','dn_%02d'%i, 'style_btn_ud', delta_width=6,  delta_font_points=-2 )
        row_info['downbtn']=btn
        hboxx.addWidget( btn )

        self.AllRows.append( row_info )

        return( hboxx )

    # create all the bottom row
    def gui_create_btm_widget( self ):
        hbox_bottom = QHBoxLayout()
        hbox_bottom.setSpacing(2)

        hbox_bottom.addStretch(1)

        create_lock_unlock = True
        if create_lock_unlock:
            lbl = QLabel()
            lbl.setText( "UNLOCKED")
            self.AllBottomStuff['lock_state_lbl']=lbl

            #lbl.setProperty("class", "style_status_val" );
            #lbl.setStyleSheet(self.GlobalStyleSheet)        


            rect =  lbl.fontMetrics().boundingRect("UNLOCKED")
            lbl.setFixedWidth( rect.width() + 4)

            hbox_bottom.addWidget(lbl)

            btn = self.gui_create_pb( 'Lock','lock', 'style_btn_lu',  delta_width=6,  delta_font_points=2)
            self.AllBottomStuff['lock']=btn
            hbox_bottom.addWidget(btn)

            btn = self.gui_create_pb( 'Unlock','unlock', 'style_btn_lu',  delta_width=6,  delta_font_points=2)
            self.AllBottomStuff['unlock']=btn
            hbox_bottom.addWidget(btn)


        hbox_bottom.addStretch(2)
        btn = self.gui_create_pb( 'Undo','undo', 'style_btn_undo_save',  delta_width=6,  delta_font_points=2)
        self.AllBottomStuff['undo']=btn
        hbox_bottom.addWidget(btn)

        btn = self.gui_create_pb( 'Save','save', 'style_btn_undo_save',  delta_width=6,  delta_font_points=2)
        self.AllBottomStuff['save']=btn
        hbox_bottom.addWidget(btn)

        hbox_bottom.addStretch(1)

        lbl = QLabel()
        lbl.setText(VER)

        if False:
            # this should have worked (to push down the text) but didnt
            # TODO: come back and make work
            vboxxxx = QVBoxLayout()
            vboxxxx.addStretch(1)
            vboxxxx.addWidget(lbl)
            hbox_bottom.addWidget(vboxxxx)
        else:
            hbox_bottom.addWidget(lbl)

        return( hbox_bottom )        

    def timecnt(self):
        print( 'cnt = %d' % self.cnt )
        self.cnt+=1

        ix=0
        e = self.AllRows[ix]['entrywidget']
        if self.cnt & 1:
            e.setProperty( "flashing", True )
        else:            
            e.setProperty( "flashing", False )

    def starttimer(self):
        self.timer=QTimer()
        self.cnt=0
        self.timer.timeout.connect(self.timecnt)
        self.timer.start( 1000 )

    def initUI(self):
        global window_id, lines_as_saved,fully_installed;
        self.GlobalStyleSheet = gen_style_sheet()

        fontDB  = QtGui.QFontDatabase()
        fontDB.addApplicationFont(":/A Font Supporting Emoji.ttf");

        vbox = QVBoxLayout()
        vbox.setContentsMargins(4,3,4,3)    # l,t,r,b
        vbox.setSpacing(0)
        vbox.addStretch(1)

        for id_row in range(NUM_CMDS):
            hboxx = self.gui_create_normal_row( id_row )
            vbox.addLayout(hboxx)

        hbox_bottom = self.gui_create_btm_widget()
        vbox.addLayout(hbox_bottom)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setWindowTitle('bbuddy')
        self.show()
        fully_installed=True
        self.refresh_all_buttons()


def main():
    global window_id, lines_as_saved;

    rr,oo,ee=run('ps -af' )
    lines=oo.splitlines()
    for line in lines:
        if 'bbuddy' in line:
            #print( "LINE: %s" % line )
            pass

    rr,oo,ee=run('%s getactivewindow' % XDOTOOL )
    if len(ee)>0:
        print( "problem running xdotool" )
        print( "stderr:", ee )
        print( "try: sudo apt install xdotool" )
        exit()

    window_id = int(  oo )
    #print( "window_id = %d (0x%x)" % (window_id, window_id) )

    if os.path.exists( fn_settings_new ):
        #print( "Loading new settings from '%s'" % fn_settings_new )
        with open( fn_settings_new, 'r' ) as f:
            storedstuff = json.loads( f.read() )
            lines_as_saved = storedstuff['commands']

    elif os.path.exists( fn_settings_old ):
        print( "Loading old settings from '%s'" % fn_settings_old )
        with open( fn_settings_old, 'r' ) as f:
            contents =f.read()
        lines_as_saved = contents.splitlines()
    else:
        print( "No setings found. Using defautlts"  )
        lines_as_saved = default_lines

    # create empty lines if not enough as loaded
    for i in range( len(lines_as_saved), NUM_CMDS):
        lines_as_saved.append('')


    if os.fork()>0:  return

    # kill the app on ctrl-c, though not really important now that fork is running
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    # for more graceful options, see https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co

    app = QApplication(sys.argv)
    ex = BBuddyWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
