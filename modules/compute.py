"""
This modules contains classes and functions to compute the schedule time lines 
for a CPU Scheduling Simulator given certain task parameters. This simulator is 
an event driven simulator and hence saves on compute time by jumping in time 
to the next occurance of an event. 

The module is structures as follows:

- The ``CPUScheduler`` is an abstract class where CPU schedulers with premption can inherit from.
- The ``CycleEDF`` is a child class that compute the CPU schedule based on the Cycle Conservative
earliest deadline first algorithm.
- The ``EDF`` is a child class that compute the CPU schedule based on the earliest deadline 
first algorithm.  
- The ``RateMonotonic`` is a child class that compute the CPU schedule based on the 
Rate Monotonic algorithm.  
- The ``FCFS`` is a class that computeS the CPU schedule based on the firt come first serve 
algorithm.
It does not have premption. 
- The ``ALGO_MAPPING`` is a dictionary that maps user inputted strings to its corresponding class 
for each CPU scheduling algorithm.
- The ``cpu_scheduling_compute`` is the function that main.py interfaces with to receive 
the schedulability results. 

Git Contributors:
- AbdulRahmanSilmy
- JUULCat6969
- HajjSalad
- dynanomino 
"""
# This module contains the
from typing import Optional
from abc import ABC, abstractmethod
import numpy as np


class CPUScheduler(ABC):
    """
    This is an abstract class where CPU schedulers with premption can inherit from. 

    Parameters
    ----------
    wc_exec_time: np.ndarray
        A 1d array of shape (num_task,) that contains worst case execution 
        time for each task

    periods: np.ndarray
        A 1d array of shape (num_task,) that contains periods for each task

    invocations: np.ndarray 
        A 2d array of shape (num_invocations, num_task) where each row represents
        the same invocations times for all tasks. Currently only used for cycleEDF.

    end_time: float
        Denoting when the simulation should end. Currently only used by RM and EDF.
    
    """
    def __init__(self,
                 wc_exec_time: np.ndarray, 
                 periods: np.ndarray, 
                 invocations: Optional[np.ndarray] = None,
                 end_time: Optional[float] = None):
        self.wc_exec_time = wc_exec_time
        self.periods = periods
        if invocations is None:
            self.invocations = None
            self.num_invocations = np.inf
            self.end_time = end_time
        else:
            self.invocations = np.array(invocations)
            self.num_invocations = self.invocations.shape[0]
            self.end_time = np.inf

        self._initialize_ready_queue()
        self.computed_results = np.array([[]])
        self.dict_info = {}

    @abstractmethod
    def _compute_frequency(self, inv_exec_t, task_num):
        """
        Computes the frequency and resulting execution time. It is used by the 
        parent class CPUScheduler
        
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

    @abstractmethod
    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """

    @abstractmethod
    def _insert_interrupting_task(self, interrupting_task):
        """
        Inserting interrupting task into ready queue

        Parameters
        ----------
        interrupting_task: int
            The task number associated to the interrupting task
        """

    @abstractmethod
    def _initialize_ready_queue(self):
        """
        Initiliazed the ready queue.
        """

    @abstractmethod
    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """

    def _break_priority_tie(self, min_loc: np.ndarray) -> np.ndarray:
        """
        Breaks ties in the ready queue when there are more than one task with 
        the same highest priority. Breaks the tie by taking the difference between  
        the remaining execution time of the task and the wc_execution time and 
        picking the task with the biggest difference. 

        Parameters
        ---------
        min_loc: np.ndarray
            The row index values indicating the tasks that have the same highest 
            priority. 
        """
        sub_ready_queue = self.ready_queue[min_loc, :]
        sub_queue_rem_exec = sub_ready_queue[:, 2]
        sub_queue_wc_exec = self.wc_exec_time[sub_ready_queue[:, 0]]
        sub_ran_exec_t = sub_queue_wc_exec-sub_queue_rem_exec
        # picking task ran the most
        max_index = np.argmax(sub_ran_exec_t)
        running_task = sub_ready_queue[max_index]

        delete_index = min_loc[max_index]

        self.ready_queue = np.delete(self.ready_queue, delete_index, axis=0)

        return running_task

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
        # checking if ready queue had tasks
        if self.ready_queue.size > 0:
            # extacting running task based on lowest period
            ready_priority = self.ready_queue[:, 1]
            min_index = np.argmin(ready_priority)
            min_val = ready_priority[min_index]
            min_loc = np.where(ready_priority == min_val)[0]
            num_min = len(min_loc)

            if num_min > 1:
                running_task = self._break_priority_tie(min_loc)
            else:
                running_task = self.ready_queue[min_index]

                # deleting running task from ready queue
                self.ready_queue = np.delete(
                    self.ready_queue, min_index, axis=0)

        else:
            # returning None if ready queue is empty
            running_task = None

        return running_task

    def _insert_task(self, task: np.ndarray):
        """
        Inserts new task to the ready_queue.

        Parameters
        -----------
        task: np.ndarray
            A 1d array of shape (3,) that contains task_number, task_deadline 
            and task_remaining_execution_time in that order.

        """
        self.ready_queue = np.concatenate([self.ready_queue, [task]])

    def _insert_computed_results(self, new_results):
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

        # check if computed results is empty
        if self.computed_results.size > 0:
            # if not empty extracts the most recent row in the
            # computed results 2d array
            recent_result = self.computed_results[-1]
            # checks if new results and recent result contain contiguous blocks of the
            # same tasks
            if recent_result[0] == new_results[0] and recent_result[2] == new_results[1]:
                # merging contiguous blocks of the same task
                recent_result[2] = new_results[2]

            else:
                self.computed_results = np.concatenate([self.computed_results,
                                                       [new_results]])
        else:
            self.computed_results = np.array([new_results])

    def _check_missed_deadline(self,interrupting_release: float) -> bool:
        """
        Checks if deadlines are missed by inspecting if the ready queue has 
        duplicates of the same task. Returns a bool which is used as 
        flag to stop simulation if deadline is missed.

        Parameters
        ----------
        interrupting_release: float
            The time of the interrupt. 

        Returns
        -------
        deadline_missed: bool
            True if deadline is missed Fals otherwise
        """
        u, c = np.unique(self.ready_queue[:, 0], return_counts=True)
        duplicated_task = u[c > 1]
        duplicated_task += 1
        deadline_missed=duplicated_task.size > 0
        if deadline_missed:
            self.dict_info["missed_task_num"] = float(duplicated_task)
            self.dict_info["miss_occurance"] = interrupting_release
        return deadline_missed

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
        # setting up period counter to keep track of deadlines
        self.period_counter = np.ones(self.periods.shape, dtype=int)
        self.inv_counter = np.zeros(self.periods.shape, dtype=int)

        current_time = 0
        # change: end simulation with end of invocation time of all task
        while any(self.inv_counter < self.num_invocations) and current_time < self.end_time:

            next_deadlines = self.periods*self.period_counter
            # extracting running task from ready queue
            running_task = self._get_task()

            if running_task is None:
                # finding nearest task if ready queue is empty
                nearest_task = np.argmin(next_deadlines)
                nearest_release = next_deadlines[nearest_task]

                if self.inv_counter[nearest_task] < self.num_invocations:
                    # jumping current time to nearest deadline
                    current_time = nearest_release
                    self._insert_nearest_task(nearest_task)

                # updating period counter of nearest task to reflect new deadline
                self.period_counter[nearest_task] += 1

            else:
                # if running task is valid/ready queue is not empty
                # extracting details from running task
                task_num = int(running_task[0])
                deadline = running_task[1]
                inv_exec_t = running_task[2]

                exec_t, freq = self._compute_frequency(inv_exec_t, task_num)

                # end time if running task runs till completion
                task_end_time = current_time+exec_t

                # checks is running task is interrupted by upcoming deadlines
                if all(task_end_time < next_deadlines):
                    # if not interrupted storing the execution of running task
                    temp_results = [
                        task_num, current_time, task_end_time, freq]
                    self._insert_computed_results(temp_results)
                    current_time = task_end_time
                    self.inv_counter[task_num] += 1

                else:
                    # if task is interrupted
                    # finding immediate task
                    interrupting_task = np.argmin(next_deadlines)
                    interrupting_release = next_deadlines[interrupting_task]

                    # change: maybe remaining exec time should be stored based on F=1
                    # calculating remaining execution time of iterrupting running task
                    running_remain_exec = task_end_time-interrupting_release
                    running_remain_exec = running_remain_exec*freq

                    if self.inv_counter[interrupting_task] < self.num_invocations:
                        # extracting invocation time
                        self._insert_interrupting_task(interrupting_task)

                    # incrementing counter to reflect new deadline of interrupting task
                    self.period_counter[interrupting_task] += 1

                    # inserting running task in ready queue if execution is not complete
                    if running_remain_exec > 0:
                        self._insert_task([task_num,
                                           deadline,
                                           running_remain_exec])
                    else:
                        self.inv_counter[task_num] += 1
                   
                    # storing the execution of running task before interruption
                    if current_time != interrupting_release:
                        temp_results = [task_num, current_time,
                                        interrupting_release, freq]
                        self._insert_computed_results(temp_results)
                    current_time = interrupting_release

                    deadline_missed = self._check_missed_deadline(interrupting_release)
                    if deadline_missed:
                        break

        return self.computed_results, self.dict_info  


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

        self.bc_exec_time = np.array(wc_exec_time)

    def _initialize_ready_queue(self):
        """
        Initiliazed the ready queue will be used in the parent class CPUScheduler
        """
        self.ready_queue = np.array([[i, per, inv_exec_t] for i, (per, inv_exec_t) in enumerate(
            zip(self.periods, self.invocations[0, :]))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        utilization_bound = 1
        if utilization > utilization_bound:
            self.dict_info['warning'] = 'The sum of utilization of worst case execution time of all tasks >= 1'

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
            The frequency used to conserve energy. 
        """
        task_num = int(task_num)
        prior_bc = self.bc_exec_time[task_num].copy()
        self.bc_exec_time[task_num] = self.wc_exec_time[task_num].copy()
        freq = sum(self.bc_exec_time/self.periods)
        if freq > 1:
            freq = 1
        exec_t = inv_exec_t/freq

        if inv_exec_t < prior_bc:
            self.bc_exec_time[task_num] = inv_exec_t
        else:
            self.bc_exec_time[task_num] = prior_bc

        return exec_t, freq

    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        # extracting invocation time
        invocation_row = self.period_counter[nearest_task]
        inv_exec_t = self.invocations[invocation_row, nearest_task]

        nearest_deadline = self.periods[nearest_task] * \
            (self.period_counter[nearest_task]+1)
        # inserting nearest task to ready queue
        self._insert_task([nearest_task,
                           nearest_deadline,
                           inv_exec_t])

    def _insert_interrupting_task(self, interrupting_task):
        """
        Inserting interrupting task into ready queue

        Parameters
        ----------
        interrupting_task: int
            The task number associated to the interrupting task
        """
        invocation_row = self.period_counter[interrupting_task]-1
        interrupting_exec_t = self.invocations[invocation_row,
                                               interrupting_task]

        interrupting_deadline = self.periods[interrupting_task] * \
            (self.period_counter[interrupting_task]+1)
        # inserting interrupting task into ready queue
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
        # Initializing a ready queue with all tasks starting at time 0
        self.ready_queue = np.array([[i, per, exec_t] for i, (per, exec_t) in enumerate(
            zip(self.periods, self.wc_exec_time))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        utilization_bound = 1
        if utilization <= utilization_bound:
            result = "yes"
        else:
            result = "no"

        self.dict_info['schedulability'] = result

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
        exec_t = inv_exec_t
        freq = 1
        return exec_t, freq

    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        nearest_deadline = self.periods[nearest_task] * \
            (self.period_counter[nearest_task]+1)
        # inserting nearest task to ready queue
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
        interrupting_deadline = self.periods[interrupting_task] * \
            (self.period_counter[interrupting_task]+1)
        # inserting interrupting task into ready queue
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
        # Initializing a ready queue with all tasks starting at time 0
        self.ready_queue = np.array([[i, per, exec_t] for i, (per, exec_t) in enumerate(
            zip(self.periods, self.wc_exec_time))])

    def _check_schedulability(self):
        """
        Checking the schedulability and updating dict info returned by self.compute
        """
        utilization = sum(self.wc_exec_time/self.periods)
        num_tasks = len(self.wc_exec_time)
        utilization_bound = num_tasks*(2**(1/num_tasks)-1)
        if utilization <= utilization_bound:
            result = "yes"
        else:
            result = "maybe"

        self.dict_info['schedulability'] = result

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
        exec_t = inv_exec_t
        freq = 1
        return exec_t, freq

    def _insert_nearest_task(self, nearest_task):
        """
        Inserting nearest task into ready queue

        Parameters
        ----------
        nearest_task: int,
            The task number associated to the nearest task
        """
        # inserting nearest task to ready queue
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
        # inserting interrupting task into ready queue
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

    deadline: Optional[np.ndarray], default=None
        A 1d array of shape (num_task,) that contains rhe deadlines of the tasks. 
        If none it is each deadline is set to np.inf.

    ToDo
    --------
    -Need to identify the deadlines and return with dictionary [extra feature]

    """
    def __init__(self, 
                 release_time: np.ndarray, 
                 wc_exec_time: np.ndarray, 
                 deadlines: Optional[np.ndarray] = None):
        self.release_time = release_time
        self.wc_exec_time = wc_exec_time
        if deadlines is None:
            self.deadlines = np.repeat(np.inf, len(release_time))
        else:
            self.deadlines = deadlines
        self.dict_info = {}

    def compute(self):
        """
        Computes the scheduling base on the first come first serve algo scheduling algorithm

        Return 
        ----------
        computed_results: np.array
            A 2d array of shape (num_task,4). Each column represents the task_num, start_time, 
            end_time and frequency in that order. Note the frequency here is always one.

        """
        # sorting tasks based on release time
        task_sorted = np.argsort(self.release_time)
        current_time = 0
        computed_results = []

        for task in task_sorted:
            release = self.release_time[task]
            # checking if current time is less than release time of task
            if current_time < release:
                start_time = release
            else:
                start_time = current_time
            wc_exec_time = self.wc_exec_time[task]

            # Check missed deadlines
            if start_time+wc_exec_time > self.deadlines[task]:
                self.dict_info['schedulability'] = "no"
                self.dict_info["missed_task_num"] = task+1
                self.dict_info["miss_occurance"] = self.deadlines[task]
                # storing task execution within computed results
                computed_results.append(
                    [task, start_time, self.deadlines[task], 1])
                break
            else:
                self.dict_info['schedulability'] = "yes"
                # storing task execution within computed results
                computed_results.append(
                    [task, start_time, start_time+wc_exec_time, 1])

            # updating current tiem
            current_time = start_time+wc_exec_time

        computed_results = np.array(computed_results, dtype=float)

        return computed_results, self.dict_info


ALGO_MAPPING = {'rate_monotonic': RateMonotonic,
                'first_come_first_serve': FCFS,
                'earliest_deadline_first': EDF,
                'CycleEDF': CycleEDF
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
    # extracting string for cpu scheduling algorithm
    algo = task_info['scheduling_algo']
    # deleting cpu scheduling algorithm to pass task info dictionary as **kwargs
    del task_info['scheduling_algo']
    # initializing the class associated with the chosen cpu scheduling algorithm
    cpu_scheduler = ALGO_MAPPING[algo](**task_info)
    # computing results of cpu scheduling algorithm
    computed_results, dict_info = cpu_scheduler.compute()

    return computed_results, dict_info
