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


