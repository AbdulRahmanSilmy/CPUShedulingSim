#This module contains the 
import numpy as np 
from typing import Optional

class RateMonotonic():

    def __init__(self,periods,wc_exec_time,end_time):
        self.periods=periods
        self.exec_time=wc_exec_time
        self.end_time=end_time 
        #Initializing a ready queue each row corresponding to a task
        #Each row containg the following elements:
        #[task_num,task_period,task_remaining_execution_time]
        self.ready_queue=np.array([[i,per,exec_t] for i,(per,exec_t) in enumerate(zip(periods,self.exec_time))])

    def _insert_task(self,task:np.ndarray):
        """
        Helper function for _rate_monotonic. Inserts new task to 
        the ready_queue. 
        """
        self.ready_queue=np.concatenate([self.ready_queue,[task]])

    def _get_task(self) -> Optional[np.ndarray]:
        """
        Helper function for _rate_monotonic. Gets the next task to be 
        run from the ready_queue
        """
        #checking if ready queue had tasks 
        if self.ready_queue.shape[0]>0:
            #extacting running task based on lowest period 
            ready_periods=self.ready_queue[:,1]
            min_index=np.argmin(ready_periods)
            running_task=self.ready_queue[min_index]

            #deleting running task from ready queue 
            self.ready_queue=np.delete(self.ready_queue,min_index,axis=0)
        else:
            #returning None if ready queue is empty 
            running_task=None

        return running_task

    def compute(self) -> np.ndarray:
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
             "task_end_time": float}


        Return 
        ----------
        computed_results: np.array
            A 2d numpy array containing the computed results.

        Note
        ----
        How to handle task with the same period?


        """
        computed_results=[]
        #setting up period counter to keep track of deadlines 
        period_counter=np.ones(self.periods.shape,dtype=int)
        

        current_time=0
        while current_time<self.end_time:
            
            next_deadlines=self.periods*period_counter
            #extracting running task from ready queue
            running_task=self._get_task()

            if running_task is None:
                #finding nearest task if ready queue is empty 
                nearest_task=np.argmin(next_deadlines)
                nearest_deadline=next_deadlines[nearest_task]

                #inserting nearest task to ready queue
                self._insert_task([nearest_task,
                                   self.periods[nearest_task],
                                   self.exec_time[nearest_task]])
                
                #jumping current time to nearest deadline 
                current_time=nearest_deadline
                #updating period counter of nearest task to reflect new deadline
                period_counter[nearest_task]+=1

            else:
                #if running task is valid/ready queue is not empty 
                #extracting details from running task
                task_num=running_task[0]
                period=running_task[1]
                exec_t=running_task[2]

                #end time is running task runs till completion 
                task_end_time=current_time+exec_t

                #checks is running task is interrupted by upcoming deadlines
                if all(task_end_time<next_deadlines):
                    #if not interrupted storing the execution of running task
                    temp_results=[task_num,current_time,task_end_time,1]
                    current_time = task_end_time

                else:
                    #if task is interrupted 
                    #finding immediate task 
                    interrupting_task=np.argmin(next_deadlines)
                    interrupting_release=next_deadlines[interrupting_task]

                    #calculating remaining execution time of iterrupting running task
                    running_remain_exec=task_end_time-interrupting_release

                    #inserting interrupting task into ready queue 
                    self._insert_task([interrupting_task,
                                       self.periods[interrupting_task],
                                       self.exec_time[interrupting_task]])

                    #inserting running task in ready queue if execution is not complete 
                    if running_remain_exec>0:
                        self._insert_task([task_num,
                                           period,
                                           running_remain_exec])
                    
                    #storing the execution of running task before interruption 
                    temp_results=[task_num,current_time,interrupting_release,1]
                    current_time=interrupting_release
                    
                    #incrementing counter to reflect new deadline
                    period_counter[interrupting_task]+=1

            
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


ALGO_MAPPING={'rate_monotonic':RateMonotonic,
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
         "task_end_time": int ->RM }
    
    Return 
    --------
    computed_results: np.array
        A 2d numpy array containing the computed results. Each lower dimension 
        contains the following 4 items and their associated type:

        Task_num -> string denoting the task number
        start_time -> float 
        task_end_time -> float
        frequency -> float 

        An example output is presented below:
        [[Task_num,start_time,task_end_time,frequency],
         [Task_num,start_time,task_end_time,frequency],
         ...]
        
    """

    algo=task_info['scheduling_algo']
    del task_info['scheduling_algo']
    cpu_scheduler=ALGO_MAPPING[algo](**task_info)
    computed_results=cpu_scheduler.compute()

    return computed_results
