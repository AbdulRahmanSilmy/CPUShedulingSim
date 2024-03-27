#This module contains the 
import numpy as np 
from typing import Optional

class CycleEDF():
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
                 invocations: np.ndarray):
        self.periods=periods
        self.wc_exec_time=wc_exec_time
        self.bc_exec_time=wc_exec_time
        #invocatios is a 2d numpy array each row representing 
        #the execuation of tasks in that order
        self.invocations=invocations
        #Initializing a ready queue with all tasks starting at time 0
        self.ready_queue=np.array([[i,per,inv_exec_t] for i,(per,inv_exec_t) in enumerate(zip(periods,self.invocations[0,:]))])

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
            ready_deadline=self.ready_queue[:,1]
            min_index=np.argmin(ready_deadline)
            running_task=self.ready_queue[min_index]

            #deleting running task from ready queue 
            self.ready_queue=np.delete(self.ready_queue,min_index,axis=0)
        else:
            #returning None if ready queue is empty 
            running_task=None

        return running_task
    
    def _compute_frequency(self, running_task):
        task_num = running_task[0]

        def sum_other_tasks(other_tasks):
            sum = 0
            for task in other_tasks:
                task_num = task[0]
                freq = self.bc_exec_time[task_num]/self.periods[task_num]
                sum += freq
            return sum

        other_tasks = np.delete(self.ready_queue.copy(),task_num,0)
        freq= self.wc_exec_time[task_num]/self.periods[task_num] + sum_other_tasks(other_tasks)
        # self.bc_exec_time[task_num] = self.
        return freq

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
        dict_info={}
        computed_results=[]
        #setting up period counter to keep track of deadlines 
        period_counter=np.ones(self.periods.shape,dtype=int)

        current_time=0
        #change: end simulation with end of invocation time of all task 
        while current_time<self.end_time:
            
            next_deadlines=self.periods*period_counter
            #extracting running task from ready queue
            running_task=self._get_task()

            if running_task is None:
                #finding nearest task if ready queue is empty 
                nearest_task=np.argmin(next_deadlines)
                nearest_release=next_deadlines[nearest_task]

                #updating period counter of nearest task to reflect new deadline
                period_counter[nearest_task]+=1

                nearest_deadline=self.periods[nearest_task]*period_counter[nearest_task]
                #inserting nearest task to ready queue
                self._insert_task([nearest_task,
                                   nearest_deadline,
                                   self.wc_exec_time[nearest_task]])
                
                #jumping current time to nearest deadline 
                current_time=nearest_release
                

            else:
                #if running task is valid/ready queue is not empty 
                #extracting details from running task
                task_num=running_task[0]
                deadline=running_task[1]
                inv_exec_t=running_task[2]

                frequency=self._compute_frequency(inv_exec_t,task_num)
                exec_t=self._compute_exec_t(frequency,inv_exec_t)

                #end time if running task runs till completion 
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

                    #change: maybe remaining exec time should be stored based on F=1
                    #calculating remaining execution time of iterrupting running task
                    running_remain_exec=task_end_time-interrupting_release

                    #incrementing counter to reflect new deadline of interrupting task
                    period_counter[interrupting_task]+=1
                    interrupting_deadline=self.periods[interrupting_task]*period_counter[interrupting_deadline]
                    #inserting interrupting task into ready queue 
                    self._insert_task([interrupting_task,
                                       interrupting_deadline,
                                       self.wc_exec_time[interrupting_task]])

                    #inserting running task in ready queue if execution is not complete 
                    if running_remain_exec>0:
                        self._insert_task([task_num,
                                           deadline,
                                           running_remain_exec])
                        
                    #dict_info=self._check_missed_deadline()
                    #storing the execution of running task before interruption 
                    temp_results=[task_num,current_time,interrupting_release,1]
                    current_time=interrupting_release
                    
                    

            
            computed_results.append(temp_results)

        return np.array(computed_results),dict_info

class EDF():
    """
    Computes the cpu scheduling with the earliest deadline first algorithm

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
        the task_number, task_deadline and task_remaining_execution_time in that 
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
        self.end_time = end_time
       
        #Initializing a ready queue with all tasks starting at time 0
        self.ready_queue=np.array([[i,per,exec_t] for i,(per,exec_t) in enumerate(zip(periods,self.wc_exec_time))])
        self.computed_results=np.array([[]])

    def _insert_task(self,task:np.ndarray):
        """
        Inserts new task to the ready_queue.

        Parameters
        -----------
        task: np.ndarray
            A 1d array of shape (3,) that contains task_number, task_deadline 
            and task_remaining_execution_time in that order.
          
        """
        self.ready_queue=np.concatenate([self.ready_queue,[task]])

    def _get_task(self) -> Optional[np.ndarray]:
        """
        Extracts the running task from the ready queue. Deletes running task 
        from the ready queue. Running task is chosen based on nearest deadline 
        of the tasks. If ready queue is empty returns None

        Returns
        -------
        running_task: np.ndarray or None 
            A 1d array of shape (3,) that contains task_number, task_deadline 
            and task_remaining_execution_time in that order. If ready queue 
            is empty returns None. 

        """
        #checking if ready queue had tasks 
        if self.ready_queue.size>0:
            #extacting running task based on lowest period 
            ready_deadline=self.ready_queue[:,1]
            min_index=np.argmin(ready_deadline)
            running_task=self.ready_queue[min_index]

            #deleting running task from ready queue 
            self.ready_queue=np.delete(self.ready_queue,min_index,axis=0)
        else:
            #returning None if ready queue is empty 
            running_task=None

        return running_task
    
    def _insert_computed_results(self,new_results):
        """
        Inserting new results into computed results. If new results task and 
        the most recent task in computed_results are contiguous in time they 
        are merged together. 

        Parameters
        ----------
        new_results: list
            A list of of shape (4,) containing the task number, start time,
            end time and frequency in that order
        """

        #check if computed results is empty 
        if self.computed_results.size>0:
            #if not empty extracts the most recent row in the 
            #computed results 2d array 
            recent_result=self.computed_results[-1]
            #checking if the most recent task in computed results
            #match the task in temp_results
            if recent_result[0]==new_results[0]:
                #check if task are contiguous in time
                if recent_result[2]==new_results[1]:
                    #if contiguous in time just altering end time of the 
                    #of the recent row in computed results 
                    recent_result[2]=new_results[2]
                else:
                    self.computed_results=np.concatenate([self.computed_results,
                                                     [new_results]])

            else:
                #if they are different task adding to
                self.computed_results=np.concatenate([self.computed_results,
                                                     [new_results]])
            
        else:
            self.computed_results=np.array([new_results])
            



    def compute(self) -> np.ndarray:
        """
        Computes the scheduling base on the earliest deadline first cpu scheduling 
        algorithm

        Return 
        ----------
        computed_results: np.array
            A 2d array of shape (N,4) where N denotes the number of task that have 
            been run. This is determined based on self.end_time. Each column represents
            the task_num, start_time, end_time and frequency in that order. Note the 
            frequency here is always one.

        """
        dict_info={}
        #computed_results=[]
        #setting up period counter to keep track of deadlines 
        period_counter=np.ones(self.periods.shape,dtype=int)

        current_time=0
        #change: end simulation with end of invocation time of all task 
        while current_time<self.end_time:
            
            next_deadlines=self.periods*period_counter
            #extracting running task from ready queue
            running_task=self._get_task()

            if running_task is None:
                #finding nearest task if ready queue is empty 
                nearest_task=np.argmin(next_deadlines)
                nearest_release=next_deadlines[nearest_task]

                #updating period counter of nearest task to reflect new deadline
                period_counter[nearest_task]+=1

                nearest_deadline=self.periods[nearest_task]*period_counter[nearest_task]
                #inserting nearest task to ready queue
                self._insert_task([nearest_task,
                                   nearest_deadline,
                                   self.wc_exec_time[nearest_task]])
                
                #jumping current time to nearest deadline 
                current_time=nearest_release
                

            else:
                #if running task is valid/ready queue is not empty 
                #extracting details from running task
                task_num=running_task[0]
                deadline=running_task[1]
                exec_t=running_task[2]

                #end time if running task runs till completion 
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

                    #change: maybe remaining exec time should be stored based on F=1
                    #calculating remaining execution time of iterrupting running task
                    running_remain_exec=task_end_time-interrupting_release

                    #incrementing counter to reflect new deadline of interrupting task
                    period_counter[interrupting_task]+=1
                    interrupting_deadline=self.periods[interrupting_task]*period_counter[interrupting_task]
                    #inserting interrupting task into ready queue 
                    self._insert_task([interrupting_task,
                                       interrupting_deadline,
                                       self.wc_exec_time[interrupting_task]])

                    #inserting running task in ready queue if execution is not complete 
                    if running_remain_exec>0:
                        self._insert_task([task_num,
                                           deadline,
                                           running_remain_exec])
                        
                    #dict_info=self._check_missed_deadline()
                    #storing the execution of running task before interruption 
                    temp_results=[task_num,current_time,interrupting_release,1]
                    current_time=interrupting_release
                    
                self._insert_computed_results(temp_results)
                #computed_results.append(temp_results)

        return np.array(self.computed_results),dict_info

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
        dict_info={}
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

                #end time if running task runs till completion 
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
                        
                    #dict_info=self._check_missed_deadline()
                    #storing the execution of running task before interruption 
                    temp_results=[task_num,current_time,interrupting_release,1]
                    current_time=interrupting_release
                    
                    #incrementing counter to reflect new deadline of interrupting task
                    period_counter[interrupting_task]+=1

            
                computed_results.append(temp_results)

        return np.array(computed_results),dict_info

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
        dict_info={}
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

        return computed_results,dict_info


ALGO_MAPPING={'rate_monotonic':RateMonotonic,
              'first_come_first_serve':FCFS,
              'earliest_deadline_first':EDF}

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
    computed_results,dict_info=cpu_scheduler.compute()

    return computed_results,dict_info
