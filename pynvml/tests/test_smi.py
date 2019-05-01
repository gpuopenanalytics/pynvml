from pynvml.smi import *
import pytest
import os

# Fixture to initialize and finalize nvml
@pytest.fixture(scope='module')
def smi(request):
    return nvidia_smi.getInstance()

@pytest.fixture
def ngpus(smi):
    result = smi.DeviceQuery('count')['count']
    assert result > 0
    print('['+str(result)+' GPUs]', end =' ')
    return result

## ---------------------------- ##
##       Start Query Tests      ##
## ---------------------------- ##

# Test free-memory query
def test_query_memory(ngpus, smi):
    result = smi.DeviceQuery('memory.free')
    for i in range(ngpus):
        assert result['gpu'][i]['fb_memory_usage']['free'] >= 0


# Test gpu-utilization query
def test_gpu_utilization(get_count):
    def _gpu_util_query(j):
        return pytest.nvsmi.DeviceQuery('utilization.gpu')['gpu'][j]['utilization']['gpu_util']
    for i in range(pytest.ngpus):
        gpu_util = _gpu_util_query(i)
        assert(gpu_util >= 0)

# Test memory-utilization query
def test_memory_utilization(get_count):
    def _memory_util_query(j):
        return pytest.nvsmi.DeviceQuery('utilization.memory')['gpu'][j]['utilization']['memory_util']
    for i in range(pytest.ngpus):
        memory_util = _memory_util_query(i)
        assert(memory_util >= 0)

# Test tx memory-transfer utilization query
def test_tx_util(get_count):
    def _tx_util_query(j):
        return pytest.nvsmi.DeviceQuery()['gpu'][j]['pci']['tx_util']
    for i in range(pytest.ngpus):
        tx_util = _tx_util_query(i)
        assert(tx_util >= 0)

# Test rx memory-transfer utilization query
def test_rx_util(get_count):
    def _rx_util_query(j):
        return pytest.nvsmi.DeviceQuery()['gpu'][j]['pci']['rx_util']
    for i in range(pytest.ngpus):
        rx_util = _rx_util_query(i)
        assert(rx_util >= 0)

# Test pstate query
def test_pstate(get_count):
    def _pstate_query(j):
        return pytest.nvsmi.DeviceQuery('pstate')['gpu'][j]['performance_state']
    for i in range(pytest.ngpus):
        pstate = _pstate_query(i)
        assert(pstate[0] == 'P')

# Test temperature query
def test_temperature(get_count):
    def _temp_query(j):
        return pytest.nvsmi.DeviceQuery('temperature.gpu')['gpu'][j]['temperature']['gpu_temp']
    def _max_temp_query(j):
        return pytest.nvsmi.DeviceQuery('temperature.gpu')['gpu'][j]['temperature']['gpu_temp_max_threshold']
    for i in range(pytest.ngpus):
        temp = _temp_query(i)
        max_temp = _max_temp_query(i)
        assert((temp > 0) and (temp < max_temp))
