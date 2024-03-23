#This module contains the 
import numpy as np 
from typing import Optional

class RateMonotonic():
    """
    Computes the cpu scheduling with the rate monotonic algorithm

    Parameters
    ----------
    periods: np.ndarray
        A 1d array of shape (num_task,) that contains periods for each task

    wc_exec_time: np.ndarray
        A 1d array of shape (num_task,) that contains worst case execution 
        time for each task

    end_time: float
        Denoting when the simulation should end.

    Attributes
    ----------
    ready_queue
        A 2d array of shape (N,3), where N represents the number of tasks in 
        the ready queue and it is dynamic. Each of the three columns represent
        the task_number, task_period and task_remaining_execution_time in that 
        order

    ToDo
    --------
    -Need to identify the deadlines and return with dictionary [extra feature]
    -Need to identify stop running of tasks by setting end time as a new period [bug]
    """

    def __init__(self,
                 periods: np.ndarray, 
                 wc_exec_time: np.ndarray, 
                 end_time: float):
        self.periods=periods
        self.wc_exec_time=wc_exec_time
        self.end_time=end_time 
        #Initializing a ready queue with all tasks starting at time 0
        self.ready_queue=np.array([[i,per,exec_t] for i,(per,exec_t) in enumerate(zip(periods,self.wc_exec_time))])

    def _insert_task(self,task:np.ndarray):
        """
        Inserts new task to the ready_queue.

        Parameters
        -----------
        task: np.ndarray
            A 1d array of shape (3,) that contains task_number, task_period 
            and task_remaining_execution_time in that order.
          
        """
        self.ready_queue=np.concatenate([self.ready_queue,[task]])

    def _get_task(self) -> Optional[np.ndarray]:
        """
        Extracts the running task from the ready queue. Deletes running task 
        from the ready queue. Running task is chosen based on lowest period 
        of the task. If ready queue is empty return None

        Returns
        -------
        running_task: np.ndarray or None 
            A 1d array of shape (3,) that contains task_number, task_period 
            and task_remaining_execution_time in that order. If ready queue 
            is empty returns None. 

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

        Return 
        ----------
        computed_results: np.array
            A 2d array of shape (N,4) where N denotes the number of task that have 
            been run. This is determined based on self.end_time. Each column represents
            the task_num, start_time, end_time and frequency in that order. Note the 
            frequency here is always one.

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
                nearest_release=next_deadlines[nearest_task]

                #inserting nearest task to ready queue
                self._insert_task([nearest_task,
                                   self.periods[nearest_task],
                                   self.wc_exec_time[nearest_task]])
                
                #jumping current time to nearest deadline 
                current_time=nearest_release
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
                                       self.wc_exec_time[interrupting_task]])

                    #inserting running task in ready queue if execution is not complete 
                    if running_remain_exec>0:
                        self._insert_task([task_num,
                                           period,
                                           running_remain_exec])
                    
                    #storing the execution of running task before interruption 
                    temp_results=[task_num,current_time,interrupting_release,1]
                    current_time=interrupting_release
                    
                    #incrementing counter to reflect new deadline of interrupting task
                    period_counter[interrupting_task]+=1

            
            computed_results.append(temp_results)

        return np.array(computed_results)

class FCFS():
    """
    Computes the cpu scheduling with the first come first serve algorithm 

    Parameters
    ----------
    release_time: np.ndarray
        A 1d array of shape (num_task,) that contains release for each task

    wc_exec_time: np.ndarray
        A 1d array of shape (num_task,) that contains worst case execution 
        time for each task
    
    ToDo
    --------
    -Need to identify the deadlines and return with dictionary [extra feature]

    """

    def __init__(self,release_time: np.ndarray, wc_exec_time: np.ndarray):
        self.release_time=release_time
        self.wc_exec_time=wc_exec_time

    def compute(self):
        """
        Computes the scheduling base on the first come first serve algo scheduling algorithm

        Return 
        ----------
        computed_results: np.array
            A 2d array of shape (num_task,4). Each column represents the task_num, start_time, 
            end_time and frequency in that order. Note the frequency here is always one.

        """
        #sorting tasks based on release time 
        task_sorted=np.argsort(self.release_time)
        current_time=0
        computed_results=[]

        for task in task_sorted:
            release = self.release_time[task]
            #checking if current time is less than release time of task 
            if current_time<release:
                start_time=release
            else:
                start_time=current_time
            wc_exec_time=self.wc_exec_time[task]

            #storing task execution within computed results
            computed_results.append([task,start_time,start_time+wc_exec_time,1])

            #updating current tiem 
            current_time=start_time+wc_exec_time    

        computed_results=np.array(computed_results,dtype=float)

        return computed_results


ALGO_MAPPING={'rate_monotonic':RateMonotonic,
              'first_come_first_serve':FCFS}

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
         "wc_exec_time": np.array 1d, -> all
         "release_time": np.array 1d, -> FCFS
         "end_time": int, -> RM
         "periods": np.array 1d, -> RM and CycleEDF
         "invoc_time": np.array 2d, -> CycleEDF
         "frequency": np.array 1d, -> CycleEDF
          }
    
    Return 
    --------
    computed_results: np.array
        A 2d array of shape (N,4), where N denotes the number of task invocations. 
        Each of the 4 columns represent the task_num, start_time, end_time and 
        frequency in that order. 

        An example output is presented below:
        [[Task_num,start_time,task_end_time,frequency],
         [Task_num,start_time,task_end_time,frequency],
         ...]
        
    """
    #extracting string for cpu scheduling algorithm 
    algo=task_info['scheduling_algo']
    #deleting cpu scheduling algorithm to pass task info dictionary as **kwargs
    del task_info['scheduling_algo']
    #initializing the class associated with the chosen cpu scheduling algorithm 
    cpu_scheduler=ALGO_MAPPING[algo](**task_info)
    #computing results of cpu scheduling algorithm
    computed_results=cpu_scheduler.compute()

    return computed_results
