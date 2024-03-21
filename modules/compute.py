#This module contains the 
import numpy as np 

def _insert_task(task,ready_queue):
    """
    Helper function for _rate_monotonic. Inserts new task to 
    the ready_queue. 
    """
    return np.concatenate([ready_queue,[task]])

def _get_task(ready_queue):
    """
    Helper function for _rate_monotonic. Gets the next task to be 
    run from the ready_queue
    """
    if ready_queue.shape[0]>0:
        ready_periods=ready_queue[:,1]
        min_index=np.argmin(ready_periods)
        task=ready_queue[min_index]
        ready_queue=np.delete(ready_queue,min_index,axis=0)
    else:
        task=None

    return task,ready_queue

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
    computed_results=[]
    periods=task_info['periods']
    exec_time=task_info['wc_exec_time']
    end_time=task_info['end_time']
    period_counter=np.ones(periods.shape,dtype=int)
    
    
    
    #initializing ready_queue 
    ready_queue=np.array([[i,per,0,exec_t] for i,(per,exec_t) in enumerate(zip(periods,exec_time))])


    current_time=0
    while current_time<end_time:
   
        next_deadlines=periods*period_counter

        task_details,ready_queue=_get_task(ready_queue)

        if task_details is None:

            immediate_task=np.argmin(next_deadlines)
            immediate_deadline=next_deadlines[immediate_task]

            ready_queue=_insert_task([immediate_task,
                                periods[immediate_task],
                                immediate_deadline,
                                exec_time[immediate_task]],
                                ready_queue)
            current_time=immediate_deadline
            period_counter[immediate_task]+=1
            
            
        else:
            
            task_num=task_details[0]
            period=task_details[1]
            exec_t=task_details[3]
            temp_time=current_time+exec_t


            if all(temp_time<next_deadlines):
                temp_results=[task_num,current_time,temp_time,1]
                current_time = temp_time

            else:
                immediate_task=np.argmin(next_deadlines)
                immediate_deadline=next_deadlines[immediate_task]
                remain_exec=temp_time-immediate_deadline

                #inserting new task because of deadline 
                ready_queue=_insert_task([immediate_task,
                                    periods[immediate_task],
                                    immediate_deadline,
                                    exec_time[immediate_task]],
                                    ready_queue)
                
                #inserting interrupted old task if exec time remains 
                if remain_exec>0:
                    ready_queue=_insert_task([task_num,
                                              period,
                                              immediate_deadline,
                                              remain_exec],
                                              ready_queue)


                temp_results=[task_num,current_time,immediate_deadline,1]
                current_time=immediate_deadline

                period_counter[immediate_task]+=1
        
      
        computed_results.append(temp_results)

    return np.array(computed_results)

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
