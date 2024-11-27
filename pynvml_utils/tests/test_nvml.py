import pynvml
import pytest
import time
import os
from distutils.version import LooseVersion

NVML_PCIE_UTIL_TX_BYTES = pynvml.NVML_PCIE_UTIL_TX_BYTES
NVML_PCIE_UTIL_RX_BYTES = pynvml.NVML_PCIE_UTIL_RX_BYTES
NVML_PCIE_UTIL_COUNT = pynvml.NVML_PCIE_UTIL_COUNT

XFAIL_LEGACY_NVLINK_MSG = "Legacy NVLink test expected to fail."

# Fixture to initialize and finalize nvml
@pytest.fixture(scope="module")
def nvml(request):
    pynvml.nvmlInit()

    def nvml_close():
        pynvml.nvmlShutdown()

    request.addfinalizer(nvml_close)


# Fixture to check driver version
@pytest.fixture(scope="module")
def driver(request):
    driver_vsn = pynvml.nvmlSystemGetDriverVersion()
    if isinstance(driver_vsn, bytes):
        driver_vsn = driver_vsn.decode("utf-8")
    # Return "major" version only
    return int(driver_vsn.split(".")[0])


# Get GPU count
@pytest.fixture
def ngpus(nvml):
    result = pynvml.nvmlDeviceGetCount()
    assert result > 0
    print("[" + str(result) + " GPUs]", end=" ")
    return result


# Get handles using pynvml.nvmlDeviceGetHandleByIndex
@pytest.fixture
def handles(ngpus):
    handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in range(ngpus)]
    assert len(handles) == ngpus
    return handles


# Get GPU MIG count
@pytest.fixture
def nmigs(handles):
    result = pynvml.nvmlDeviceGetMaxMigDeviceCount(handles[0])
    print("[" + str(result) + " MIGs]", end=" ")
    return result


# Get MIG device handles
@pytest.fixture
def mig_handles(nmigs):
    handles = [pynvml.nvmlDeviceGetMigDeviceHandleByIndex(i) for i in range(nmigs)]
    assert len(handles) == nmigs
    return handles


@pytest.fixture
def serials(ngpus, handles):
    serials = [pynvml.nvmlDeviceGetSerial(handles[i]) for i in range(ngpus)]
    assert len(serials) == ngpus
    return serials


@pytest.fixture
def uuids(ngpus, handles):
    uuids = [pynvml.nvmlDeviceGetUUID(handles[i]) for i in range(ngpus)]
    assert len(uuids) == ngpus
    return uuids


@pytest.fixture
def pci_info(ngpus, handles):
    pci_info = [pynvml.nvmlDeviceGetPciInfo(handles[i]) for i in range(ngpus)]
    assert len(pci_info) == ngpus
    return pci_info


## ---------------------------- ##
## Start Fucntion-pointer Tests ##
## ---------------------------- ##

# Test pynvml.nvmlSystemGetNVMLVersion
def test_nvmlSystemGetNVMLVersion(nvml):
    vsn = 0.0
    vsn = pynvml.nvmlSystemGetNVMLVersion()
    print("[NVML Version: " + vsn + "]", end=" ")
    assert vsn > LooseVersion("0.0")


def test_nvmlSystemGetCudaDriverVersion(nvml):
    vsn = 0.0
    vsn = pynvml.nvmlSystemGetCudaDriverVersion()
    assert vsn != 0.0


# Test pynvml.nvmlSystemGetProcessName
def test_nvmlSystemGetProcessName(nvml):
    procname = None
    procname = pynvml.nvmlSystemGetProcessName(os.getpid())
    print("[Process: " + str(procname) + "]", end=" ")
    assert procname != None


# Test pynvml.nvmlSystemGetDriverVersion
def test_nvmlSystemGetDriverVersion(nvml):
    vsn = 0.0
    vsn = pynvml.nvmlSystemGetDriverVersion()
    print("[Driver Version: " + vsn + "]", end=" ")
    assert vsn > LooseVersion("0.0")  # Developing with 396.44


## Unit "Get" Functions (Skipping for now) ##

## Device "Get" Functions (Note: Some functions are fixtures, above) ##


def test_nvmlDeviceGetAttributes(mig_handles):
    # nvmlDeviceGetAttributes requires MIG device handle

    if mig_handles:
        for handle in mig_handles:
            att = pynvml.nvmlDeviceGetAttributes(handle)
            assert att is not None
    # No MIG devices, Skip
    pytest.skip()


# Test pynvml.nvmlDeviceGetHandleBySerial
def test_nvmlDeviceGetHandleBySerial(ngpus, serials):
    handles = [pynvml.nvmlDeviceGetHandleBySerial(serials[i]) for i in range(ngpus)]
    assert len(handles) == ngpus


# Test pynvml.nvmlDeviceGetHandleByUUID
def test_nvmlDeviceGetHandleByUUID(ngpus, uuids):
    handles = [pynvml.nvmlDeviceGetHandleByUUID(uuids[i]) for i in range(ngpus)]
    assert len(handles) == ngpus


# Test pynvml.nvmlDeviceGetHandleByPciBusId
def test_nvmlDeviceGetHandleByPciBusId(ngpus, pci_info):
    handles = [
        pynvml.nvmlDeviceGetHandleByPciBusId(pci_info[i].busId) for i in range(ngpus)
    ]
    assert len(handles) == ngpus


@pytest.mark.parametrize(
    "scope", [pynvml.NVML_AFFINITY_SCOPE_NODE, pynvml.NVML_AFFINITY_SCOPE_SOCKET]
)
def test_nvmlDeviceGetMemoryAffinity(handles, scope):
    size = 1024
    for handle in handles:
        nodeSet = pynvml.nvmlDeviceGetMemoryAffinity(handle, size, scope)
        assert nodeSet is not None


@pytest.mark.parametrize(
    "scope", [pynvml.NVML_AFFINITY_SCOPE_NODE, pynvml.NVML_AFFINITY_SCOPE_SOCKET]
)
def test_nvmlDeviceGetCpuAffinityWithinScope(handles, scope):
    size = 1024
    for handle in handles:
        cpuSet = pynvml.nvmlDeviceGetCpuAffinityWithinScope(handle, size, scope)
        assert cpuSet is not None


@pytest.mark.parametrize(
    "index",
    [
        pynvml.NVML_P2P_CAPS_INDEX_READ,
        pynvml.NVML_P2P_CAPS_INDEX_WRITE,
        pynvml.NVML_P2P_CAPS_INDEX_NVLINK,
        pynvml.NVML_P2P_CAPS_INDEX_ATOMICS,
        pynvml.NVML_P2P_CAPS_INDEX_PROP,
        pynvml.NVML_P2P_CAPS_INDEX_UNKNOWN,
    ],
)
def test_nvmlDeviceGetP2PStatus(handles, index):
    for h1 in handles:
        for h2 in handles:
            if h1 is not h2:
                status = pynvml.nvmlDeviceGetP2PStatus(h1, h2, index)
                assert (
                    pynvml.NVML_P2P_STATUS_OK
                    <= status
                    <= pynvml.NVML_P2P_STATUS_UNKNOWN
                )


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
        power_mWatts = pynvml.nvmlDeviceGetPowerUsage(handles[i])
        assert power_mWatts >= 0.0


# Test pynvml.nvmlDeviceGetTotalEnergyConsumption
def test_nvmlDeviceGetTotalEnergyConsumption(ngpus, handles):
    for i in range(ngpus):
        energy_mJoules1 = pynvml.nvmlDeviceGetTotalEnergyConsumption(handles[i])
        for j in range(10):  # idle for 150 ms
            time.sleep(0.015)  # and check for increase every 15 ms
            energy_mJoules2 = pynvml.nvmlDeviceGetTotalEnergyConsumption(handles[i])
            assert energy_mJoules2 >= energy_mJoules1
            if energy_mJoules2 > energy_mJoules1:
                break
        else:
            assert False, "energy did not increase across 150 ms interval"


# [Skipping] pynvml.nvmlDeviceGetGpuOperationMode
# [Skipping] pynvml.nvmlDeviceGetCurrentGpuOperationMode
# [Skipping] pynvml.nvmlDeviceGetPendingGpuOperationMode

# Test pynvml.nvmlDeviceGetMemoryInfo
def test_nvmlDeviceGetMemoryInfo(ngpus, handles):
    for i in range(ngpus):
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handles[i])
        assert (meminfo.used <= meminfo.total) and (meminfo.free <= meminfo.total)


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
        urate = pynvml.nvmlDeviceGetUtilizationRates(handles[i])
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
        tx_bytes_tp = pynvml.nvmlDeviceGetPcieThroughput(
            handles[i], NVML_PCIE_UTIL_TX_BYTES
        )
        assert tx_bytes_tp >= 0
        rx_bytes_tp = pynvml.nvmlDeviceGetPcieThroughput(
            handles[i], NVML_PCIE_UTIL_RX_BYTES
        )
        assert rx_bytes_tp >= 0
        count_tp = pynvml.nvmlDeviceGetPcieThroughput(handles[i], NVML_PCIE_UTIL_COUNT)
        assert count_tp >= 0


# [Skipping] pynvml.nvmlSystemGetTopologyGpuSet
# [Skipping] pynvml.nvmlDeviceGetTopologyNearestGpus
# [Skipping] pynvml.nvmlDeviceGetTopologyCommonAncestor

# Test pynvml.nvmlDeviceGetNvLinkVersion
# Test pynvml.nvmlDeviceGetNvLinkState
# Test pynvml.nvmlDeviceGetNvLinkRemotePciInfo
def test_nvml_nvlink_properties(ngpus, handles, driver):

    if driver > 450.0:
        pytest.xfail(XFAIL_LEGACY_NVLINK_MSG)

    for i in range(ngpus):
        for j in range(pynvml.NVML_NVLINK_MAX_LINKS):
            version = pynvml.nvmlDeviceGetNvLinkVersion(handles[i], j)
            assert version >= 1
            state = pynvml.nvmlDeviceGetNvLinkState(handles[i], j)
            assert state >= 0
            pci_info = pynvml.nvmlDeviceGetNvLinkRemotePciInfo(handles[i], j)
            assert isinstance(pci_info, pynvml.c_nvmlPciInfo_t)


# Test pynvml.nvmlDeviceGetNvLinkCapability
@pytest.mark.parametrize(
    "cap_type",
    [
        pynvml.NVML_NVLINK_CAP_P2P_SUPPORTED,  # P2P over NVLink is supported
        pynvml.NVML_NVLINK_CAP_SYSMEM_ACCESS,  # Access to system memory is supported
        pynvml.NVML_NVLINK_CAP_P2P_ATOMICS,  # P2P atomics are supported
        pynvml.NVML_NVLINK_CAP_SYSMEM_ATOMICS,  # System memory atomics are supported
        pynvml.NVML_NVLINK_CAP_SLI_BRIDGE,  # SLI is supported over this link
        pynvml.NVML_NVLINK_CAP_VALID,
    ],
)  # Link is supported on this device
def test_nvml_nvlink_capability(ngpus, handles, cap_type):
    for i in range(ngpus):
        for j in range(pynvml.NVML_NVLINK_MAX_LINKS):
            cap = pynvml.nvmlDeviceGetNvLinkCapability(handles[i], j, cap_type)
            assert cap >= 0


# Test pynvml.nvmlDeviceResetNvLinkUtilizationCounter
# Test pynvml.nvmlDeviceSetNvLinkUtilizationControl
# Test pynvml.nvmlDeviceGetNvLinkUtilizationCounter
# Test pynvml.nvmlDeviceGetNvLinkUtilizationControl
# Test pynvml.nvmlDeviceFreezeNvLinkUtilizationCounter
@pytest.mark.parametrize("counter", [0, 1])
@pytest.mark.parametrize("control", [0, 1, 2])
def test_nvml_nvlink_counters(ngpus, handles, counter, control, driver):

    if driver > 450.0:
        pytest.xfail(XFAIL_LEGACY_NVLINK_MSG)

    reset = 0
    for i in range(ngpus):
        for j in range(pynvml.NVML_NVLINK_MAX_LINKS):
            assert (
                pynvml.nvmlDeviceResetNvLinkUtilizationCounter(handles[i], j, counter)
                == pynvml.NVML_SUCCESS
            )
            pynvml.nvmlDeviceSetNvLinkUtilizationControl(
                handles[i], j, counter, control, reset
            )
            countdict = pynvml.nvmlDeviceGetNvLinkUtilizationCounter(
                handles[i], j, counter
            )
            ctl = pynvml.nvmlDeviceGetNvLinkUtilizationControl(handles[i], j, counter)
            assert countdict["rx"] >= 0
            assert countdict["tx"] >= 0
            assert ctl == control
            assert (
                pynvml.nvmlDeviceFreezeNvLinkUtilizationCounter(
                    handles[i], j, counter, 1
                )
                == pynvml.NVML_SUCCESS
            )
            assert (
                pynvml.nvmlDeviceFreezeNvLinkUtilizationCounter(
                    handles[i], j, counter, 0
                )
                == pynvml.NVML_SUCCESS
            )


# Test pynvml.nvmlDeviceResetNvLinkErrorCounters
# Test pynvml.nvmlDeviceGetNvLinkErrorCounter
@pytest.mark.parametrize(
    "error_type",
    [
        pynvml.NVML_NVLINK_ERROR_DL_REPLAY,
        pynvml.NVML_NVLINK_ERROR_DL_RECOVERY,
        pynvml.NVML_NVLINK_ERROR_DL_CRC_FLIT,
        pynvml.NVML_NVLINK_ERROR_DL_CRC_DATA,
    ],
)
def test_nvml_nvlink_error_counters(ngpus, handles, error_type, driver):

    if driver > 450.0:
        pytest.xfail(XFAIL_LEGACY_NVLINK_MSG)

    for i in range(ngpus):
        for j in range(pynvml.NVML_NVLINK_MAX_LINKS):
            assert (
                pynvml.nvmlDeviceResetNvLinkErrorCounters(handles[i], j)
                == pynvml.NVML_SUCCESS
            )
            error_count = pynvml.nvmlDeviceGetNvLinkErrorCounter(
                handles[i], j, error_type
            )
            assert error_count >= 0
