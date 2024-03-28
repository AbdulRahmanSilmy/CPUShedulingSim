from bokeh.models import Button, NumericInput, Select, Div, Plot, ColumnDataSource
from bokeh.layouts import layout
from bokeh.plotting import figure, show, curdoc
from bokeh.events import ButtonClick
from modules.compute import cpu_scheduling_compute
from datetime import datetime, timedelta
from functools import partial
import numpy as np
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

# figure_...        ---> Figure that will hold the plotted scheduling results

# will add more models as needed...


#-------------------------------------
    # Thread Controls
#-------------------------------------


# these will be thread events (semaphores, but complexities are hidden)

button_run_pressed = threading.Event()


#-------------------------------------
    # Misc. Initialisation
#-------------------------------------

# front-end list for FCFS release times
FCFS_release_time: list[int] = list()
FCFS_wc_exec_time: list[int] = list()

# a count for which task the user is configuring
count_task: int = 1


#-------------------------------------
    # Margins
#-------------------------------------

# define spacing of U/I elements, will become more populated over time
# syntax: (top, right, bottom, left)

margin_label_dropdown = (200,0,10,90)

margin_button_dropdown_algo = (195,0,40,15)

margin_figure_results = (-100,0,0,800)

margin_label_task_count = (-250,0,0,260)
margin_label_release_time = (-200,-7,20,147)
margin_label_wc_exec_time = (-150,10,40,40)

margin_display_release_time = (-201,0,0,0)
margin_display_wc_exec_time = (-151,0,0,0)

margin_button_add_task = (-60,0,0,100)
margin_button_clear_tasks = (-60,0,0,100)
margin_button_run = (-185,0,0,450)



#-------------------------------------
    # Styles
#-------------------------------------

# styles define some properties of the U/I, which will help give a modern feel eventually

# the 'z-index' property places the elements in vertical layers, higher index values means a higher layer
# when two U/I elements are on a different layer, their padding/margins won't affect each other


style_buttons = {
                                        'z-index':'5',
                                        'font-size': '16px',                                       
                }

style_button_run = {
                                        'z-index':'5',
                                        'font-size': '16px',
                                        'position':'fixed',
                                        
                }

style_labels = {  
                                        'z-index':'4',
                                        'font-size': '16px',
                                        'font-weight':'bold',
                                        
                }

style_displays = {
                                        'z-index':'4',
                                        'font-size': '16px',
                 }

style_figure = {
                                        'font-weight':'bold',
                                        'font-size': '16px',
                                        'position':'relative',                                        
}


#-------------------------------------
    # Labels
#-------------------------------------

# labels for all the different U/I elements that need them

label_dropdown = Div(
    text = "<b>Choose Scheduling Algorithm:</b>",
    width=245,
    height=30,
    margin = margin_label_dropdown,
    styles = style_labels,
)

# to let the user be aware of what task they're currently configuring
label_task_count = Div(
    text = """<u>Task 1:</u>""",
    width=125,
    height=30,
    visible = False,
    margin = margin_label_task_count,
    styles = style_labels,
)

label_release_time = Div(
    text = "<b>Release Time:</b>",
    width=125,
    height=30,
    visible = False,
    margin = margin_label_release_time,
    styles = style_labels,
)

label_wc_exec_time = Div(
    text = "<b>Worst-case Execution Time:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_wc_exec_time,
    styles = style_labels,
)


#-------------------------------------
    # Displays
#-------------------------------------


# for inputting numbers

display_release_time = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_release_time,
)

display_wc_exec_time = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_wc_exec_time,
)


#-------------------------------------
    # Miscellaneous U/I
#-------------------------------------


# will have the graph plot for the schedule results, and other touches for user-friendliness

figure_results = figure(
    x_range = [],
    height=350,
    #toolbar = _,
    #toolbar_location = _,
    title="Scheduling Results",
    styles = style_figure,
    margin = margin_figure_results,
)


#-------------------------------------
            # Buttons  
#-------------------------------------


button_dropdown_algo = Select(
    width=90,
    height = 25,
    visible = True,
    value = "",
    options = ['FCFS', 'RM'],
    margin = margin_button_dropdown_algo,
    styles = style_buttons,
)

button_add_task = Button(
    label = "Add New Task",
    width=100,
    height = 40,
    button_type = 'default',
    visible = False,
    margin = margin_button_add_task,
    styles = style_buttons,
)

button_clear_tasks = Button(
    label = "Clear Tasks",
    width=100,
    height = 40,
    button_type = 'primary',
    visible = False,
    margin = margin_button_clear_tasks,
    styles = style_buttons,
)

button_run = Button(
    label = "Run",
    width=100,
    height = 40,
    button_type = 'success',
    visible = False,
    margin = margin_button_run,
    styles = style_button_run,
)


#-------------------------------------
            # Button Callbacks   
#-------------------------------------

# these are the functions that will be tied to buttons (e.g "play", "reset", "shutdown", maybe "save" if we have time?)

#TODO - clear any data that was collected from a previous algo options, to have a clean slate
def show_options(attr, old, new):
    
    if new == 'FCFS':
        
        # invisible the others, show the U/I for release time, w.c exec time, add new task, clear task, run
        print('You chose FCFS')

        label_task_count.visible = True
        label_release_time.visible = True
        label_wc_exec_time.visible = True
        display_release_time.visible = True
        display_wc_exec_time.visible = True
        button_add_task.visible = True
        button_clear_tasks.visible = True
        button_run.visible = True
        
    if new == 'RM':

        # TODO - add extra U/I and U/I behaviour for RM
        print('You chose RM')    
button_dropdown_algo.on_change("value", show_options)

# signals the master thread to collect the appropriate scheduling info
def run():

    # checking whether the run button has already been clicked and is being processed
    # if the button action hasn't finished yet, the next click can't operate yet
    if not button_run_pressed.wait(timeout = 0.05):
        
        button_run_pressed.set()
button_run.on_event(ButtonClick,run)  

def collect_task():

    global count_task
    
    # the value of the dropdown button will dictate what task info to collect
    if button_dropdown_algo.value == 'FCFS':

        FCFS_release_time.append(display_release_time.value)
        FCFS_wc_exec_time.append(display_wc_exec_time.value)
        display_release_time.value = 0
        display_wc_exec_time.value = 0
    
        print(f'Release times: {FCFS_release_time}')
        print(f'W.C Ex. times: {FCFS_wc_exec_time}')
        
    # clear the inputs for the next entry
    count_task += 1
    label_task_count.text = f"""<u>Task {count_task}:</u>"""
    
button_add_task.on_click(collect_task) 


#-------------------------------------
    # Master Thread Callbacks
#-------------------------------------

# the U/I changes have to be caused by threads, with those U/I changes coming in through server callbacks
# for now, a single master thread will handle all U/I changes

# applies vertical bars for task results
def show_task_result(task_x_coord, task_width, frequency, label, task_count):

    # TODO - make it possible to use distinct colours for any number of tasks
    plot_colors=['blue','green','red','pink','orange','yellow']
    
    figure_results.vbar(x = task_x_coord, width = task_width, top = frequency, fill_color = plot_colors[task_count])
    figure_results.y_range.start = 0
    figure_results.xgrid.grid_line_color = None
    figure_results.xaxis.axis_label = "Time"
    figure_results.outline_line_color = None
    print('done displaying')

    

#-------------------------------------
    # Threads 
#-------------------------------------

# ONLY relevant thread events will be passed to a thread

# the master thread will be the thread that contains the dynamics of the simulator
# inside it is where we'll have calls to the scheduling functions that have been made (and possibly other functions)
# server callbacks will cause U/I changes on the fly
def master_thread(t_master_button_run_pressed):

  # main_thread is the one thread that all the code lives within
  # bokeh servers will need independent threads to run properly, and opens the avenue for user-friendliness
  while threading.main_thread().is_alive():

    if button_run_pressed.wait():

        if button_dropdown_algo.value == 'FCFS':

            task_info = {   "scheduling_algo":'first_come_first_serve',
                            'release_time':FCFS_release_time,
                            'wc_exec_time':FCFS_wc_exec_time
                        }

            results, dict_info = cpu_scheduling_compute(task_info)

            # the callback will repeatedly add bars for each task
            for row in results:

                task_x_coord = np.mean(row[1:3])
                task_width = row[2] - row[1]
                frequency = row[3]
                label = f'Task {int(row[0])+1}'
                task_count = int(row[0])
                
                app_doc.add_next_tick_callback(partial(show_task_result, task_x_coord, task_width, frequency, label, task_count))

        button_run_pressed.clear()
      
    print("Simulating stuff...")
    time.sleep(1)

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
                        [label_dropdown, button_dropdown_algo],
                        [figure_results],
                        [label_task_count],
                        [label_release_time, display_release_time],
                        [label_wc_exec_time, display_wc_exec_time, button_run],
                        [button_add_task, button_clear_tasks],
                      ]
                   )


# declaring the document object for the app, so all threads access the same document & cause U/I changes
app_doc = curdoc()
app_doc.title = "Scheduling Simulator"

# to show the layout
app_doc.add_root(my_layout)

# may or may not need to set some thread events here

# preparing the threads, passing over relevant thread arguments
t1 = threading.Thread( target = master_thread, args = (button_run_pressed,) )
t2 = threading.Thread( target = shutdown_thread, args = ())


# t2.start()
t1.start()

# eventually, i'll make a batch script so that we'll have the ultimate user-friendliness
show(my_layout)