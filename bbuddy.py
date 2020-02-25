#!/usr/bin/env python3
#
#   bbuddy.py
#
#  (c) Dick Justice
#  Released under MIT license.  See LICENSE.txt
#
import os,sys,subprocess,threading,time,copy
from tkinter import Tk, Label, Button, Frame, Entry, StringVar, font, END

NUM_CMDS = 10
MS_PER_KEYSTROKE_MAX = 100
MS_TOTAL_MAX = 500

XDOTOOL = 'xdotool'
fn_settings = os.environ['HOME']+'/.bbuddy.conf'
default_lines = ( "ls -l", "ps", "ps -e", 'pwd' )

blues  = { 'normal':'#6994f0', 'hover':'#93b2f5'}
greens = { 'normal':'#65c974', 'hover':'#7de88d'}
oranges= { 'normal':'#ccc266', 'hover':'#f5eda6'}
yellowish='#faf9f2'
white = '#ffffff'
black = '#000000'
pink = '#facfec'  #pale pink
lavender='#f6b2f7'

#---------------------
#  global data
window_id = 0;
fully_installed=False
presently_locked=False
BottomButtons = {}
all_rows=[]

def run( cmd ):
   checkprocess  = subprocess.run(  cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE  )  
   rr = checkprocess.returncode 
   oo = checkprocess.stdout.decode( "utf-8" )
   ee = checkprocess.stderr.decode( "utf-8" )
   return( rr, oo, ee )

def any_lines_have_changed():
   havechanged=False
   for i in range(NUM_CMDS):
      if init_lines[i] != all_rows[i]['entrywidget'].get():
         havechanged=True
   return havechanged      

def set_button_enabled_state( btn, val, colors ):
   btn['foreground'] = '#000000'
   if val:
      btn['state'] = 'normal'
      btn['background']       = colors['normal']
      btn['activebackground'] = colors['hover']
   else:
      btn['state'] = 'disabled'
      btn['background'] = '#c0c0c0'

def refresh_the_bottom_buttons():
   if fully_installed:
      havechanged=any_lines_have_changed()
      for name in ( 'undo', 'save' ):
         bi = BottomButtons[name]
         set_button_enabled_state( bi[ 'button' ], havechanged, bi[ 'colors' ] )
      ub = BottomButtons[ 'unlock' ]
      unlock_btn_state = True if presently_locked else False
      set_button_enabled_state( ub['button'], unlock_btn_state,  ub['colors'] )
      lb = BottomButtons[ 'lock' ]
      lock_btn_state = True if (not presently_locked) and (not havechanged) else False
      set_button_enabled_state( lb['button'], lock_btn_state, lb['colors'] )

      for i in range( NUM_CMDS ):
         ee =  all_rows[i]['entrywidget']
         if presently_locked:
            ee['disabledbackground'] =  yellowish
            ee['disabledforeground'] =  black
            ee['state'] = 'disabled'
         else:
            ee['background'] =  white
            ee['state'] = 'normal'
   return

def refresh_button_for_row( ix ):
 if fully_installed:
   do_enabled=True;  up_enabled=True;  down_enabled=True
   ri = all_rows[ix]
   e = ri['entrywidget']
   if len( e.get() ) <=0:
      do_enabled=False
      down_enabled=False
      up_enabled=False
   if ix==0:
      up_enabled=False
   if ix==NUM_CMDS-1:
      down_enabled=False
   if presently_locked:
      down_enabled=False
      up_enabled=False
   set_button_enabled_state( ri['upbtn'],   up_enabled,   oranges )
   set_button_enabled_state( ri['downbtn'], down_enabled, oranges )
   set_button_enabled_state( ri['dobtn'],   do_enabled,   greens )

def refresh_all_grid_buttons():
   for i in range(NUM_CMDS):
      refresh_button_for_row(i)

def refresh_all_buttons():
   refresh_the_bottom_buttons()
   refresh_all_grid_buttons()

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

def blink_row( ix, highlight_color, nloops, secs ):  
   ee = all_rows[ix]['entrywidget']
   #time.sleep( 0.15)
   for i in range(nloops):
      ee['background'] = highlight_color
      ee['disabledbackground'] = highlight_color
      time.sleep( 0.1 ) 

      if presently_locked:
         color =  yellowish
      else:
         color =  white
      ee['background'] = color
      ee['disabledbackground'] = color
      time.sleep( 0.1 ) 

def blink_row_async( ix, highlight_color, nloops, secs ):
   t = threading.Thread(target=blink_row, args=(ix,highlight_color,nloops,secs), kwargs=None )
   t.start()

def button_cb( ix,name ):
   global presently_locked
   if name=='undo':
      whichdiff = execute_undo()
      for j,chgd in enumerate(whichdiff):
         if chgd:
            blink_row_async(j, lavender, 1, 0.25)
   elif name=='save':
      execute_save()
   elif name=='lock':
      presently_locked=True
   elif name=='unlock':
      presently_locked=False
   elif name=='do':
      blink_row_async(ix, pink,2, 0.1)
      sendcmd = all_rows[ix]['entrywidget'].get()
      execute_do_async( sendcmd )
   elif name=='up':
      if ix==0:
         print( "error: at top already ")
         return()
      swap_entry_contents( ix, ix-1)
   elif name=='down':
      if ix==(NUM_CMDS-1):
         print( "error: at bottom already")
         return()
      swap_entry_contents( ix, ix+1)
   else:
      exit_fail( "bad name: '%'%" % name )
   refresh_all_buttons()

def entry_callback( stringvar, ix):
   refresh_all_buttons()

# returns an array of bools where true means that value changed
def execute_undo():
   rval=[]
   for i in range(NUM_CMDS):
      ri = all_rows[i]
      e = ri['entrywidget']
      was_different = True if e.get()!=init_lines[i] else False
      rval.append(was_different)
      e.delete( 0,END)
      e.insert( 0,  init_lines[i] )
   return rval

def execute_save():
   global init_lines
   saved_lines=[]
   f=open( fn_settings, 'w' )
   for i in range( NUM_CMDS ):
      ri = all_rows[i]
      e = ri['entrywidget']
      f.write(  e.get()+'\n' )
      saved_lines.append(  e.get() )
   f.close()
   init_lines = saved_lines

def swap_entry_contents( ix0, ix1 ):
   e0 = all_rows[ix0]['entrywidget']
   e1 = all_rows[ix1]['entrywidget']
   s0 = e0.get()
   s1 = e1.get()
   e1.delete( 0,END)
   e1.insert( 0,s0 )
   e0.delete( 0,END)
   e0.insert( 0,s1 )

def install_main_grid( master ):
   global all_rows
   do_font=font.Font( size=6 )
   for r in range(NUM_CMDS):
      row_info={}
      c=0;
      btn = Button( master, text='DO', pady=3, font=do_font, command=lambda j=r: button_cb(j,'do')  )
      btn.grid(row=r,column=c, padx=0 )
      enable_state = True if len( init_lines[r] ) >0 else False
      set_button_enabled_state( btn, enable_state, greens )
      row_info['dobtn']=btn
      c+=1

      sv = StringVar()
      sv.trace( 'w',  lambda name, index, mode, j=r, sv=sv: entry_callback(sv,j) )
      e= Entry( master, width=50, textvariable=sv   )
      e.grid(row=r,column=c, padx=2)
      if r<len(init_lines):
         e.insert( 0, init_lines[r])
      row_info['entrywidget']=e
      c+=1

      btn = Button( master, text='▲', padx=2, pady=3, font=do_font, command=lambda j=r: button_cb(j,'up')  )
      btn.grid(row=r,column=c, padx=0 )
      set_button_enabled_state( btn, True, oranges )
      row_info['upbtn']=btn
      c+=1

      btn = Button( master, text='▼', padx=2, pady=3, font=do_font, command=lambda j=r: button_cb(j,'down')  )
      btn.grid(row=r,column=c, padx=0 )
      set_button_enabled_state( btn, True, oranges )
      row_info['downbtn']=btn
      c+=1

      all_rows.append( row_info )
   return

def install_bottom_buttons( frame ):
   global BottomButtons
   button_text = {
      'lock'  :   'L',     
      'unlock':   'U',   
      'undo':     'Undo',    
      'save':     'Save',    
   }
   spacer_columns = {
      'sp_left'   : 3,
      'sp_middle' : 4,
      'sp_right'  : 5,
   }
   columns = ( 'sp_left' ,'unlock', 'lock', 'sp_middle' , 'undo', 'save', 'sp_right' )

   for col,name in enumerate(columns):
      if name in button_text:
         btn = Button( frame, text=button_text[name], command=lambda j=0,nn=name: button_cb(j,nn) )
         btn.grid(row=0,column=col, padx=3, pady=5)
         info_per_button = { 'button' : btn,  'colors':  blues  }
         BottomButtons[name]=info_per_button
      elif name in spacer_columns:
         weight = spacer_columns[name]
         frame.grid_columnconfigure( col, weight=weight)
      else:
         exit_fail( "illegal column")
      col+=1

   for name in BottomButtons:
      bi = BottomButtons[name]
      set_button_enabled_state(  bi['button'], True,  bi['colors'] )

def init_window( root ):
   global fully_installed
   top_frame = Frame(root , width=450, height=2, pady=3)
   center = Frame(root )
   btm_frame = Frame(root ) 
   top_frame.grid(row=0, sticky="ew")
   center.grid(row=1, sticky="nsew")
   btm_frame.grid(row=3, sticky="ew")
   install_main_grid( center )
   install_bottom_buttons( btm_frame )   
   fully_installed=True
   refresh_all_buttons()

def main(argv):
   global window_id, init_lines;

   rr,oo,ee=run('%s getactivewindow' % XDOTOOL )
   if len(ee)>0:
      print( "problem running xdotool" )
      print( "stderr:", ee )
      print( "try: sudo apt install xdotool" )
      exit()

   window_id = int(  oo )
   print( "window_id = %d (0x%x)" % (window_id, window_id) )

   if os.path.exists( fn_settings ):
      print( "Loading settings from '%s'" % fn_settings )
      with open( fn_settings, 'r' ) as f:
         contents =f.read()
      init_lines = contents.splitlines()
      for i in range( len(init_lines), NUM_CMDS):
         init_lines.append('')
   else:
      print( "No setings found. Using defautlts"  )
      init_lines = default_lines

   # fork and return parent process
   if os.fork()>0:
      return

   #child process - create window and launch its
   root = Tk()
   root.title( "bbuddy")
   init_window( root )
   root.resizable(False,False)
   root.mainloop()


#-------------------------------
if __name__ == "__main__":
   main( sys.argv)

