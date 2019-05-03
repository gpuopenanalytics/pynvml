import pynvml
import pytest
import os

NVML_PCIE_UTIL_TX_BYTES = pynvml.NVML_PCIE_UTIL_TX_BYTES
NVML_PCIE_UTIL_RX_BYTES = pynvml.NVML_PCIE_UTIL_RX_BYTES
NVML_PCIE_UTIL_COUNT = pynvml.NVML_PCIE_UTIL_COUNT

# Fixture to initialize and finalize nvml
@pytest.fixture(scope='module')
def nvml(request):
    pynvml.nvmlInit()
    def nvml_close():
        pynvml.nvmlShutdown()
    request.addfinalizer(nvml_close)

# Get GPU count
@pytest.fixture
def ngpus(nvml):
    result = pynvml.nvmlDeviceGetCount()
    assert result > 0
    print('['+str(result)+' GPUs]', end =' ')
    return result

# Get handles using pynvml.nvmlDeviceGetHandleByIndex
@pytest.fixture
def handles(ngpus):
    handles = [ pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(ngpus) ]
    assert len(handles) == ngpus
    return handles

@pytest.fixture
def serials(ngpus, handles):
    serials = [ pynvml.nvmlDeviceGetSerial(handles[i]) for i in range(ngpus) ]
    assert len(serials) == ngpus
    return serials

@pytest.fixture
def uuids(ngpus, handles):
    uuids = [ pynvml.nvmlDeviceGetUUID(handles[i]) for i in range(ngpus) ]
    assert len(uuids) == ngpus
    return uuids

@pytest.fixture
def pci_info(ngpus, handles):
    pci_info = [ pynvml.nvmlDeviceGetPciInfo(handles[i]) for i in range(ngpus) ]
    assert len(pci_info) == ngpus
    return pci_info

## ---------------------------- ##
## Start Fucntion-pointer Tests ##
## ---------------------------- ##

# Test pynvml.nvmlSystemGetNVMLVersion
def test_nvmlSystemGetNVMLVersion(nvml):
    vsn = 0.0
    vsn = float(pynvml.nvmlSystemGetDriverVersion().decode())
    print('[NVML Version: '+str(vsn)+']', end =' ')
    assert vsn > 0.0

# Test pynvml.nvmlSystemGetProcessName
def test_nvmlSystemGetProcessName(nvml):
    procname = None
    procname = pynvml.nvmlSystemGetProcessName(os.getpid())
    print('[Process: '+str(procname.decode())+']', end =' ')
    assert procname != None

# Test pynvml.nvmlSystemGetDriverVersion
def test_nvmlSystemGetDriverVersion(nvml):
    vsn = 0.0
    vsn = float(pynvml.nvmlSystemGetDriverVersion().decode())
    print('[Driver Version: '+str(vsn)+']', end =' ')
    assert vsn > 0.0 # Developing with 396.44

## Unit "Get" Functions (Skipping for now) ##

## Device "Get" Functions (Note: Some functions are fixtures, above) ##

# Test pynvml.nvmlDeviceGetHandleBySerial
def test_nvmlDeviceGetHandleBySerial(ngpus, serials):
    handles = [ pynvml.nvmlDeviceGetHandleBySerial(serials[i]) for i in range(ngpus) ]
    assert len(handles) == ngpus

# Test pynvml.nvmlDeviceGetHandleByUUID
def test_nvmlDeviceGetHandleByUUID(ngpus, uuids):
    handles = [ pynvml.nvmlDeviceGetHandleByUUID(uuids[i]) for i in range(ngpus) ]
    assert len(handles) == ngpus

# Test pynvml.nvmlDeviceGetHandleByPciBusId
def test_nvmlDeviceGetHandleByPciBusId(ngpus, pci_info):
    handles = [ pynvml.nvmlDeviceGetHandleByPciBusId(pci_info[i].busId) for i in range(ngpus) ]
    assert len(handles) == ngpus

# [Skipping] pynvml.nvmlDeviceGetName
# [Skipping] pynvml.nvmlDeviceGetBoardId
# [Skipping] pynvml.nvmlDeviceGetMultiGpuBoard
# [Skipping] pynvml.nvmlDeviceGetBrand
# [Skipping] pynvml.nvmlDeviceGetCpuAffinity
# [Skipping] pynvml.nvmlDeviceSetCpuAffinity
# [Skipping] pynvml.nvmlDeviceClearCpuAffinity
# [Skipping] pynvml.nvmlDeviceGetMinorNumber
# [Skipping] pynvml.nvmlDeviceGetUUID
# [Skipping] pynvml.nvmlDeviceGetInforomVersion
# [Skipping] pynvml.nvmlDeviceGetInforomImageVersion
# [Skipping] pynvml.nvmlDeviceGetInforomConfigurationChecksum
# [Skipping] pynvml.nvmlDeviceValidateInforom
# [Skipping] pynvml.nvmlDeviceGetDisplayMode
# [Skipping] pynvml.nvmlDeviceGetPersistenceMode
# [Skipping] pynvml.nvmlDeviceGetClockInfo
# [Skipping] pynvml.nvmlDeviceGetMaxClockInfo
# [Skipping] pynvml.nvmlDeviceGetApplicationsCloc
# [Skipping] pynvml.nvmlDeviceGetDefaultApplicationsClock
# [Skipping] pynvml.nvmlDeviceGetSupportedMemoryClocks
# [Skipping] pynvml.nvmlDeviceGetSupportedGraphicsClocks
# [Skipping] pynvml.nvmlDeviceGetFanSpeed
# [Skipping] pynvml.nvmlDeviceGetTemperature
# [Skipping] pynvml.nvmlDeviceGetTemperatureThreshold
# [Skipping] pynvml.nvmlDeviceGetPowerState
# [Skipping] pynvml.nvmlDeviceGetPerformanceState
# [Skipping] pynvml.nvmlDeviceGetPowerManagementMode
# [Skipping] pynvml.nvmlDeviceGetPowerManagementLimit
# [Skipping] pynvml.nvmlDeviceGetPowerManagementLimitConstraints
# [Skipping] pynvml.nvmlDeviceGetPowerManagementDefaultLimit
# [Skipping] pynvml.nvmlDeviceGetEnforcedPowerLimit

# Test pynvml.nvmlDeviceGetPowerUsage
def test_nvmlDeviceGetPowerUsage(ngpus, handles):
    for i in range(ngpus):
        power_watts = pynvml.nvmlDeviceGetPowerUsage( handles[i] )
        assert power_watts >= 0.0

# [Skipping] pynvml.nvmlDeviceGetGpuOperationMode
# [Skipping] pynvml.nvmlDeviceGetCurrentGpuOperationMode
# [Skipping] pynvml.nvmlDeviceGetPendingGpuOperationMode

# Test pynvml.nvmlDeviceGetMemoryInfo
def test_nvmlDeviceGetMemoryInfo(ngpus, handles):
    for i in range(ngpus):
        meminfo = pynvml.nvmlDeviceGetMemoryInfo( handles[i] )
        assert (meminfo.used <= meminfo.free) and (meminfo.free <= meminfo.total)

# [Skipping] pynvml.nvmlDeviceGetBAR1MemoryInfo
# [Skipping] pynvml.nvmlDeviceGetComputeMode
# [Skipping] pynvml.nvmlDeviceGetEccMode
# [Skipping] pynvml.nvmlDeviceGetCurrentEccMode (Python API Addition)
# [Skipping] pynvml.nvmlDeviceGetPendingEccMode (Python API Addition)
# [Skipping] pynvml.nvmlDeviceGetTotalEccErrors
# [Skipping] pynvml.nvmlDeviceGetDetailedEccErrors
# [Skipping] pynvml.nvmlDeviceGetMemoryErrorCounter

# Test pynvml.nvmlDeviceGetUtilizationRates
def test_nvmlDeviceGetUtilizationRates(ngpus, handles):
    for i in range(ngpus):
        urate = pynvml.nvmlDeviceGetUtilizationRates( handles[i] )
        assert urate.gpu >= 0
        assert urate.memory >= 0

# [Skipping] pynvml.nvmlDeviceGetEncoderUtilization
# [Skipping] pynvml.nvmlDeviceGetDecoderUtilization
# [Skipping] pynvml.nvmlDeviceGetPcieReplayCounter
# [Skipping] pynvml.nvmlDeviceGetDriverModel
# [Skipping] pynvml.nvmlDeviceGetCurrentDriverModel
# [Skipping] pynvml.nvmlDeviceGetPendingDriverModel
# [Skipping] pynvml.nvmlDeviceGetVbiosVersion
# [Skipping] pynvml.nvmlDeviceGetComputeRunningProcesses
# [Skipping] pynvml.nvmlDeviceGetGraphicsRunningProcesses
# [Skipping] pynvml.nvmlDeviceGetAutoBoostedClocksEnabled
# [Skipping] nvmlUnitSetLedState
# [Skipping] pynvml.nvmlDeviceSetPersistenceMode
# [Skipping] pynvml.nvmlDeviceSetComputeMode
# [Skipping] pynvml.nvmlDeviceSetEccMode
# [Skipping] pynvml.nvmlDeviceClearEccErrorCounts
# [Skipping] pynvml.nvmlDeviceSetDriverModel
# [Skipping] pynvml.nvmlDeviceSetAutoBoostedClocksEnabled
# [Skipping] pynvml.nvmlDeviceSetDefaultAutoBoostedClocksEnabled
# [Skipping] pynvml.nvmlDeviceSetApplicationsClocks
# [Skipping] pynvml.nvmlDeviceResetApplicationsClocks
# [Skipping] pynvml.nvmlDeviceSetPowerManagementLimit
# [Skipping] pynvml.nvmlDeviceSetGpuOperationMode
# [Skipping] nvmlEventSetCreate
# [Skipping] pynvml.nvmlDeviceRegisterEvents
# [Skipping] pynvml.nvmlDeviceGetSupportedEventTypes
# [Skipping] nvmlEventSetWait
# [Skipping] nvmlEventSetFree
# [Skipping] pynvml.nvmlDeviceOnSameBoard
# [Skipping] pynvml.nvmlDeviceGetCurrPcieLinkGeneration
# [Skipping] pynvml.nvmlDeviceGetMaxPcieLinkGeneration
# [Skipping] pynvml.nvmlDeviceGetCurrPcieLinkWidth
# [Skipping] pynvml.nvmlDeviceGetMaxPcieLinkWidth
# [Skipping] pynvml.nvmlDeviceGetSupportedClocksThrottleReasons
# [Skipping] pynvml.nvmlDeviceGetCurrentClocksThrottleReasons
# [Skipping] pynvml.nvmlDeviceGetIndex
# [Skipping] pynvml.nvmlDeviceGetAccountingMode
# [Skipping] pynvml.nvmlDeviceSetAccountingMode
# [Skipping] pynvml.nvmlDeviceClearAccountingPids
# [Skipping] pynvml.nvmlDeviceGetAccountingStats
# [Skipping] pynvml.nvmlDeviceGetAccountingPids
# [Skipping] pynvml.nvmlDeviceGetAccountingBufferSize
# [Skipping] pynvml.nvmlDeviceGetRetiredPages
# [Skipping] pynvml.nvmlDeviceGetRetiredPagesPendingStatus
# [Skipping] pynvml.nvmlDeviceGetAPIRestriction
# [Skipping] pynvml.nvmlDeviceSetAPIRestriction
# [Skipping] pynvml.nvmlDeviceGetBridgeChipInfo
# [Skipping] pynvml.nvmlDeviceGetSamples
# [Skipping] pynvml.nvmlDeviceGetViolationStatus

# Test pynvml.nvmlDeviceGetPcieThroughput
def test_nvmlDeviceGetPcieThroughput(ngpus, handles):
    for i in range(ngpus):
        tx_bytes_tp = pynvml.nvmlDeviceGetPcieThroughput( handles[i], NVML_PCIE_UTIL_TX_BYTES )
        assert tx_bytes_tp >= 0
        rx_bytes_tp = pynvml.nvmlDeviceGetPcieThroughput( handles[i], NVML_PCIE_UTIL_RX_BYTES )
        assert rx_bytes_tp >= 0
        count_tp = pynvml.nvmlDeviceGetPcieThroughput( handles[i], NVML_PCIE_UTIL_COUNT )
        assert count_tp >= 0

# [Skipping] pynvml.nvmlSystemGetTopologyGpuSet
# [Skipping] pynvml.nvmlDeviceGetTopologyNearestGpus
# [Skipping] pynvml.nvmlDeviceGetTopologyCommonAncestor
