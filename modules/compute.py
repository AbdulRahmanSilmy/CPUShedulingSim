#This module contains the 
import numpy as np 

def _FCFS(task_info:dict) -> np.ndarray:
    """
    Computes the scheduling base on the first come first serve
    
    Parameters
    ----------

    task_info: dict 
        A dictionary containing both the scheduling algorithm and task details

        The dictionary should contain the following key strings and value types
        presented below:

        {"release_time": np.array 1d,
         "wc_exec_time": np.array 1d}

    
    Return 
    ----------
    computed_results: np.array
        A 2d numpy array containing the computed results.

    """

    release_time=task_info['release_time']
    wx_exec_time=task_info['wc_exec_time']
    task_sorted=np.argsort(release_time)
    current_time=0
    computed_results=[]

    for task in task_sorted:
        release = release_time[task]
        #checking if current time is less than release time of task 
        if current_time<release:
            start_time=release
        else:
            start_time=current_time
        exec_time=wx_exec_time[task]
        computed_results.append([task,start_time,start_time+exec_time,1])
        current_time=start_time+exec_time    

    computed_results=np.array(computed_results,dtype=float)

    return computed_results

def _rate_monotonic(task_info:dict) -> np.ndarray:
    """
    Computes the scheduling base on the rate monotonic cpu scheduling algorithm

    Parameters
    ----------

    task_info: dict 
        A dictionary containing both the scheduling algorithm and task details

        The dictionary should contain the following key strings and value types
        presented below:

        {"periods": np.array 1d,
         "wc_exec_time": np.array 1d,
         "end_time": float}

    
    Return 
    ----------
    computed_results: np.array
        A 2d numpy array containing the computed results.

    Note
    ----
    How to handle task with the same period?


    """

    computed_results=np.array([[]])

    return computed_results    

ALGO_MAPPING={'rate_monotonic':_rate_monotonic,
              'first_come_first_serve':_FCFS}

def cpu_scheduling_compute(task_info: dict) -> np.ndarray:
    """
    Computes the scheduling based on the cpu scheduling algorithm 
    and task details in task_info

    Parameters
    ----------

    task_info: dict 
        A dictionary containing both the scheduling algorithm and task details

        The dictionary and with all the possible the key string and value type 
        is presented below:

        {"sceduling_algo": str, -> all
         "periods": np.array 1d, -> RM
         "wc_exec_time": np.array 1d, -> all
         "invoc_time": np.array 2d,
         "frequency": np.array 1d,
         "release_time": np.array 1d, -> FCFS
         "end_time": int ->RM }
    
    Return 
    --------
    computed_results: np.array
        A 2d numpy array containing the computed results. Each lower dimension 
        contains the following 4 items and their associated type:

        Task_num -> string denoting the task number
        start_time -> float 
        end_time -> float
        frequency -> float 

        An example output is presented below:
        [[Task_num,start_time,end_time,frequency],
         [Task_num,start_time,end_time,frequency],
         ...]
        
    """

    algo=task_info['scheduling_algo']

    computed_results=ALGO_MAPPING[algo](task_info)

    return computed_results
