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
                                      [ 1, 10, 10,  1],
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
                                      [ 3, 93, 99,  1]]))])
def test_RM(task_info,expected_results):
    task_info["scheduling_algo"]='rate_monotonic'
    results,dict_info=cpu_scheduling_compute(task_info)

    assert np.array_equal(results,expected_results), "computed results don't match expected results" 