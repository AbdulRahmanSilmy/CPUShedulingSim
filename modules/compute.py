#This module contains the 
import numpy as np 
from typing import Optional
from abc import ABC, abstractmethod

class CPUScheduler(ABC):
    def __init__(self,wc_exec_time,periods,invocations=None,end_time=None):
        self.wc_exec_time=wc_exec_time
        self.periods=periods
        if invocations is None:
            self.invocations=None
            self.num_invocations=np.inf
            self.end_time=end_time
        else:
            self.invocations=np.array(invocations)
            self.num_invocations=self.invocations.shape[0]
            self.end_time=np.inf
        
        self._initialize_ready_queue()
        self.computed_results=np.array([[]])
        self.dict_info={}

    @abstractmethod
    def _compute_frequency(self,inv_exec_t,task_num):
        pass

    @abstractmethod
    def _insert_nearest_task(self,nearest_task):
        pass

    @abstractmethod
    def _insert_interrupting_task(self,interrupting_task):
        pass
    
    @abstractmethod
    def _initialize_ready_queue(self):
        pass
    
    @abstractmethod
    def _check_schedulability(self):
        pass

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
            ready_priority=self.ready_queue[:,1]
            min_index=np.argmin(ready_priority)
            running_task=self.ready_queue[min_index]

            #deleting running task from ready queue 
            self.ready_queue=np.delete(self.ready_queue,min_index,axis=0)
        else:
            #returning None if ready queue is empty 
            running_task=None

        return running_task

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
            #checks if new results and recent result contain contiguous blocks of the 
            #same tasks
            if recent_result[0]==new_results[0] and recent_result[2]==new_results[1]:
                #merging contiguous blocks of the same task
                recent_result[2]=new_results[2]
         
            else:
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
        self._check_schedulability()
        #setting up period counter to keep track of deadlines 
        self.period_counter=np.ones(self.periods.shape,dtype=int)
        self.inv_counter=np.zeros(self.periods.shape,dtype=int)

        current_time=0
        #change: end simulation with end of invocation time of all task 
        while any(self.inv_counter<self.num_invocations) and current_time<self.end_time:

            next_deadlines=self.periods*self.period_counter
            #extracting running task from ready queue
            running_task=self._get_task()

            if running_task is None:
                #finding nearest task if ready queue is empty
                nearest_task=np.argmin(next_deadlines)
                nearest_release=next_deadlines[nearest_task]

                if self.inv_counter[nearest_task]<self.num_invocations:
                    #jumping current time to nearest deadline 
                    current_time=nearest_release
                    self._insert_nearest_task(nearest_task)
                    
                #updating period counter of nearest task to reflect new deadline
                self.period_counter[nearest_task]+=1
                
            else:
                #if running task is valid/ready queue is not empty 
                #extracting details from running task
                task_num=int(running_task[0])
                deadline=running_task[1]
                inv_exec_t=running_task[2]

                exec_t,freq=self._compute_frequency(inv_exec_t,task_num)

                #end time if running task runs till completion 
                task_end_time=current_time+exec_t

                #checks is running task is interrupted by upcoming deadlines
                if all(task_end_time<next_deadlines):
                    #if not interrupted storing the execution of running task
                    temp_results=[task_num,current_time,task_end_time,freq]
                    self._insert_computed_results(temp_results)
                    current_time = task_end_time
                    self.inv_counter[task_num]+=1

                else:
                    #if task is interrupted 
                    #finding immediate task 
                    interrupting_task=np.argmin(next_deadlines)
                    interrupting_release=next_deadlines[interrupting_task]

                    #change: maybe remaining exec time should be stored based on F=1
                    #calculating remaining execution time of iterrupting running task
                    running_remain_exec=task_end_time-interrupting_release
                    running_remain_exec=running_remain_exec*freq

                    if self.inv_counter[interrupting_task]<self.num_invocations:
                        #extracting invocation time
                        self._insert_interrupting_task(interrupting_task)
                        
                    #incrementing counter to reflect new deadline of interrupting task
                    self.period_counter[interrupting_task]+=1


                    #inserting running task in ready queue if execution is not complete 
                    if running_remain_exec>0:
                        self._insert_task([task_num,
                                           deadline,
                                           running_remain_exec])
                    else:
                        self.inv_counter[task_num]+=1
                    
                    deadline_missed, task_missed = self._check_missed_deadline()
                    if deadline_missed:
                        dict_info = {"missed_task_num": float(task_missed), "miss_occurance": interrupting_release*(self.period_counter[interrupting_task]-1)}
                        print(dict_info)
                    #storing the execution of running task before interruption 
                    if current_time!=interrupting_release:
                        temp_results=[task_num,current_time,interrupting_release,freq]
                        self._insert_computed_results(temp_results)
                    current_time=interrupting_release
                    if deadline_missed:
                        break
                    

        return self.computed_results,self.dict_info

    def _check_missed_deadline(self):
        # def rateMonotonic_sufficient_sched():
        #     sumUtil = sum(self.wc_exec_time/self.periods)
        #     nTask = len(self.wc_exec_time)
        #     utilBound = nTask*(pow(2, (1/nTask))-1)
        #     return sumUtil <= utilBound
        # def cycleEDF_sufficient_sched():
        #     sumUtil = sum(self.wc_exec_time/self.periods)
        #     utilBound = 1
        #     return sumUtil <= utilBound
        u, c = np.unique(self.ready_queue[:,0], return_counts=True)
        duplicated_task = u[c > 1]
        duplicated_task+=1
        return duplicated_task.size > 0, duplicated_task
    
class CycleEDF(CPUScheduler):
    """
    Computes the cpu scheduling with the Cycle Conservative earliest 
    deadline first algorithm.

    Parameters
    ----------
    periods: np.ndarray
        A 1d array of shape (num_task,) that contains periods for each task

    wc_exec_time: np.ndarray
        A 1d array of shape (num_task,) that contains worst case execution 
        time for each task

    invocations: np.ndarray 
        A 2d array of shape (num_invocations, num_task) where each row represents
        the same invocations times for all tasks. 

    Attributes
    ----------
    bc_exec_time: np.array
        A 1d array of shape (num_task,) that contains best case execution 
        time for each task. Initialised to be equal to wc_exec_time at the start.

    """

    def __init__(self,
                 periods: np.ndarray, 
                 wc_exec_time: np.ndarray, 
                 invocations: Optional[np.ndarray]):
        
        super().__init__(periods=periods,
                         wc_exec_time=wc_exec_time,
                         invocations=invocations,
                         end_time=None)
        
        
        self.bc_exec_time=np.array(wc_exec_time)

    def _initialize_ready_queue(self):
        """
        Initiliazed the ready queue will be used in the parent class CPUScheduler
        """
        self.ready_queue=np.array([[i,per,inv_exec_t] for i,(per,inv_exec_t) in enumerate(zip(self.periods,self.invocations[0,:]))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        utilization_bound = 1
        if utilization<=utilization_bound:
            result="yes"
        else:
            result="no"
        
        self.dict_info['schedulability']=result


    def _compute_frequency(self,inv_exec_t,task_num):
        """
        Computes the frequency and resulting execution time. It is used by the 
        parent class CPUScheduler.

        Parameters
        ----------
        inv_exec_t: float
            The invocation execution time of the task.
        task_num: int
            The task number 
        
        Returns
        -------
        exec_t: float
            The execution time after calculating frequency used.
        
        freq: float
            The frequency used to conserve energy. 
        """
        task_num=int(task_num)
        prior_bc=self.bc_exec_time[task_num].copy()
        self.bc_exec_time[task_num]=self.wc_exec_time[task_num].copy()
        freq=sum(self.bc_exec_time/self.periods)
        exec_t=inv_exec_t/freq

        if inv_exec_t<prior_bc:
            self.bc_exec_time[task_num]=inv_exec_t
        else:
            self.bc_exec_time[task_num]=prior_bc

        return exec_t,freq
    
    def _insert_nearest_task(self,nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        #extracting invocation time
        invocation_row=self.period_counter[nearest_task]
        inv_exec_t=self.invocations[invocation_row,nearest_task]
        
        nearest_deadline=self.periods[nearest_task]*(self.period_counter[nearest_task]+1)
        #inserting nearest task to ready queue
        self._insert_task([nearest_task,
                            nearest_deadline,
                            inv_exec_t])
        
    def _insert_interrupting_task(self,interrupting_task):
        """
        Inserting interrupting task into ready queue

        Parameters
        ----------
        interrupting_task: int
            The task number associated to the interrupting task
        """
        invocation_row=self.period_counter[interrupting_task]-1
        interrupting_exec_t=self.invocations[invocation_row,interrupting_task]
        
        interrupting_deadline=self.periods[interrupting_task]*(self.period_counter[interrupting_task]+1)
        #inserting interrupting task into ready queue 
        self._insert_task([interrupting_task,
                           interrupting_deadline,
                           interrupting_exec_t])

class EDF(CPUScheduler):
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
        Denoting when the simulation should end   

    """

    def __init__(self,
                 periods: np.ndarray, 
                 wc_exec_time: np.ndarray, 
                 end_time: float):
        
        super().__init__(periods=periods,
                         wc_exec_time=wc_exec_time,
                         end_time=end_time,
                         invocations=None)
        
    
    def _initialize_ready_queue(self):
        """
        Initiliazed the ready queue will be used in the parent class CPUScheduler
        """
        #Initializing a ready queue with all tasks starting at time 0
        self.ready_queue=np.array([[i,per,exec_t] for i,(per,exec_t) in enumerate(zip(self.periods,self.wc_exec_time))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        utilization_bound = 1
        if utilization<=utilization_bound:
            result="yes"
        else:
            result="no"
        
        self.dict_info['schedulability']=result

    def _compute_frequency(self, inv_exec_t, task_num):
        """
        Computes the frequency and resulting execution time. It is used by the 
        parent class CPUScheduler. 

        Parameters
        ----------
        inv_exec_t: float
            The invocation execution time of the task.
        task_num: int
            The task number 
        
        Returns
        -------
        exec_t: float
            The execution time after calculating frequency used.
        
        freq: float
            The frequency used. 
        """
        exec_t=inv_exec_t
        freq=1
        return exec_t,freq
    
    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        nearest_deadline=self.periods[nearest_task]*(self.period_counter[nearest_task]+1)
        #inserting nearest task to ready queue
        self._insert_task([nearest_task,
                           nearest_deadline,
                           self.wc_exec_time[nearest_task]])
        
    def _insert_interrupting_task(self, interrupting_task):
        """
        Inserting interrupting task into ready queue

        Parameters
        ----------
        interrupting_task: int
            The task number associated to the interrupting task
        """
        interrupting_deadline=self.periods[interrupting_task]*(self.period_counter[interrupting_task]+1)
        #inserting interrupting task into ready queue 
        self._insert_task([interrupting_task,
                           interrupting_deadline,
                           self.wc_exec_time[interrupting_task]])

class RateMonotonic(CPUScheduler):
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
    ready_queue: np.ndarray 
        A 2d array of shape (N,3), where N represents the number of tasks in 
        the ready queue and it is dynamic. Each of the three columns represent
        the task_number, task_period and task_remaining_execution_time in that 
        order
    computed_results: np.array
        A 2d array of shape (N,4) where N denotes the number of task that have 
        been run. Each column represents the task_num, start_time, end_time and 
        frequency in that order. Note the frequency here is always one. Initially
        size of this array is zero. 

    ToDo
    --------
    -Need to identify the deadlines and return with dictionary [extra feature]
    -Need to identify stop running of tasks by setting end time as a new period [bug]
    """

    def __init__(self,
                 periods: np.ndarray, 
                 wc_exec_time: np.ndarray, 
                 end_time: float):
        
        super().__init__(periods=periods,
                         wc_exec_time=wc_exec_time,
                         end_time=end_time,
                         invocations=None)

    
    def _initialize_ready_queue(self):
        """
        Initiliazed the ready queue will be used in the parent class CPUScheduler
        """
        #Initializing a ready queue with all tasks starting at time 0
        self.ready_queue=np.array([[i,per,exec_t] for i,(per,exec_t) in enumerate(zip(self.periods,self.wc_exec_time))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        num_tasks=len(self.wc_exec_time)
        utilization_bound = num_tasks*(2**(1/num_tasks)-1)
        if utilization<=utilization_bound:
            result="yes"
        else:
            result="maybe"
        
        self.dict_info['schedulability']=result

    def _compute_frequency(self, inv_exec_t, task_num):
        """
        Computes the frequency and resulting execution time. It is used by the 
        parent class CPUScheduler. 

        Parameters
        ----------
        inv_exec_t: float
            The invocation execution time of the task.
        task_num: int
            The task number 
        
        Returns
        -------
        exec_t: float
            The execution time after calculating frequency used.
        
        freq: float
            The frequency used. 
        """
        exec_t=inv_exec_t
        freq=1
        return exec_t,freq
    
    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        #inserting nearest task to ready queue
        self._insert_task([nearest_task,
                           self.periods[nearest_task],
                           self.wc_exec_time[nearest_task]])
        
    def _insert_interrupting_task(self, interrupting_task):
        """
        Inserting interrupting task into ready queue

        Parameters
        ----------
        interrupting_task: int
            The task number associated to the interrupting task
        """
        #inserting interrupting task into ready queue 
        self._insert_task([interrupting_task,
                           self.periods[interrupting_task],
                           self.wc_exec_time[interrupting_task]])  

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
              'earliest_deadline_first':EDF,
              'CycleEDF':CycleEDF
              }

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
