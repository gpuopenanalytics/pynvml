from pynvml_utils import nvidia_smi
import pytest


# Fixture to initialize and finalize nvml
@pytest.fixture(scope="module")
def smi(request):
    return nvidia_smi.getInstance()


@pytest.fixture
def ngpus(smi):
    result = smi.DeviceQuery("count")["count"]
    assert result > 0
    print("[" + str(result) + " GPUs]", end=" ")
    return result


## ---------------------------- ##
##       Start Query Tests      ##
## ---------------------------- ##

# Test free-memory query
def test_query_memory(ngpus, smi):
    result = smi.DeviceQuery("memory.free")
    for i in range(ngpus):
        assert result["gpu"][i]["fb_memory_usage"]["free"] >= 0


# Test gpu-utilization query
def test_gpu_utilization(ngpus, smi):
    for i in range(ngpus):
        result = smi.DeviceQuery("utilization.gpu")["gpu"][i]["utilization"]["gpu_util"]
        assert result >= 0


# Test memory-utilization query
def test_memory_utilization(ngpus, smi):
    for i in range(ngpus):
        result = smi.DeviceQuery("utilization.memory")["gpu"][i]["utilization"][
            "memory_util"
        ]
        assert result >= 0


# Test pstate query
def test_pstate(ngpus, smi):
    for i in range(ngpus):
        result = smi.DeviceQuery("pstate")["gpu"][i]["performance_state"]
        assert result[0] == "P"


# Test temperature query
def test_temperature(ngpus, smi):
    for i in range(ngpus):
        temp = smi.DeviceQuery("temperature.gpu")["gpu"][i]["temperature"]["gpu_temp"]
        max_temp = smi.DeviceQuery("temperature.gpu")["gpu"][i]["temperature"][
            "gpu_temp_max_threshold"
        ]
        assert (temp > 0) and (temp < max_temp)
