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

# to let the shutdown thread show the shutdown popup
button_shutdown_pressed = threading.Event()

# to notify that the simulator has shutdown
shutdown_confirmed = threading.Event()


#-------------------------------------
    # Misc. Initialisation
#-------------------------------------

# front-end list for FCFS release times
FCFS_release_time: list[int] = list()
FCFS_wc_exec_time: list[int] = list()

# front-end list for RM release times
RM_exec_time: list[int] = list()
RM_period: list[int] = list()
RM_end_time: list[int] = list()


# front-end list for EDF release times
CC_EDF_wc_exec_time: list[int] = list()
CC_EDF_period: list[int] = list()
CC_EDF_invocation1: list[int] = list()
CC_EDF_invocation2: list[int] = list()
CC_EDF_invocation3: list[int] = list()

# a count for which task the user is configuring
count_task: int = 1


#-------------------------------------
    # Margins
#-------------------------------------

# define spacing of U/I elements, will become more populated over time
# syntax: (top, right, bottom, left)

margin_label_dropdown = (200,0,10,90)
margin_label_num_invocations = (-200,-20,60,40)  # Label for the Num invocation label

margin_button_dropdown_algo = (195,0,40,15)
margin_button_dropdown_invocation = (-201,0,0,20)  # Button for dropdown invocation

margin_figure_results = (-100,0,0,900)

# For FCFS
margin_label_task_count = (-350,0,0,260)
margin_label_release_time = (-300,-7,20,147)
margin_label_wc_exec_time = (-250,10,40,40)
margin_label_invocation1 = (-150,0,0,100)
margin_label_invocation2 = (-150,0,0,300)
margin_label_invocation3 = (-150,0,0,500)
margin_label_period = (-300,-20,60,197)
margin_label_exec_time = (-250,10,40,167)
margin_label_end_time = (-200,10,40,173)

margin_display_release_time = (-301,0,0,0)
margin_display_period = (-301,0,0,-36)
margin_display_wc_exec_time = (-251,0,0,0)
margin_display_invocation = (-201,0,0,-97)
margin_display_exec_time = (-251,0,0,-127)
margin_display_invocation1 = (-150,0,0,-110)
margin_display_invocation2 = (-150,0,0,-110)
margin_display_invocation3 = (-150,0,0,-110)
margin_display_end_time = (-200,0,0,-132)


margin_button_add_task = (-30,0,0,100)
margin_button_clear_tasks = (-30,0,0,100)
margin_button_run = (75,0,0,650)
margin_button_show_shutdown = (-30,0,0,150)
margin_button_shutdown_no = (-170,0,0,-300)
margin_button_shutdown_yes = (-170,0,0,100)

margin_blur_block = (0,0,-1300,-500)
margin_popup_shutdown = (-200,0,0,559)

margin_background_UI = (-440,0,0,20)

#-------------------------------------
    # Styles
#-------------------------------------

# styles define some properties of the U/I, which will help give a modern feel eventually

# the 'z-index' property places the elements in vertical layers, higher index values means a higher layer
# when two U/I elements are on a different layer, their padding/margins won't affect each other


style_buttons = {
                                        'z-index':'5',
                                        'font-size': '16px',
                                        'position':'relative'
                                        
                }
  
# since the U/I options change for each algo, the run button position is absolute to avoid moving around unnecessarily  
style_button_run = {
                                        'z-index':'5',
                                        'font-size': '16px',
                                        'position':'absolute',
                                        
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
                                        'z-index':'4',
                                        'font-weight':'bold',
                                        'font-size': '16px',
                                        'position':'relative',                                        
                }

style_blur_block = {
                                        'z-index':'7',
                                        'background-color': 'rgba(255,255,255,0.3)',
                                        'backdrop-filter':'blur(7px)',
                                        'position':'relative'
                    }

style_popup_shutdown = {
                                        'position':'relative',
                                        'font-size':'15px',
                                        'z-index':'8',
                                        'background-color': '#DDDDDD',
                                        'border-radius':'5px 8px',
                                        'text-align':'center',
                                        'padding-top':'10px'
                        }

style_background_UI = {
                                        'position':'relative',
                                        'font-size':'15px',
                                        'z-index':'3',
                                        'background-color': '#92B8D0',
                                        'border-radius':'65px 8px',
                                        'text-align':'center',
                        }
                        
                        
# this is applied to both the "no" and "yes" buttons rendered on the shutdown popup
style_button_shutdown = {
                                        'position':'relative',
                                        'font-size':'15px',
                                        'z-index':'9',
                                        'text-align':'center',
                                        'padding-top':'10px'
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

label_num_invocations = Div(
    text = "<b>Choose Number of Invocations:</b>",
    width=245,
    height=30,
    margin = margin_label_num_invocations,
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

label_period = Div(
    text = "<b>Period:</b>",
    width=125,
    height=30,
    visible = False,
    margin = margin_label_period,
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

label_invocation1 = Div(
    text = "<b>Invocation 1:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_invocation1,
    styles = style_labels,
)

label_invocation2 = Div(
    text = "<b>Invocation 2:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_invocation2,
    styles = style_labels,
)
label_invocation3 = Div(
    text = "<b>Invocation 3:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_invocation3,
    styles = style_labels,
)

label_exec_time = Div(
    text = "<b>Exec Time:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_exec_time,
    styles = style_labels,
)

label_end_time = Div(
    text = "<b>End Time:</b>",
    width=215,
    height=30,
    visible = False,
    margin = margin_label_end_time,
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

display_invocation = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_invocation,
)

display_period = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_period,
)

display_exec_time = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_exec_time,
)

display_end_time = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_end_time,
)

display_invocation1 = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_invocation1,
)
display_invocation2 = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_invocation2,
)
display_invocation3 = NumericInput(
    mode = 'int',
    value = 0,
    low = 0,
    width=65,
    height = 25,
    styles = style_displays,
    visible = False,
    margin = margin_display_invocation3,
)

#-------------------------------------
    # Miscellaneous U/I
#-------------------------------------


# will have the graph plot for the schedule results, and other touches for user-friendliness

figure_results = figure(
    height=450,
    #toolbar = _,
    #toolbar_location = _,
    title="Scheduling Results",
    styles = style_figure,
    margin = margin_figure_results,
)

background_UI = Div(
    width=760,
    height=500,
    visible = True,
    styles = style_background_UI,
    margin = margin_background_UI,
)

blur_block = Div(
    width=1920,
    height=1080,
    visible = False,
    styles = style_blur_block,
    margin = margin_blur_block,
)

# this acts as the shutdown popup window
popup_shutdown = Div(
    text =  """ <b>Are you sure you want to stop the simulator?</b> """,
    width=400,
    height=90,
    visible = False,
    styles = style_popup_shutdown,
    margin = margin_popup_shutdown,
)


#-------------------------------------
            # Buttons  
#-------------------------------------


button_dropdown_algo = Select(
    width=90,
    height = 25,
    visible = True,
    value = "",
    options = ['FCFS', 'RM', 'CC EDF'],
    margin = margin_button_dropdown_algo,
    styles = style_buttons,
)

button_dropdown_invocation = Select(
    width=90,
    height = 25,
    visible = True,
    value = "",
    options = ['1', '2', '3'],
    margin = margin_button_dropdown_invocation,
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

button_show_shutdown = Button(
    label = "Shutdown",
    width=100,
    height = 40,
    button_type = 'danger',
    visible = True,
    margin = margin_button_show_shutdown,
    styles = style_buttons,
)

button_shutdown_no =  Button(
    label = "No",
    width=45,
    height = 45,
    button_type = 'primary',
    visible = False,
    margin = margin_button_shutdown_no,
    styles = style_button_shutdown,
)

button_shutdown_yes =  Button(
    label = "Yes",
    width=45,
    height = 45,
    button_type = 'default',
    visible = False,
    margin = margin_button_shutdown_yes,
    styles = style_button_shutdown,
)


#-------------------------------------
            # Button Callbacks   
#-------------------------------------

# Button
# these are the functions that will be tied to buttons (e.g "play", "reset", "shutdown", maybe "save" if we have time?)
# Set default values for UI elements
button_dropdown_algo.value = 'FCFS'
label_task_count.visible = True
label_release_time.visible = True
label_wc_exec_time.visible = True
label_period.visible = False
label_exec_time.visible = False
label_end_time.visible = False
label_invocation1.visible = False
label_invocation2.visible = False
label_invocation3.visible = False
label_num_invocations.visible = False
display_release_time.visible = True
display_wc_exec_time.visible = True
display_period.visible = False
display_invocation.visible = False
display_exec_time.visible = False
display_end_time.visible = False
button_dropdown_invocation.visible = False
button_add_task.visible = True
button_clear_tasks.visible = True
button_run.visible = True

#TODO - clear any data that was collected from a previous algo options, to have a clean slate
def show_options(attr, old, new):
    
    global count_task
    
    button_add_task.visible = True
    button_clear_tasks.visible = True
    label_task_count.visible = True
    button_run.visible = True
    
    # TODO - let this condition also handle transitions from the other algo options, to FCFS
    if (new == 'FCFS') and (old == 'RM'):
        print('Went to FCFS from RM')
        RM_exec_time.clear()
        RM_period.clear()

    elif (new == 'FCFS') and (old == 'CC EDF'):
        print('Went from CC EDF to RM')
        CC_EDF_wc_exec_time.clear()
        CC_EDF_period.clear()
        

    if new == 'FCFS':
        
        # TODO - clear the lists that the other algorithms use here
        
        # invisible the others, show the U/I for release time, w.c exec time, add new task, clear task, run
        print('You chose FCFS')

        label_task_count.visible = True
        label_release_time.visible = True
        label_wc_exec_time.visible = True
        label_period.visible = False
        label_exec_time.visible = False
        label_end_time.visible = False
        label_invocation1.visible = False
        label_invocation2.visible = False
        label_invocation3.visible = False
        label_num_invocations.visible = False
        label_invocation1.visible = False
        label_invocation2.visible = False
        label_invocation3.visible = False
        button_dropdown_invocation.visible = False
        display_release_time.visible = True
        display_wc_exec_time.visible = True
        display_period.visible = False  # Hide the period input field
        display_invocation.visible = False
        display_exec_time.visible = False
        display_end_time.visible = False
        

        
        
        count_task = 1
        label_task_count.text = f"""<u>Task {count_task}:</u>"""


    # TODO - let this condition also handle transitions from the other algo options, to RM
    if (new == 'RM') and (old == 'FCFS'):
        print('Went to RM from FCFS')
        FCFS_release_time.clear()
        FCFS_wc_exec_time.clear()
        
    elif (new == 'RM') and (old == 'CC EDF'):
        print('Went to RM from CC EDF')
        CC_EDF_wc_exec_time.clear()
        CC_EDF_period.clear()
       
        
    if new == 'RM':

        # TODO - add extra U/I and U/I behaviour for RM
        
        print('You chose RM')
        
        label_task_count.visible = True
        label_period.visible = True
        label_release_time.visible = False
        label_wc_exec_time.visible = False
        label_invocation1.visible = False
        label_invocation2.visible = False
        label_invocation3.visible = False
        label_exec_time.visible = True
        label_end_time.visible = True
        label_num_invocations.visible = False
        label_invocation1.visible = False
        label_invocation2.visible = False
        label_invocation3.visible = False
        display_period.visible = True
        display_release_time.visible = False
        display_wc_exec_time.visible = False
        display_invocation.visible = False
        display_exec_time.visible = True
        display_end_time.visible = True
        button_dropdown_invocation.visible = False

        count_task = 1
        label_task_count.text = f"""<u>Task {count_task}:</u>"""

    if (new == 'CC EDF') and (old == 'FCFS'):
        print('Went to RM from FCFS')
        FCFS_release_time.clear()
        FCFS_wc_exec_time.clear()

    elif (new == 'CC EDF') and (old == 'RM'):
        print('Went to RM from CC EDF')
        RM_exec_time.clear()
        RM_period.clear()

    if new == 'CC EDF':

        # TODO - clear the lists that the other algorithms use here

        print("You chose CC EDF")

        label_task_count.visible = True
        label_period.visible = True
        label_wc_exec_time.visible = True
        label_exec_time.visible = False
        label_end_time.visible = False
        label_invocation1.visible = False
        label_invocation2.visible = False
        label_invocation3.visible = False
        label_num_invocations.visible = True
        label_release_time.visible = False
        display_period.visible = True
        display_wc_exec_time.visible = True
        display_invocation.visible = False
        display_release_time.visible = False    # Hide the release time input 
        display_exec_time.visible = False
        display_end_time.visible = False
        button_dropdown_invocation.visible = True
    


        count_task = 1
        label_task_count.text = f"""<u>Task {count_task}:</u>"""

# Register the callback function for the dropdown button
button_dropdown_algo.on_change("value", show_options)
button_dropdown_invocation.on_change('value', show_options)

def show_invocation_labels(attr, old, new):
    # Determine which label_invocation element to display based on the selected value
    if new == '1':
        label_invocation1.visible = True
        label_invocation2.visible = False
        label_invocation3.visible = False
        display_invocation1.visible = True
        display_invocation2.visible = False
        display_invocation3.visible = False
    elif new == '2':
        label_invocation1.visible = True
        label_invocation2.visible = True
        label_invocation3.visible = False
        display_invocation1.visible = True
        display_invocation2.visible = True
        display_invocation3.visible = False
    elif new == '3':
        label_invocation1.visible = True
        label_invocation2.visible = True
        label_invocation3.visible = True
        display_invocation1.visible = True
        display_invocation2.visible = True
        display_invocation3.visible = True

# Register the callback function for the dropdown button
button_dropdown_invocation.on_change('value', show_invocation_labels)

def collect_task():

    global count_task
    
    
    # the value of the dropdown button will dictate what task info to collect
    if button_dropdown_algo.value == 'FCFS':

        FCFS_release_time.append(display_release_time.value)
        FCFS_wc_exec_time.append(display_wc_exec_time.value)
        display_release_time.value = 0
        display_wc_exec_time.value = 0
    
        print(f'Release times (FCFS): {FCFS_release_time}')
        print(f'W.C Ex. times (FCFS): {FCFS_wc_exec_time}')

    elif button_dropdown_algo.value == 'RM':
        RM_period.append(display_period.value)
        RM_exec_time.append(display_exec_time.value)
        RM_end_time.append(display_end_time.value)
        display_period.value = 0
        display_exec_time.value = 0
        display_end_time.value = 0

        print(f'Periods (RM): {RM_period}')  
        print(f'W.C Ex. times (RM): {RM_exec_time}')
        print(f'End Time (RM): {RM_end_time}')  

    elif button_dropdown_algo.value == 'CC EDF':
        CC_EDF_period.append(display_period.value)
        display_period.value = 0
        print(f'Periods (CC EDF): {CC_EDF_period}')  
    
        CC_EDF_wc_exec_time.append(display_wc_exec_time.value)
        display_wc_exec_time.value = 0
        print(f'W.C Ex. times (CC EDF): {CC_EDF_wc_exec_time}')

        invocation_1_val = 0
        invocation_2_val = 0
        invocation_3_val = 0
        
        if button_dropdown_invocation.value == '1':
            invocation_1_val = display_invocation1.value
        elif button_dropdown_invocation.value == '2':
            invocation_1_val = display_invocation1.value
            invocation_2_val = display_invocation2.value
        elif button_dropdown_invocation.value == '3':
            invocation_1_val = display_invocation1.value
            invocation_2_val = display_invocation2.value
            invocation_3_val = display_invocation3.value

        CC_EDF_invocation1.append(invocation_1_val)
        display_invocation1.value = 0
        CC_EDF_invocation2.append(invocation_2_val)
        display_invocation2.value = 0
        CC_EDF_invocation3.append(invocation_3_val)
        display_invocation3.value = 0
        
        print(f'Invocation 1 (CC EDF): {CC_EDF_invocation1}')
        print(f'Invocation 2 (CC EDF): {CC_EDF_invocation2}')
        print(f'Invocation 3 (CC EDF): {CC_EDF_invocation3}')

    
    
    count_task += 1
    label_task_count.text = f"""<u>Task {count_task}:</u>"""
button_add_task.on_click(collect_task) 


# clears the task data collected for a given algorithm
#TODO - add the clearing option for the other algos
def clear_tasks():
    
    global count_task
    
    count_task = 1
    label_task_count.text = f"""<u>Task {count_task}:</u>"""
    
    if button_dropdown_algo.value == 'FCFS':
        
        FCFS_release_time.clear()
        FCFS_wc_exec_time.clear()

    elif button_dropdown_algo.value == 'CC EDF':

        CC_EDF_wc_exec_time.clear()
        CC_EDF_period.clear()
    
    elif button_dropdown_algo.value == 'RM':
        RM_period.clear()
        RM_exec_time.clear()

button_clear_tasks.on_click(clear_tasks)

 
# signals the master thread to collect the appropriate scheduling info
def run():

    # checking whether the run button has already been clicked and is being processed
    # if the button action hasn't finished yet, the next click can't operate yet
    if not button_run_pressed.wait(timeout = 0.05):
        
        button_run_pressed.set()
button_run.on_event(ButtonClick,run)  


def show_shutdown_popup():
    
    button_shutdown_pressed.set()
button_show_shutdown.on_event(ButtonClick,show_shutdown_popup)


def hide_shutdown_popup():
    
    button_shutdown_pressed.clear()
button_shutdown_no.on_event(ButtonClick,hide_shutdown_popup)


def trigger_shutdown():
    
    shutdown_confirmed.set()  
button_shutdown_yes.on_event(ButtonClick,trigger_shutdown) 


#-------------------------------------
    # Master Thread Callbacks
#-------------------------------------

# the U/I changes have to be caused by threads, with those U/I changes coming in through server callbacks


# applies vertical bars for task results
def show_task_result(task_x_coord, task_width, frequency, label, task_count):
    
    # TODO - make it possible to use distinct colours for any number of tasks
    plot_colors=['blue','green','red','pink','orange','yellow']
    
    figure_results.vbar(x = task_x_coord, width = task_width, top = frequency, fill_color = plot_colors[task_count])
    figure_results.y_range.start = 0
    figure_results.xgrid.grid_line_color = None
    figure_results.xaxis.axis_label = "Time"
    figure_results.yaxis.axis_label = "Frequency"
    figure_results.outline_line_color = None
    print('done displaying')


#-------------------------------------
    # Shutdown Thread Callbacks
#-------------------------------------

# in case we run into issues when testing, or the user is done with their work, the simulator can be shut down
# ctrl + c doesn't actually kill the threads, this is an easy mechanism to achieving it

def show_shutdown_ui(show_popup, confirm_string):
    
    if show_popup:
    
        blur_block.visible = True
        popup_shutdown.visible = True
        button_shutdown_no.visible = True
        button_shutdown_yes.visible = True
        
        if confirm_string == "end":
            
            popup_shutdown.text = """ <b>Simulator has stopped</b> """
            button_shutdown_no.visible = False
            button_shutdown_yes.visible = False
            
    else:
        
        blur_block.visible = False  
        popup_shutdown.visible = False
        button_shutdown_no.visible = False
        button_shutdown_yes.visible = False
    
    
def shutdown():
    sys.exit()   
    
#-------------------------------------
    # Threads 
#-------------------------------------

# ONLY relevant thread events will be passed to a thread

# the master thread will be the thread that contains the dynamics of the simulator
# inside it is where we'll have calls to the scheduling functions that have been made (and possibly other functions)
# server callbacks will cause U/I changes on the fly
def master_thread(button_run_pressed):

    # main_thread is the one thread that all the code lives within
    # bokeh servers will need independent threads to run properly, and opens the avenue for user-friendliness
    while threading.main_thread().is_alive():
        
        # necessary so that the master thread doesn't get blocked from shutting down
        if button_run_pressed.wait(0.01):

            # clear the figure, to showcase only the tasks desired
            figure_results.renderers.clear()
            
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


    # the code below will run once the user has decided to shutdown the simulator, which will kill main_thread & all other threads
    # this is only possible with the while loop structure above (and after adding a "shutdown" button)
    # also, the shutdown button is necessarry to avoid rogue threads just continuing to live on independently
    print(f'[MASTER] [ {datetime.now()} ] Simulator shutting down... \n')


# a shutdown thread, for U/I responsiveness that isn't affected by the master thread
def shutdown_thread(button_shutdown_pressed, shutdown_confirmed):

    while threading.main_thread().is_alive():
        
        # necessary for the shutdown thread to not hog the CPU 
        time.sleep(0.005)
        
        if button_shutdown_pressed.is_set():
            
            # allow the user to confirm a shutdown
            app_doc.add_next_tick_callback(partial(show_shutdown_ui, 1, ""))
        
            if shutdown_confirmed.is_set():
                
                app_doc.add_next_tick_callback(partial(show_shutdown_ui, 1, "end"))
                
                # when a child thread calls "sys.exit()", the threads will end but the bokeh server will still be running
                # for this reason, there must be a server callback that calls "sys.exit()" for a synchronised shutdown between Bokeh & the threads (via "threading.main_thread.is_alive()" )
                app_doc.add_next_tick_callback(partial(shutdown))
                
        else:
            
            app_doc.add_next_tick_callback(partial(show_shutdown_ui, 0, ""))
            
    print(f'[SHUTDOWN] [ {datetime.now()} ] Simulator shutting down... \n')


# this is the literal layout of the U/I, all the U/I elements will be placed here
# Bokeh can't display the same U/I element multiple times in the same layout row
# "button_run" is placed next to the graph, so that it can't have its position adjusted by toggling U/I elements visible/invisible
my_layout = layout (  [
                        [label_dropdown, button_dropdown_algo, blur_block],
                        [button_run, figure_results],                       
                        [label_task_count],
                        [label_period, display_period],
                        [label_exec_time, display_exec_time],
                        [label_end_time, display_end_time],
                        [label_release_time, display_release_time],
                        [label_wc_exec_time, display_wc_exec_time],
                        [label_num_invocations, button_dropdown_invocation, blur_block],
                        [label_invocation1, display_invocation1],
                        [label_invocation2, display_invocation2],
                        [label_invocation3, display_invocation3],
                        [button_add_task, button_clear_tasks, button_show_shutdown],
                        [popup_shutdown, button_shutdown_no, button_shutdown_yes],
                        [background_UI]
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
t2 = threading.Thread( target = shutdown_thread, args = (button_shutdown_pressed, shutdown_confirmed))

t2.start()
t1.start()

# TODO - make a batch script so that we'll have the ultimate user-friendliness
# TODO - make a task history U/I element to show the current tasks collected for a given algorithm