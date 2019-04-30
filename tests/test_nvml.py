from pynvml.nvml import *
import pytest
import os

# Fixture to initialize and finalize nvml
@pytest.fixture(scope='module')
def nvml_init(request):
    nvmlInit()
    def nvml_close():
        nvmlShutdown()
    request.addfinalizer(nvml_close)

# Get GPU count
@pytest.fixture
def get_gpu_count(nvml_init):
    pytest.ngpus = nvmlDeviceGetCount()
    print('['+str(pytest.ngpus)+' GPUs]', end =' ')
    assert(pytest.ngpus>0)

# Get handles using nvmlDeviceGetHandleByIndex
@pytest.fixture
def get_gpu_handles(get_gpu_count):
    pytest.handles = [ nvmlDeviceGetHandleByIndex(i) for i in range(pytest.ngpus) ]
    assert(len(pytest.handles)==pytest.ngpus)

@pytest.fixture
def get_gpu_serials(get_gpu_handles):
    pytest.serials = [ nvmlDeviceGetSerial(pytest.handles[i]) for i in range(pytest.ngpus) ]
    assert(len(pytest.serials)==pytest.ngpus)

@pytest.fixture
def get_gpu_uuids(get_gpu_handles):
    pytest.uuids = [ nvmlDeviceGetUUID(pytest.handles[i]) for i in range(pytest.ngpus) ]
    assert(len(pytest.uuids)==pytest.ngpus)

@pytest.fixture
def get_gpu_pci_info(get_gpu_handles):
    pytest.pci_info = [ nvmlDeviceGetPciInfo(pytest.handles[i]) for i in range(pytest.ngpus) ]
    assert(len(pytest.pci_info)==pytest.ngpus)

## ---------------------------- ##
## Start Fucntion-pointer Tests ##
## ---------------------------- ##

# Test nvmlSystemGetNVMLVersion
def test_nvmlSystemGetNVMLVersion(nvml_init):
    vsn = 0.0
    vsn = float(nvmlSystemGetDriverVersion().decode())
    print('[NVML Version: '+str(vsn)+']', end =' ')
    assert(vsn!=0.0)

# Test nvmlSystemGetProcessName
def test_nvmlSystemGetProcessName(nvml_init):
    procname = None
    procname = nvmlSystemGetProcessName( os.getpid() )
    print('[Process: '+str(procname.decode())+']', end =' ')
    assert(procname!=None)

# Test nvmlSystemGetDriverVersion
def test_nvmlSystemGetDriverVersion(nvml_init):
    vsn = float(nvmlSystemGetDriverVersion().decode())
    print('[Driver Version: '+str(vsn)+']', end =' ')
    assert((vsn > 396.0) and (vsn < 397.0)) # Developing with 396.44

## Unit "Get" Functions (Skipping for now) ##

## Device "Get" Functions (Note: Some functions are fixtures, above) ##

# Test nvmlDeviceGetHandleBySerial
def test_nvmlDeviceGetHandleBySerial(get_gpu_serials):
    handles = [ nvmlDeviceGetHandleBySerial(pytest.serials[i]) for i in range(pytest.ngpus) ]
    assert(len(pytest.handles)==len(handles))

# Test nvmlDeviceGetHandleByUUID
def test_nvmlDeviceGetHandleByUUID(get_gpu_uuids):
    handles = [ nvmlDeviceGetHandleByUUID(pytest.uuids[i]) for i in range(pytest.ngpus) ]
    assert(len(pytest.handles)==len(handles))

# Test nvmlDeviceGetHandleByPciBusId
def test_nvmlDeviceGetHandleByPciBusId(get_gpu_pci_info):
    handles = [ nvmlDeviceGetHandleByPciBusId(pytest.pci_info[i].busId) for i in range(pytest.ngpus) ]
    assert(len(pytest.handles)==len(handles))

# [Skipping] nvmlDeviceGetName
# [Skipping] nvmlDeviceGetBoardId
# [Skipping] nvmlDeviceGetMultiGpuBoard
# [Skipping] nvmlDeviceGetBrand
# [Skipping] nvmlDeviceGetCpuAffinity
# [Skipping] nvmlDeviceSetCpuAffinity
# [Skipping] nvmlDeviceClearCpuAffinity
# [Skipping] nvmlDeviceGetMinorNumber
# [Skipping] nvmlDeviceGetUUID
# [Skipping] nvmlDeviceGetInforomVersion
# [Skipping] nvmlDeviceGetInforomImageVersion
# [Skipping] nvmlDeviceGetInforomConfigurationChecksum
# [Skipping] nvmlDeviceValidateInforom
# [Skipping] nvmlDeviceGetDisplayMode
# [Skipping] nvmlDeviceGetPersistenceMode
# [Skipping] nvmlDeviceGetClockInfo
# [Skipping] nvmlDeviceGetMaxClockInfo
# [Skipping] nvmlDeviceGetApplicationsCloc
# [Skipping] nvmlDeviceGetDefaultApplicationsClock
# [Skipping] nvmlDeviceGetSupportedMemoryClocks
# [Skipping] nvmlDeviceGetSupportedGraphicsClocks
# [Skipping] nvmlDeviceGetFanSpeed
# [Skipping] nvmlDeviceGetTemperature
# [Skipping] nvmlDeviceGetTemperatureThreshold
# [Skipping] nvmlDeviceGetPowerState
# [Skipping] nvmlDeviceGetPerformanceState
# [Skipping] nvmlDeviceGetPowerManagementMode
# [Skipping] nvmlDeviceGetPowerManagementLimit
# [Skipping] nvmlDeviceGetPowerManagementLimitConstraints
# [Skipping] nvmlDeviceGetPowerManagementDefaultLimit
# [Skipping] nvmlDeviceGetEnforcedPowerLimit

# Test nvmlDeviceGetPowerUsage
def test_nvmlDeviceGetPowerUsage(get_gpu_handles):
    for i in range(pytest.ngpus):
        power_watts = nvmlDeviceGetPowerUsage( pytest.handles[i] )
        assert(power_watts >= 0.0)

# [Skipping] nvmlDeviceGetGpuOperationMode
# [Skipping] nvmlDeviceGetCurrentGpuOperationMode
# [Skipping] nvmlDeviceGetPendingGpuOperationMode

# Test nvmlDeviceGetMemoryInfo
def test_nvmlDeviceGetMemoryInfo(get_gpu_handles):
    for i in range(pytest.ngpus):
        meminfo = nvmlDeviceGetMemoryInfo( pytest.handles[i] )
        assert((meminfo.used <= meminfo.free) and (meminfo.free <= meminfo.total))

# [Skipping] nvmlDeviceGetBAR1MemoryInfo
# [Skipping] nvmlDeviceGetComputeMode
# [Skipping] nvmlDeviceGetEccMode
# [Skipping] nvmlDeviceGetCurrentEccMode (Python API Addition)
# [Skipping] nvmlDeviceGetPendingEccMode (Python API Addition)
# [Skipping] nvmlDeviceGetTotalEccErrors
# [Skipping] nvmlDeviceGetDetailedEccErrors
# [Skipping] nvmlDeviceGetMemoryErrorCounter

# Test nvmlDeviceGetUtilizationRates
def test_nvmlDeviceGetUtilizationRates(get_gpu_handles):
    for i in range(pytest.ngpus):
        urate = nvmlDeviceGetUtilizationRates( pytest.handles[i] )
        assert(urate.gpu >= 0)
        assert(urate.memory >= 0)
        #print('[urate.gpu: '+str(urate.gpu)+']', end =' ')

# [Skipping] nvmlDeviceGetEncoderUtilization
# [Skipping] nvmlDeviceGetDecoderUtilization
# [Skipping] nvmlDeviceGetPcieReplayCounter
# [Skipping] nvmlDeviceGetDriverModel
# [Skipping] nvmlDeviceGetCurrentDriverModel
# [Skipping] nvmlDeviceGetPendingDriverModel
# [Skipping] nvmlDeviceGetVbiosVersion
# [Skipping] nvmlDeviceGetComputeRunningProcesses
# [Skipping] nvmlDeviceGetGraphicsRunningProcesses
# [Skipping] nvmlDeviceGetAutoBoostedClocksEnabled
# [Skipping] nvmlUnitSetLedState
# [Skipping] nvmlDeviceSetPersistenceMode
# [Skipping] nvmlDeviceSetComputeMode
# [Skipping] nvmlDeviceSetEccMode
# [Skipping] nvmlDeviceClearEccErrorCounts
# [Skipping] nvmlDeviceSetDriverModel
# [Skipping] nvmlDeviceSetAutoBoostedClocksEnabled
# [Skipping] nvmlDeviceSetDefaultAutoBoostedClocksEnabled
# [Skipping] nvmlDeviceSetApplicationsClocks
# [Skipping] nvmlDeviceResetApplicationsClocks
# [Skipping] nvmlDeviceSetPowerManagementLimit
# [Skipping] nvmlDeviceSetGpuOperationMode
# [Skipping] nvmlEventSetCreate
# [Skipping] nvmlDeviceRegisterEvents
# [Skipping] nvmlDeviceGetSupportedEventTypes
# [Skipping] nvmlEventSetWait
# [Skipping] nvmlEventSetFree
# [Skipping] nvmlDeviceOnSameBoard
# [Skipping] nvmlDeviceGetCurrPcieLinkGeneration
# [Skipping] nvmlDeviceGetMaxPcieLinkGeneration
# [Skipping] nvmlDeviceGetCurrPcieLinkWidth
# [Skipping] nvmlDeviceGetMaxPcieLinkWidth
# [Skipping] nvmlDeviceGetSupportedClocksThrottleReasons
# [Skipping] nvmlDeviceGetCurrentClocksThrottleReasons
# [Skipping] nvmlDeviceGetIndex
# [Skipping] nvmlDeviceGetAccountingMode
# [Skipping] nvmlDeviceSetAccountingMode
# [Skipping] nvmlDeviceClearAccountingPids
# [Skipping] nvmlDeviceGetAccountingStats
# [Skipping] nvmlDeviceGetAccountingPids
# [Skipping] nvmlDeviceGetAccountingBufferSize
# [Skipping] nvmlDeviceGetRetiredPages
# [Skipping] nvmlDeviceGetRetiredPagesPendingStatus
# [Skipping] nvmlDeviceGetAPIRestriction
# [Skipping] nvmlDeviceSetAPIRestriction
# [Skipping] nvmlDeviceGetBridgeChipInfo
# [Skipping] nvmlDeviceGetSamples
# [Skipping] nvmlDeviceGetViolationStatus

# Test nvmlDeviceGetPcieThroughput
def test_nvmlDeviceGetPcieThroughput(get_gpu_handles):
    for i in range(pytest.ngpus):
        tx_bytes_tp = nvmlDeviceGetPcieThroughput( pytest.handles[i], NVML_PCIE_UTIL_TX_BYTES )
        assert(tx_bytes_tp >= 0)
        rx_bytes_tp = nvmlDeviceGetPcieThroughput( pytest.handles[i], NVML_PCIE_UTIL_RX_BYTES )
        assert(rx_bytes_tp >= 0)
        count_tp = nvmlDeviceGetPcieThroughput( pytest.handles[i], NVML_PCIE_UTIL_COUNT )
        assert(count_tp >= 0)

# [Skipping] nvmlSystemGetTopologyGpuSet
# [Skipping] nvmlDeviceGetTopologyNearestGpus
# [Skipping] nvmlDeviceGetTopologyCommonAncestor
