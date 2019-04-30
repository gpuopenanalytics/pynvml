from nvml.pynvml import *
import pytest

# Fixture to initialize and finalize nvml
@pytest.fixture(scope='module')
def nvml_init(request):
    nvmlInit()
    def nvml_close():
        nvmlShutdown()
    request.addfinalizer(nvml_close)

# Test nvmlSystemGetDriverVersion
def test_nvmlSystemGetDriverVersion(nvml_init):
    vsn = float(nvmlSystemGetDriverVersion().decode())
    assert((vsn > 396.0) and (vsn < 397.0)) # Developing with 396.44

# Test nvmlSystemGetDriverVersion (get GPU count)
@pytest.fixture
def get_gpu_count(nvml_init):
    pytest.ngpus = nvmlDeviceGetCount()
    print('[Detecting '+str(pytest.ngpus)+' GPUs]', end =' ')
    assert(pytest.ngpus>0)

# Test nvmlDeviceGetHandleByIndex
@pytest.fixture
def get_gpu_handles(nvml_init, get_gpu_count):
    pytest.handles = [ nvmlDeviceGetHandleByIndex(i) for i in range(pytest.ngpus) ]
    assert(len(pytest.handles)==pytest.ngpus)

# Test nvmlDeviceGetMemoryInfo
def test_nvmlDeviceGetMemoryInfo(nvml_init, get_gpu_count, get_gpu_handles):
    for i in range(pytest.ngpus):
        meminfo = nvmlDeviceGetMemoryInfo( pytest.handles[i] )
        assert((meminfo.used <= meminfo.free) and (meminfo.free <= meminfo.total))
