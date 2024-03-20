from bokeh.models import Button, NumericInput, Div, Plot, ColumnDataSource
from bokeh.layouts import layout
from bokeh.io import show, curdoc
from bokeh.events import ButtonClick
from datetime import datetime, timedelta
import sys
import threading
import time

#--------------------------------------------------------------------------------------------------------------------

                                            # BOKEH 

#--------------------------------------------------------------------------------------------------------------------


#-------------------------------------
    # U/I Syntax
#-------------------------------------


# label_...         ---> Div of a text, for labelling U/I elements

# display_...       ---> NumericInput display, for displaying the actual boxy data

# button_...        ---> Button, not much else to say

# dropdown_...      ---> model for a drop-down menu, will look into working with it

# will add more models as needed...


#-------------------------------------
    # Thread Controls
#-------------------------------------

# these will be thread events (semaphores, but complexities are hidden)


#-------------------------------------
    # Margins
#-------------------------------------

# define spacing of U/I elements, will become more populated over time


#-------------------------------------
    # Styles
#-------------------------------------

# styles define some properties of the U/I, which will help give a modern feel eventually

# the 'z-index' property places the elements in vertical layers, higher index values means a higher layer
# when two U/I elements are on a different layer, their padding/margins won't affect each other


#-------------------------------------
    # Labels
#-------------------------------------

# labels for all the different U/I elements that need them


#-------------------------------------
    # Displays
#-------------------------------------

# for inputting numbers


#-------------------------------------
    # Miscellaneous U/I
#-------------------------------------

# will have the graph plot for the schedule results, and other touches for user-friendliness


#-------------------------------------
            # Buttons  
#-------------------------------------


#-------------------------------------
            # Button Callbacks   
#-------------------------------------

# these are the functions that will be tied to buttons (e.g "play", "reset", "shutdown", maybe "save" if we have time?)


#-------------------------------------
    # Master Thread Callbacks
#-------------------------------------

# the U/I changes have to be caused by threads, with those U/I changes coming in through server callbacks
# for now, a single master thread will handle all U/I changes


#-------------------------------------
    # Threads 
#-------------------------------------

# ONLY relevant thread events will be passed to a thread

# the master thread will be the thread that contains the dynamics of the simulator
# inside it is where we'll have calls to the scheduling functions that have been made (and possibly other functions)
# server callbacks will cause U/I changes on the fly
def master_thread():

  # main_thread is the one thread that all the code lives within
  # bokeh servers will need independent threads to run properly, and opens the avenue for user-friendliness
  # while threading.main_thread().is_alive():

  #   print("Simulating stuff...")
  #   time.sleep(1)

  # the code below will run once the user has decided to shutdown the simulator, which will kill main_thread & all other threads
  # this is only possible with the while loop structure above (and after adding a "shutdown" button)
  # also, the shutdown button is necessarry to avoid rogue threads just continuing to live on independently
  # print(f'[MASTER] [ {datetime.now()} ] Simulator shutting down... \n')

  # the return is unneccessary, this is just to not have a wierd error for incomplete code
  return None

# a shutdown thread, for U/I responsiveness that isn't affected by the master thread
def shutdown_thread():

  # while threading.main_thread().is_alive():

  #   print("Waiting to stop...")
  #   time.sleep(1)
    
  return None


# this is the literal layout of the U/I, all the U/I elements will be placed here
# Bokeh can't display the same U/I element multiple times in the same layout row
my_layout = layout (  [
                        [],
                      ]
                   )


# declaring the document object for the app, so all threads access the same document & cause U/I changes
app_doc = curdoc()
app_doc.title = "Scheduling Simulator"

# to show the layout
app_doc.add_root(my_layout)

# may or may not need to set some thread events here

# preparing the threads, passing over relevant thread arguments
t1 = threading.Thread( target = master_thread, args = () )
t2 = threading.Thread( target = shutdown_thread, args = ())


# t2.start()
# t1.start()

# eventually, i'll make a batch script so that we'll have the ultimate user-friendliness
