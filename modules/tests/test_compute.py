from ..compute import cpu_scheduling_compute
import pytest
import numpy as np

@pytest.mark.parametrize("task_info, expected_results",
                         [({'release_time':[1,3,2,15,30],
                            'wc_exec_time':[2,4,5,3,9]}, 
                            np.array([[ 0.,  1.,  3.,  1.],
                                      [ 2.,  3.,  8.,  1.],
                                      [ 1.,  8., 12.,  1.],
                                      [ 3., 15., 18.,  1.],
                                      [ 4., 30., 39.,  1.]]))])
def test_FCFS(task_info,expected_results):
    task_info["scheduling_algo"]='first_come_first_serve'
    results,dict_info=cpu_scheduling_compute(task_info)

    assert np.array_equal(results,expected_results), "computed results don't match expected results" 


@pytest.mark.parametrize("task_info, expected_results",
                         [({'periods':np.array([8,5,10]),
                            'wc_exec_time':np.array([1,2,2]),
                            'end_time':15}, 
                            np.array([[ 1,  0,  2,  1],
                                      [ 0,  2,  3,  1],
                                      [ 2,  3,  5,  1],
                                      [ 1,  5,  7,  1],
                                      [ 0,  8,  9,  1],
                                      [ 1, 10, 12,  1],
                                      [ 2, 12, 14,  1]])),
                          ({"periods": np.array([25,35,60,105]),
                            "wc_exec_time": np.array([5,8,20,15]),
                            "end_time": 100}, 
                            np.array([[ 0,  0,  5,  1],
                                      [ 1,  5, 13,  1],
                                      [ 2, 13, 25,  1],
                                      [ 0, 25, 30,  1],
                                      [ 2, 30, 35,  1],
                                      [ 1, 35, 43,  1],
                                      [ 2, 43, 46,  1],
                                      [ 3, 46, 50,  1],
                                      [ 0, 50, 55,  1],
                                      [ 3, 55, 60,  1],
                                      [ 2, 60, 70,  1],
                                      [ 1, 70, 75,  1],
                                      [ 0, 75, 80,  1],
                                      [ 1, 80, 83,  1],
                                      [ 2, 83, 93,  1],
                                      [ 3, 93, 99,  1]])),
                          #check if it merges contiguous blocks from the same task
                          ({"periods": np.array([8,15,20,22]), 
                            "wc_exec_time": np.array([1,3,4,6]),
                            "end_time": 55}, 
                            np.array([[ 0,  0,  1,  1],
                                      [ 1,  1,  4,  1],
                                      [ 2,  4,  8,  1],
                                      [ 0,  8,  9,  1],
                                      [ 3,  9, 15,  1],
                                      [ 1, 15, 16,  1],
                                      [ 0, 16, 17,  1],
                                      [ 1, 17, 19,  1],
                                      [ 2, 20, 24,  1],
                                      [ 0, 24, 25,  1],
                                      [ 3, 25, 30,  1],
                                      [ 1, 30, 32,  1],
                                      [ 0, 32, 33,  1],
                                      [ 1, 33, 34,  1],
                                      [ 3, 34, 35,  1],
                                      [ 0, 40, 41,  1],
                                      [ 2, 41, 45,  1],
                                      [ 1, 45, 48,  1],
                                      [ 0, 48, 49,  1],
                                      [ 3, 49, 55,  1]]))])
def test_RM(task_info,expected_results):
    task_info["scheduling_algo"]='rate_monotonic'
    results,dict_info=cpu_scheduling_compute(task_info)

    assert np.array_equal(results,expected_results), "computed results don't match expected results" 


@pytest.mark.parametrize("task_info, expected_results",
                         [({'periods':np.array([50,40,30]),
                            'wc_exec_time':np.array([12,10,10]),
                            'end_time':120}, 
                            np.array([[  2,   0,  10,   1],
                                      [  1,  10,  20,   1],
                                      [  0,  20,  32,   1],
                                      [  2,  32,  42,   1],
                                      [  1,  42,  52,   1],
                                      [  0,  52,  60,   1],
                                      [  2,  60,  70,   1],
                                      [  0,  70,  74,   1],
                                      [  1,  80,  90,   1],
                                      [  2,  90, 100,   1],
                                      [  0, 100, 112,   1]]))])
def test_EDF(task_info,expected_results):
    task_info["scheduling_algo"]='earliest_deadline_first'
    results,dict_info=cpu_scheduling_compute(task_info)

    assert np.array_equal(results,expected_results), "computed results don't match expected results" 