# ============================================================================ #
# Copyright (c) 2011-2015, NVIDIA Corporation.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the NVIDIA Corporation nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# ============================================================================ #

"""
Python bindings for the NVML library.
"""

from ctypes import *
from ctypes.util import find_library
import sys
import os
import threading
import string

## ========================================================================== ##
##                                                                            ##
##                              CType Mappings                                ##
##                                                                            ##
## ========================================================================== ##

NVML_API_VERSION = 11
NVML_API_VERSION_STR = "11"

## Enums
_nvmlBridgeChipType_t = c_uint
NVML_BRIDGE_CHIP_PLX = 0
NVML_BRIDGE_CHIP_BRO4 = 1
NVML_MAX_PHYSICAL_BRIDGE = 128

NVML_VALUE_NOT_AVAILABLE_ulonglong = c_ulonglong(-1)
NVML_VALUE_NOT_AVAILABLE_uint = c_uint(-1)

# Added CUDA 10.0
NVML_DEVICE_PCI_BUS_ID_LEGACY_FMT = "%04X:%02X:%02X.0"
NVML_DEVICE_PCI_BUS_ID_FMT = "%08X:%02X:%02X.0"

# Updated from 6 to 12 in CUDA 11.0
NVML_NVLINK_MAX_LINKS = 12

_nvmlNvLinkUtilizationCountUnits_t = c_uint
NVML_NVLINK_COUNTER_UNIT_CYCLES = 0
NVML_NVLINK_COUNTER_UNIT_PACKETS = 1
NVML_NVLINK_COUNTER_UNIT_BYTES = 2
# Added CUDA 10.1
NVML_NVLINK_COUNTER_UNIT_RESERVED = 3
NVML_NVLINK_COUNTER_UNIT_COUNT = 4

_nvmlNvLinkUtilizationCountPktTypes_t = c_uint
NVML_NVLINK_COUNTER_PKTFILTER_NOP = 0x1
NVML_NVLINK_COUNTER_PKTFILTER_READ = 0x2
NVML_NVLINK_COUNTER_PKTFILTER_WRITE = 0x4
NVML_NVLINK_COUNTER_PKTFILTER_RATOM = 0x8
NVML_NVLINK_COUNTER_PKTFILTER_NRATOM = 0x10
NVML_NVLINK_COUNTER_PKTFILTER_FLUSH = 0x20
NVML_NVLINK_COUNTER_PKTFILTER_RESPDATA = 0x40
NVML_NVLINK_COUNTER_PKTFILTER_RESPNODATA = 0x80
NVML_NVLINK_COUNTER_PKTFILTER_ALL = 0xFF

_nvmlNvLinkUtilizationControl_t = c_int

_nvmlNvLinkCapability_t = c_uint
NVML_NVLINK_CAP_P2P_SUPPORTED = 0
NVML_NVLINK_CAP_SYSMEM_ACCESS = 1
NVML_NVLINK_CAP_P2P_ATOMICS = 2
NVML_NVLINK_CAP_SYSMEM_ATOMICS = 3
NVML_NVLINK_CAP_SLI_BRIDGE = 4
NVML_NVLINK_CAP_VALID = 5
NVML_NVLINK_CAP_COUNT = 6

_nvmlNvLinkErrorCounter_t = c_uint
NVML_NVLINK_ERROR_DL_REPLAY = 0
NVML_NVLINK_ERROR_DL_RECOVERY = 1
NVML_NVLINK_ERROR_DL_CRC_FLIT = 2
NVML_NVLINK_ERROR_DL_CRC_DATA = 3
NVML_NVLINK_ERROR_COUNT = 4

_nvmlGpuTopologyLevel_t = c_uint
NVML_TOPOLOGY_INTERNAL = 0
NVML_TOPOLOGY_SINGLE = 10
NVML_TOPOLOGY_MULTIPLE = 20
NVML_TOPOLOGY_HOSTBRIDGE = 30
NVML_TOPOLOGY_NODE = 40
NVML_TOPOLOGY_SYSTEM = 50
# Changed from CPU to NODE in CUDA 9.1
NVML_TOPOLOGY_CPU = 40

# Added CUDA 9.0
_nvmlGpuP2PStatus_t = c_uint
NVML_P2P_STATUS_OK = 0
NVML_P2P_STATUS_CHIPSET_NOT_SUPPORED = 1
NVML_P2P_STATUS_GPU_NOT_SUPPORTED = 2
NVML_P2P_STATUS_IOH_TOPOLOGY_NOT_SUPPORTED = 3
NVML_P2P_STATUS_DISABLED_BY_REGKEY = 4
NVML_P2P_STATUS_NOT_SUPPORTED = 5
NVML_P2P_STATUS_UNKNOWN = 6

# Added CUDA 9.0
_nvmlGpuP2PCapsIndex_t = c_uint
NVML_P2P_CAPS_INDEX_READ = 0
NVML_P2P_CAPS_INDEX_WRITE = 1
NVML_P2P_CAPS_INDEX_NVLINK = 2
NVML_P2P_CAPS_INDEX_ATOMICS = 3
NVML_P2P_CAPS_INDEX_PROP = 4
NVML_P2P_CAPS_INDEX_UNKNOWN = 5

_nvmlSamplingType_t = c_uint
NVML_TOTAL_POWER_SAMPLES = 0
NVML_GPU_UTILIZATION_SAMPLES = 1
NVML_MEMORY_UTILIZATION_SAMPLES = 2
NVML_ENC_UTILIZATION_SAMPLES = 3
NVML_DEC_UTILIZATION_SAMPLES = 4
NVML_PROCESSOR_CLK_SAMPLES = 5
NVML_MEMORY_CLK_SAMPLES = 6
NVML_SAMPLINGTYPE_COUNT = 7

_nvmlPcieUtilCounter_t = c_uint
NVML_PCIE_UTIL_TX_BYTES = 0
NVML_PCIE_UTIL_RX_BYTES = 1
NVML_PCIE_UTIL_COUNT = 2

_nvmlValueType_t = c_uint
NVML_VALUE_TYPE_DOUBLE = 0
NVML_VALUE_TYPE_UNSIGNED_INT = 1
NVML_VALUE_TYPE_UNSIGNED_LONG = 2
NVML_VALUE_TYPE_UNSIGNED_LONG_LONG = 3
# Added CUDA 9.0
NVML_VALUE_TYPE_SIGNED_LONG_LONG = 4
NVML_VALUE_TYPE_COUNT = 5

_nvmlPerfPolicyType_t = c_uint
NVML_PERF_POLICY_POWER = 0
NVML_PERF_POLICY_THERMAL = 1
# Added CUDA 9.0
NVML_PERF_POLICY_SYNC_BOOST = 2
NVML_PERF_POLICY_BOARD_LIMIT = 3
NVML_PERF_POLICY_LOW_UTILIZATION = 4
NVML_PERF_POLICY_RELIABILITY = 5
NVML_PERF_POLICY_TOTAL_APP_CLOCKS = 10
NVML_PERF_POLICY_TOTAL_BASE_CLOCKS = 11
NVML_PERF_POLICY_COUNT = 12

_nvmlEnableState_t = c_uint
NVML_FEATURE_DISABLED = 0
NVML_FEATURE_ENABLED = 1

# C preprocessor defined values
nvmlFlagDefault = 0
nvmlFlagForce = 1

_nvmlBrandType_t = c_uint
NVML_BRAND_UNKNOWN = 0
NVML_BRAND_QUADRO = 1
NVML_BRAND_TESLA = 2
NVML_BRAND_NVS = 3
NVML_BRAND_GRID = 4
NVML_BRAND_GEFORCE = 5
# CUDA 9.2
NVML_BRAND_TITAN = 6
NVML_BRAND_COUNT = 7

_nvmlTemperatureThresholds_t = c_uint
NVML_TEMPERATURE_THRESHOLD_SHUTDOWN = 0
NVML_TEMPERATURE_THRESHOLD_SLOWDOWN = 1
# CUDA 9.0
NVML_TEMPERATURE_THRESHOLD_MEM_MAX = 2
NVML_TEMPERATURE_THRESHOLD_GPU_MAX = 3
NVML_TEMPERATURE_THRESHOLD_COUNT = 4

_nvmlTemperatureSensors_t = c_uint
NVML_TEMPERATURE_GPU = 0
NVML_TEMPERATURE_COUNT = 1

_nvmlComputeMode_t = c_uint
NVML_COMPUTEMODE_DEFAULT = 0
NVML_COMPUTEMODE_EXCLUSIVE_THREAD = 1
NVML_COMPUTEMODE_PROHIBITED = 2
NVML_COMPUTEMODE_EXCLUSIVE_PROCESS = 3
NVML_COMPUTEMODE_COUNT = 4

_nvmlMemoryLocation_t = c_uint
NVML_MEMORY_LOCATION_L1_CACHE = 0
NVML_MEMORY_LOCATION_L2_CACHE = 1
NVML_MEMORY_LOCATION_DEVICE_MEMORY = 2
NVML_MEMORY_LOCATION_REGISTER_FILE = 3
NVML_MEMORY_LOCATION_TEXTURE_MEMORY = 4
NVML_MEMORY_LOCATION_COUNT = 5

# These are deprecated, instead use _nvmlMemoryErrorType_t
_nvmlEccBitType_t = c_uint
NVML_SINGLE_BIT_ECC = 0
NVML_DOUBLE_BIT_ECC = 1
NVML_ECC_ERROR_TYPE_COUNT = 2

_nvmlEccCounterType_t = c_uint
NVML_VOLATILE_ECC = 0
NVML_AGGREGATE_ECC = 1
NVML_ECC_COUNTER_TYPE_COUNT = 2

_nvmlMemoryErrorType_t = c_uint
NVML_MEMORY_ERROR_TYPE_CORRECTED = 0
NVML_MEMORY_ERROR_TYPE_UNCORRECTED = 1
NVML_MEMORY_ERROR_TYPE_COUNT = 2

_nvmlClockType_t = c_uint
NVML_CLOCK_GRAPHICS = 0
NVML_CLOCK_SM = 1
NVML_CLOCK_MEM = 2
# CUDA 9.0
NVML_CLOCK_VIDEO = 3
NVML_CLOCK_COUNT = 4

# CUDA 9.0
_nvmlClockId_t = c_uint
NVML_CLOCK_ID_CURRENT = 0
NVML_CLOCK_ID_APP_CLOCK_TARGET = 1
NVML_CLOCK_ID_APP_CLOCK_DEFAULT = 2
NVML_CLOCK_ID_CUSTOMER_BOOST_MAX = 3
NVML_CLOCK_ID_COUNT = 4

_nvmlDriverModel_t = c_uint
NVML_DRIVER_WDDM = 0
NVML_DRIVER_WDM = 1

_nvmlPstates_t = c_uint
NVML_PSTATE_0 = 0
NVML_PSTATE_1 = 1
NVML_PSTATE_2 = 2
NVML_PSTATE_3 = 3
NVML_PSTATE_4 = 4
NVML_PSTATE_5 = 5
NVML_PSTATE_6 = 6
NVML_PSTATE_7 = 7
NVML_PSTATE_8 = 8
NVML_PSTATE_9 = 9
NVML_PSTATE_10 = 10
NVML_PSTATE_11 = 11
NVML_PSTATE_12 = 12
NVML_PSTATE_13 = 13
NVML_PSTATE_14 = 14
NVML_PSTATE_15 = 15
NVML_PSTATE_UNKNOWN = 32

_nvmlGpuOperationMode_t = c_uint
NVML_GOM_ALL_ON = 0
NVML_GOM_COMPUTE = 1
NVML_GOM_LOW_DP = 2

_nvmlInforomObject_t = c_uint
NVML_INFOROM_OEM = 0
NVML_INFOROM_ECC = 1
NVML_INFOROM_POWER = 2
NVML_INFOROM_COUNT = 3

_nvmlReturn_t = c_uint
NVML_SUCCESS = 0
NVML_ERROR_UNINITIALIZED = 1
NVML_ERROR_INVALID_ARGUMENT = 2
NVML_ERROR_NOT_SUPPORTED = 3
NVML_ERROR_NO_PERMISSION = 4
NVML_ERROR_ALREADY_INITIALIZED = 5
NVML_ERROR_NOT_FOUND = 6
NVML_ERROR_INSUFFICIENT_SIZE = 7
NVML_ERROR_INSUFFICIENT_POWER = 8
NVML_ERROR_DRIVER_NOT_LOADED = 9
NVML_ERROR_TIMEOUT = 10
NVML_ERROR_IRQ_ISSUE = 11
NVML_ERROR_LIBRARY_NOT_FOUND = 12
NVML_ERROR_FUNCTION_NOT_FOUND = 13
NVML_ERROR_CORRUPTED_INFOROM = 14
NVML_ERROR_GPU_IS_LOST = 15
NVML_ERROR_RESET_REQUIRED = 16
NVML_ERROR_OPERATING_SYSTEM = 17
NVML_ERROR_LIB_RM_VERSION_MISMATCH = 18
# CUDA 9.0
NVML_ERROR_IN_USE = 19
NVML_ERROR_MEMORY = 20
NVML_ERROR_NO_DATA = 21
NVML_ERROR_VGPU_ECC_NOT_SUPPORTED = 22
# CUDA 11.0
NVML_ERROR_INSUFFICIENT_RESOURCES = 23
NVML_ERROR_UNKNOWN = 999

# CUDA 9.0
_nvmlMemoryLocation_t = c_uint
NVML_MEMORY_LOCATION_L1_CACHE = 0
NVML_MEMORY_LOCATION_L2_CACHE = 1
NVML_MEMORY_LOCATION_DEVICE_MEMORY = 2
NVML_MEMORY_LOCATION_REGISTER_FILE = 3
NVML_MEMORY_LOCATION_TEXTURE_MEMORY = 4
NVML_MEMORY_LOCATION_TEXTURE_SHM = 5
NVML_MEMORY_LOCATION_CBU = 6
# CUDA 10.0
NVML_MEMORY_LOCATION_SRAM = 7
NVML_MEMORY_LOCATION_COUNT = 8

_nvmlPageRetirementCause_t = c_uint
NVML_PAGE_RETIREMENT_CAUSE_DOUBLE_BIT_ECC_ERROR = 0
NVML_PAGE_RETIREMENT_CAUSE_MULTIPLE_SINGLE_BIT_ECC_ERRORS = 1
NVML_PAGE_RETIREMENT_CAUSE_COUNT = 2

_nvmlRestrictedAPI_t = c_uint
NVML_RESTRICTED_API_SET_APPLICATION_CLOCKS = 0
NVML_RESTRICTED_API_SET_AUTO_BOOSTED_CLOCKS = 1
NVML_RESTRICTED_API_COUNT = 2

# Added CUDA 9.0
_nvmlGpuVirtualizationMode = c_uint
NVML_GPU_VIRTUALIZATION_MODE_NONE = 0
NVML_GPU_VIRTUALIZATION_MODE_PASSTHROUGH = 1
NVML_GPU_VIRTUALIZATION_MODE_VGPU = 2
NVML_GPU_VIRTUALIZATION_MODE_HOST_VGPU = 3
NVML_GPU_VIRTUALIZATION_MODE_HOST_VSGA = 4

# Added CUDA 9.0
_nvmlHostVgpuMode_t = c_uint
NVML_HOST_VGPU_MODE_NON_SRIOV = 0
NVML_HOST_VGPU_MODE_SRIOV = 1

# Added CUDA 9.0
_nvmlVgpuVmIdType_t = c_uint
NVML_VGPU_VM_ID_DOMAIN_ID = 0
NVML_VGPU_VM_ID_UUID = 1

# Added CUDA 9.0
_nvmlVgpuGuestInfoState_t = c_uint
NVML_VGPU_INSTANCE_GUEST_INFO_STATE_UNINITIALIZED = 0
NVML_VGPU_INSTANCE_GUEST_INFO_STATE_INITIALIZED = 1

# Added CUDA 9.0
_nvmlGridLicenseFeatureCode_t = c_uint
NVML_GRID_LICENSE_FEATURE_CODE_VGPU = 0
NVML_GRID_LICENSE_FEATURE_CODE_VWORKSTATION = 1

# Added CUDA 11.0
_nvmlDeviceArchitecture_t = c_uint
NVML_DEVICE_ARCH_KEPLER = 2
NVML_DEVICE_ARCH_MAXWELL = 3
NVML_DEVICE_ARCH_PASCAL = 4
NVML_DEVICE_ARCH_VOLTA = 5
NVML_DEVICE_ARCH_TURING = 6
NVML_DEVICE_ARCH_AMPERE = 7
NVML_DEVICE_ARCH_UNKNOWN = 0xffffffff

# Added CUDA 9.0
_nvmlFieldValueEnums_t = c_uint
NVML_FI_DEV_ECC_CURRENT = 1
NVML_FI_DEV_ECC_PENDING = 2
NVML_FI_DEV_ECC_SBE_VOL_TOTAL = 3
NVML_FI_DEV_ECC_DBE_VOL_TOTAL = 4
NVML_FI_DEV_ECC_SBE_AGG_TOTAL = 5
NVML_FI_DEV_ECC_DBE_AGG_TOTAL = 6
NVML_FI_DEV_ECC_SBE_VOL_L1 = 7
NVML_FI_DEV_ECC_DBE_VOL_L1 = 8
NVML_FI_DEV_ECC_SBE_VOL_L2 = 9
NVML_FI_DEV_ECC_DBE_VOL_L2 = 10
NVML_FI_DEV_ECC_SBE_VOL_DEV = 11
NVML_FI_DEV_ECC_DBE_VOL_DEV = 12
NVML_FI_DEV_ECC_SBE_VOL_REG = 13
NVML_FI_DEV_ECC_DBE_VOL_REG = 14
NVML_FI_DEV_ECC_SBE_VOL_TEX = 15
NVML_FI_DEV_ECC_DBE_VOL_TEX = 16
NVML_FI_DEV_ECC_DBE_VOL_CBU = 17
NVML_FI_DEV_ECC_SBE_AGG_L1 = 18
NVML_FI_DEV_ECC_DBE_AGG_L1 = 19
NVML_FI_DEV_ECC_SBE_AGG_L2 = 20
NVML_FI_DEV_ECC_DBE_AGG_L2 = 21
NVML_FI_DEV_ECC_SBE_AGG_DEV = 22
NVML_FI_DEV_ECC_DBE_AGG_DEV = 23
NVML_FI_DEV_ECC_SBE_AGG_REG = 24
NVML_FI_DEV_ECC_DBE_AGG_REG = 25
NVML_FI_DEV_ECC_SBE_AGG_TEX = 26
NVML_FI_DEV_ECC_DBE_AGG_TEX = 27
NVML_FI_DEV_ECC_DBE_AGG_CBU = 28
NVML_FI_DEV_RETIRED_SBE = 29
NVML_FI_DEV_RETIRED_DBE = 30
NVML_FI_DEV_RETIRED_PENDING = 31
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L0 = 32
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L1 = 33
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L2 = 34
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L3 = 35
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L4 = 36
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L5 = 37
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_TOTAL = 38
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L0 = 39
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L1 = 40
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L2 = 41
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L3 = 42
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L4 = 43
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L5 = 44
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_TOTAL = 45
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L0 = 46
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L1 = 47
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L2 = 48
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L3 = 49
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L4 = 50
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L5 = 51
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_TOTAL = 52
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L0 = 53
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L1 = 54
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L2 = 55
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L3 = 56
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L4 = 57
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L5 = 58
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_TOTAL = 59
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L0 = 60
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L1 = 61
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L2 = 62
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L3 = 63
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L4 = 64
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L5 = 65
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_TOTAL = 66
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L0 = 67
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L1 = 68
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L2 = 69
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L3 = 70
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L4 = 71
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L5 = 72
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_TOTAL = 73
NVML_FI_DEV_PERF_POLICY_POWER = 74
NVML_FI_DEV_PERF_POLICY_THERMAL = 75
NVML_FI_DEV_PERF_POLICY_SYNC_BOOST = 76
NVML_FI_DEV_PERF_POLICY_BOARD_LIMIT = 77
NVML_FI_DEV_PERF_POLICY_LOW_UTILIZATION = 78
NVML_FI_DEV_PERF_POLICY_RELIABILITY = 79
NVML_FI_DEV_PERF_POLICY_TOTAL_APP_CLOCKS = 80
NVML_FI_DEV_PERF_POLICY_TOTAL_BASE_CLOCKS = 81
NVML_FI_DEV_MEMORY_TEMP = 82
NVML_FI_DEV_TOTAL_ENERGY_CONSUMPTION = 83
# Added CUDA 9.1
NVML_FI_DEV_NVLINK_SPEED_MBPS_L0 = 84
NVML_FI_DEV_NVLINK_SPEED_MBPS_L1 = 85
NVML_FI_DEV_NVLINK_SPEED_MBPS_L2 = 86
NVML_FI_DEV_NVLINK_SPEED_MBPS_L3 = 87
NVML_FI_DEV_NVLINK_SPEED_MBPS_L4 = 88
NVML_FI_DEV_NVLINK_SPEED_MBPS_L5 = 89
NVML_FI_DEV_NVLINK_SPEED_MBPS_COMMON = 90
NVML_FI_DEV_NVLINK_LINK_COUNT = 91
# Added CUDA 9.2
NVML_FI_DEV_RETIRED_PENDING_SBE = 92
NVML_FI_DEV_RETIRED_PENDING_DBE = 93
# Added CUDA 10.0
NVML_FI_DEV_PCIE_REPLAY_COUNTER = 94
NVML_FI_DEV_PCIE_REPLAY_ROLLOVER_COUNTER = 95
# Added CUDA 11.0
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L6 = 96
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L7 = 97
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L8 = 98
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L9 = 99
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L10 = 100
NVML_FI_DEV_NVLINK_CRC_FLIT_ERROR_COUNT_L11 = 101
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L6 = 102
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L7 = 103
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L8 = 104
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L9 = 105
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L10 = 106
NVML_FI_DEV_NVLINK_CRC_DATA_ERROR_COUNT_L11 = 107
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L6 = 108
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L7 = 119
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L8 = 110
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L9 = 111
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L10 = 112
NVML_FI_DEV_NVLINK_REPLAY_ERROR_COUNT_L11 = 113
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L6 = 114
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L7 = 115
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L8 = 116
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L9 = 117
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L10 = 118
NVML_FI_DEV_NVLINK_RECOVERY_ERROR_COUNT_L11 = 119
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L6 = 120
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L7 = 121
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L8 = 122
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L9 = 123
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L10 = 124
NVML_FI_DEV_NVLINK_BANDWIDTH_C0_L11 = 125
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L6 = 126
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L7 = 127
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L8 = 128
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L9 = 129
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L10 = 130
NVML_FI_DEV_NVLINK_BANDWIDTH_C1_L11 = 131
NVML_FI_DEV_NVLINK_SPEED_MBPS_L6 = 132
NVML_FI_DEV_NVLINK_SPEED_MBPS_L7 = 133
NVML_FI_DEV_NVLINK_SPEED_MBPS_L8 = 134
NVML_FI_DEV_NVLINK_SPEED_MBPS_L9 = 135
NVML_FI_DEV_NVLINK_SPEED_MBPS_L10 = 136
NVML_FI_DEV_NVLINK_SPEED_MBPS_L11 = 137
NVML_FI_DEV_NVLINK_THROUGHPUT_DATA_TX = 138
NVML_FI_DEV_NVLINK_THROUGHPUT_DATA_RX = 139
NVML_FI_DEV_NVLINK_THROUGHPUT_RAW_TX = 140
NVML_FI_DEV_NVLINK_THROUGHPUT_RAW_R = 141
NVML_FI_DEV_REMAPPED_COR = 142
NVML_FI_DEV_REMAPPED_UNC = 143
NVML_FI_DEV_REMAPPED_PENDING = 144
NVML_FI_DEV_REMAPPED_FAILURE = 145
NVML_FI_MAX = 146

_nvmlFanState_t = c_uint
NVML_FAN_NORMAL = 0
NVML_FAN_FAILED = 1

_nvmlLedColor_t = c_uint
NVML_LED_COLOR_GREEN = 0
NVML_LED_COLOR_AMBER = 1

# Added CUDA 9.0
NVML_GRID_LICENSE_BUFFER_SIZE = 128
NVML_VGPU_NAME_BUFFER_SIZE = 64
NVML_GRID_LICENSE_FEATURE_MAX_COUNT = 3

# Added CUDA 9.0
NVML_VGPU_PGPU_VIRTUALIZATION_CAP_MIGRATION = 0
NVML_VGPU_PGPU_VIRTUALIZATION_CAP_MIGRATION_NO = 0
NVML_VGPU_PGPU_VIRTUALIZATION_CAP_MIGRATION_YES = 1

# Added CUDA 10.2
NVML_VGPU_VIRTUALIZATION_CAP_MIGRATION = 0
NVML_VGPU_VIRTUALIZATION_CAP_MIGRATION_NO = 0
NVML_VGPU_VIRTUALIZATION_CAP_MIGRATION_YES = 1

# Added CUDA 9.0
_nvmlEncoderQueryType_t = c_uint
_nvmlEncoderType_t = c_uint
NVML_ENCODER_QUERY_H264 = 0
NVML_ENCODER_QUERY_HEVC = 1

# Added CUDA 10.0
_nvmlFBCSessionType_t = c_uint
NVML_FBC_SESSION_TYPE_UNKNOWN = 0
NVML_FBC_SESSION_TYPE_TOSYS = 1
NVML_FBC_SESSION_TYPE_CUDA = 2
NVML_FBC_SESSION_TYPE_VID = 3
NVML_FBC_SESSION_TYPE_HWENC = 4

# Added CUDA 10.0
_nvmlFBCStats_t = c_uint
NVML_NVFBC_SESSION_FLAG_DIFFMAP_ENABLED = 1
NVML_NVFBC_SESSION_FLAG_CLASSIFICATIONMAP_ENABLED = 2
NVML_NVFBC_SESSION_FLAG_CAPTURE_WITH_WAIT_NO_WAIT = 4
NVML_NVFBC_SESSION_FLAG_CAPTURE_WITH_WAIT_INFINITE = 8
NVML_NVFBC_SESSION_FLAG_CAPTURE_WITH_WAIT_TIMEOUT = 16

# Added CUDA 9.2
_nvmlDetachGpuState_t = c_uint
NVML_DETACH_GPU_KEEP = 0
NVML_DETACH_GPU_REMOVE = 1

# Added CUDA 9.2
_nvmlPcieLinkState_t = c_uint
NVML_PCIE_LINK_KEEP = 0
NVML_PCIE_LINK_SHUT_DOWN = 1

# Added CUDA 9.1
_nvmlInitializationAndCleanup_t = c_uint
NVML_INIT_FLAG_NO_GPUS = 1
# Added CUDA 9.2
NVML_INIT_FLAG_NO_ATTACH = 2

# buffer size
_nvmlConstants_t = c_uint
NVML_DEVICE_INFOROM_VERSION_BUFFER_SIZE = 16
NVML_DEVICE_UUID_BUFFER_SIZE = 80
NVML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE = 80
NVML_SYSTEM_NVML_VERSION_BUFFER_SIZE = 80
NVML_DEVICE_NAME_BUFFER_SIZE = 64
NVML_DEVICE_SERIAL_BUFFER_SIZE = 30
NVML_DEVICE_VBIOS_VERSION_BUFFER_SIZE = 32
NVML_DEVICE_PCI_BUS_ID_BUFFER_SIZE = 32
NVML_DEVICE_PCI_BUS_ID_BUFFER_V2_SIZE = 16
# Added CUDA 9.0
NVML_DEVICE_PART_NUMBER_BUFFER_SIZE = 80
# Added CUDA 11.0
NVML_DEVICE_UUID_V2_BUFFER_SIZE = 96

_nvmlAffinityScope_t = c_uint
NVML_AFFINITY_SCOPE_NODE = 0
NVML_AFFINITY_SCOPE_SOCKET = 1

NVML_DEVICE_MIG_DISABLE = 0
NVML_DEVICE_MIG_ENABLE = 1

NVML_GPU_INSTANCE_PROFILE_1_SLICE = 0
NVML_GPU_INSTANCE_PROFILE_2_SLICE = 1
NVML_GPU_INSTANCE_PROFILE_3_SLICE = 2
NVML_GPU_INSTANCE_PROFILE_4_SLICE = 3
NVML_GPU_INSTANCE_PROFILE_7_SLICE = 4
NVML_GPU_INSTANCE_PROFILE_COUNT = 5

NVML_COMPUTE_INSTANCE_ENGINE_PROFILE_SHARED = 0
NVML_COMPUTE_INSTANCE_ENGINE_PROFILE_COUNT = 1

## ========================================================================== ##
##                                                                            ##
##                              Library Loading                               ##
##                                                                            ##
## ========================================================================== ##

nvml_lib = None
lib_load_lock = threading.Lock()
nvml_lib_refcount = 0  # Incremented on each nvmlInit and decremented on nvmlShutdown


## ========================================================================== ##
##                                                                            ##
##                         Error-checking Functionality                       ##
##                                                                            ##
## ========================================================================== ##

class NVMLError(Exception):
    _val_mapping = dict()
    # List of currently known error codes
    _errcode_to_string = {
        NVML_ERROR_UNINITIALIZED: "Uninitialized",
        NVML_ERROR_INVALID_ARGUMENT: "Invalid Argument",
        NVML_ERROR_NOT_SUPPORTED: "Not Supported",
        NVML_ERROR_NO_PERMISSION: "Insufficient Permissions",
        NVML_ERROR_ALREADY_INITIALIZED: "Already Initialized",
        NVML_ERROR_NOT_FOUND: "Not Found",
        NVML_ERROR_INSUFFICIENT_SIZE: "Insufficient Size",
        NVML_ERROR_INSUFFICIENT_POWER: "Insufficient External Power",
        NVML_ERROR_DRIVER_NOT_LOADED: "Driver Not Loaded",
        NVML_ERROR_TIMEOUT: "Timeout",
        NVML_ERROR_IRQ_ISSUE: "Interrupt Request Issue",
        NVML_ERROR_LIBRARY_NOT_FOUND: "NVML Shared Library Not Found",
        NVML_ERROR_FUNCTION_NOT_FOUND: "Function Not Found",
        NVML_ERROR_CORRUPTED_INFOROM: "Corrupted infoROM",
        NVML_ERROR_GPU_IS_LOST: "GPU is lost",
        NVML_ERROR_RESET_REQUIRED: "GPU requires restart",
        NVML_ERROR_OPERATING_SYSTEM: "The operating system has blocked the request.",
        NVML_ERROR_LIB_RM_VERSION_MISMATCH: "RM has detected an NVML/RM version mismatch.",
        NVML_ERROR_UNKNOWN: "Unknown Error",
    }

    def __new__(typ, value):
        '''
        Maps value to a proper subclass of NVMLError.
        See _extract_errors_as_classes function for more details
        '''
        if typ == NVMLError:
            typ = NVMLError._val_mapping.get(value, typ)
        obj = Exception.__new__(typ)
        obj.value = value
        return obj

    def __str__(self):
        try:
            if self.value not in NVMLError._errcode_to_string:
                NVMLError._errcode_to_string[self.value] = str(nvml_error_string(self.value))
            return NVMLError._errcode_to_string[self.value]
        except NVMLError_Uninitialized:
            return "NVML Error with code %d" % self.value

    def __eq__(self, other):
        return self.value == other.value


def _extract_errors_as_classes():
    '''
    Generates a hierarchy of classes on top of NVMLError class.

    Each NVML Error gets a new NVMLError subclass. This way try,except blocks can filter appropriate
    exceptions more easily.

    NVMLError is a parent class. Each NVML_ERROR_* gets it's own subclass.
    e.g. NVML_ERROR_ALREADY_INITIALIZED will be turned into NVMLError_AlreadyInitialized
    '''
    this_module = sys.modules[__name__]
    nvmlErrorsNames = filter(lambda x: x.startswith("NVML_ERROR_"), dir(this_module))
    for err_name in nvmlErrorsNames:
        # e.g. Turn NVML_ERROR_ALREADY_INITIALIZED into NVMLError_AlreadyInitialized
        class_name = "NVMLError_" + string.capwords(err_name.replace("NVML_ERROR_", ""), "_").replace("_", "")
        err_val = getattr(this_module, err_name)

        def gen_new(val):
            def new(typ):
                obj = NVMLError.__new__(typ, val)
                return obj

            return new

        new_error_class = type(class_name, (NVMLError,), {'__new__': gen_new(err_val)})
        new_error_class.__module__ = __name__
        setattr(this_module, class_name, new_error_class)
        NVMLError._val_mapping[err_val] = new_error_class


_extract_errors_as_classes()


def check_return(ret):
    if (ret != NVML_SUCCESS):
        raise NVMLError(ret)
    return ret


## ========================================================================== ##
##                                                                            ##
##                          Library Function Access                           ##
##                                                                            ##
## ========================================================================== ##

_func_pointer_cache = dict()  # function pointers are cached to prevent unnecessary lib_load_lock locking


def get_func_pointer(name):
    global nvml_lib

    if name in _func_pointer_cache:
        return _func_pointer_cache[name]

    lib_load_lock.acquire()
    try:
        # ensure library was loaded
        if (nvml_lib == None):
            raise NVMLError(NVML_ERROR_UNINITIALIZED)
        try:
            _func_pointer_cache[name] = getattr(nvml_lib, name)
            return _func_pointer_cache[name]
        except AttributeError:
            raise NVMLError(NVML_ERROR_FUNCTION_NOT_FOUND)
    finally:
        # lock is always freed
        lib_load_lock.release()


## Alternative object
# Allows the object to be printed
# Allows mismatched types to be assigned
#  - like None when the Structure variant requires c_uint
class FriendlyObject(object):
    def __init__(self, dictionary):
        for x in dictionary:
            setattr(self, x, dictionary[x])

    def __str__(self):
        return self.__dict__.__str__()


def struct_to_friendly_object(struct):
    d = {}
    for x in struct._fields_:
        key = x[0]
        value = getattr(struct, key)
        d[key] = value
    obj = FriendlyObject(d)
    return obj


# pack the object so it can be passed to the NVML library
def friendly_object_to_struct(obj, model):
    for x in model._fields_:
        key = x[0]
        value = obj.__dict__[key]
        setattr(model, key, value)
    return model


## Unit structures
class struct_c_nvmlUnit_t(Structure):
    pass  # opaque handle


c_nvmlUnit_t = POINTER(struct_c_nvmlUnit_t)


class PrintableStructure(Structure):
    """
    Abstract class that produces nicer __str__ output than ctypes.Structure.
    e.g. instead of:
      >>> print str(obj)
      <class_name object at 0x7fdf82fef9e0>
    this class will print
      class_name(field_name: formatted_value, field_name: formatted_value)

    _fmt_ dictionary of <str _field_ name> -> <str format>
    e.g. class that has _field_ 'hex_value', c_uint could be formatted with
      _fmt_ = {"hex_value" : "%08X"}
    to produce nicer output.
    Default fomratting string for all fields can be set with key "<default>" like:
      _fmt_ = {"<default>" : "%d MHz"} # e.g all values are numbers in MHz.
    If not set it's assumed to be just "%s"

    Exact format of returned str from this class is subject to change in the future.
    """
    _fmt_ = {}

    def __str__(self):
        result = []
        for x in self._fields_:
            key = x[0]
            value = getattr(self, key)
            fmt = "%s"
            if key in self._fmt_:
                fmt = self._fmt_[key]
            elif "<default>" in self._fmt_:
                fmt = self._fmt_["<default>"]
            result.append(("%s: " + fmt) % (key, value))
        return self.__class__.__name__ + "(" + string.join(result, ", ") + ")"


## ========================================================================== ##
##                                                                            ##
##                         C-Type Class Definitions                           ##
##                                                                            ##
## ========================================================================== ##

class c_nvmlUnitInfo_t(PrintableStructure):
    _fields_ = [
        ('name', c_char * 96),
        ('id', c_char * 96),
        ('serial', c_char * 96),
        ('firmwareVersion', c_char * 96),
    ]


class c_nvmlLedState_t(PrintableStructure):
    _fields_ = [
        ('cause', c_char * 256),
        ('color', _nvmlLedColor_t),
    ]


class c_nvmlPSUInfo_t(PrintableStructure):
    _fields_ = [
        ('state', c_char * 256),
        ('current', c_uint),
        ('voltage', c_uint),
        ('power', c_uint),
    ]


class c_nvmlUnitFanInfo_t(PrintableStructure):
    _fields_ = [
        ('speed', c_uint),
        ('state', _nvmlFanState_t),
    ]


class c_nvmlUnitFanSpeeds_t(PrintableStructure):
    _fields_ = [
        ('fans', c_nvmlUnitFanInfo_t * 24),
        ('count', c_uint)
    ]


## Device structures
class struct_c_nvmlDevice_t(Structure):
    pass  # opaque handle


c_nvmlDevice_t = POINTER(struct_c_nvmlDevice_t)


class c_nvmlPciInfo_t(PrintableStructure):
    _fields_ = [
        # Changed from busId to busIdLegacy in CUDA 9.0
        ('busIdLegacy', c_char * NVML_DEVICE_PCI_BUS_ID_BUFFER_V2_SIZE),
        ('domain', c_uint),
        ('bus', c_uint),
        ('device', c_uint),
        ('pciDeviceId', c_uint),
        # Added in 2.285
        ('pciSubSystemId', c_uint),
        # Changed from reserved0-3 to busId in CUDA 9.0
        ('busId', c_char * NVML_DEVICE_PCI_BUS_ID_BUFFER_SIZE),
    ]
    _fmt_ = {
        'domain': "0x%04X",
        'bus': "0x%02X",
        'device': "0x%02X",
        'pciDeviceId': "0x%08X",
        'pciSubSystemId': "0x%08X",
    }


class nvmlPciInfo_t(c_nvmlPciInfo_t):
    pass


class c_nvmlEccErrorCounts_t(PrintableStructure):
    _fields_ = [
        ('l1Cache', c_ulonglong),
        ('l2Cache', c_ulonglong),
        ('deviceMemory', c_ulonglong),
        ('registerFile', c_ulonglong),
    ]


class c_nvmlUtilization_t(PrintableStructure):
    _fields_ = [
        ('gpu', c_uint),
        ('memory', c_uint),
    ]
    _fmt_ = {'<default>': "%d %%"}


class c_nvmlMemory_t(PrintableStructure):
    _fields_ = [
        ('total', c_ulonglong),
        ('free', c_ulonglong),
        ('used', c_ulonglong),
    ]
    _fmt_ = {'<default>': "%d B"}


class c_nvmlBAR1Memory_t(PrintableStructure):
    _fields_ = [
        ('bar1Total', c_ulonglong),
        ('bar1Free', c_ulonglong),
        ('bar1Used', c_ulonglong),
    ]
    _fmt_ = {'<default>': "%d B"}


# On Windows with the WDDM driver, usedGpuMemory is reported as None
# Code that processes this structure should check for None, I.E.
#
# if (info.usedGpuMemory == None):
#     # TODO handle the error
#     pass
# else:
#    print("Using %d MiB of memory" % (info.usedGpuMemory / 1024 / 1024))
#
# See NVML documentation for more information
class c_nvmlProcessInfo_t(PrintableStructure):
    _fields_ = [
        ('pid', c_uint),
        ('usedGpuMemory', c_ulonglong),
    ]
    _fmt_ = {'usedGpuMemory': "%d B"}


# Added CUDA 11.0
class c_nvmlDeviceAttributes_t(PrintableStructure):
    _fields_ = [
        ('multiprocessorCount', c_uint),
        ('sharedCopyEngineCount', c_uint),
        ('sharedDecoderCount', c_uint),
        ('sharedEncoderCount', c_uint),
        ('sharedJpegCount', c_uint),
        ('sharedOfaCount', c_uint),
    ]


# Added CUDA 9
class c_nvmlNvLinkUtilizationControl_t(PrintableStructure):
    _fields_ = [
        ('units', _nvmlNvLinkUtilizationCountUnits_t),
        ('pktfilter', _nvmlNvLinkUtilizationCountPktTypes_t),
    ]


class c_nvmlBridgeChipInfo_t(PrintableStructure):
    _fields_ = [
        ('type', _nvmlBridgeChipType_t),
        ('fwVersion', c_uint),
    ]


class c_nvmlBridgeChipHierarchy_t(PrintableStructure):
    _fields_ = [
        ('bridgeCount', c_uint),
        ('bridgeChipInfo', c_nvmlBridgeChipInfo_t * NVML_MAX_PHYSICAL_BRIDGE),
    ]


class c_nvmlValue_t(Union):
    _fields_ = [
        ('dVal', c_double),
        ('uiVal', c_uint),
        ('ulVal', c_ulong),
        ('ullVal', c_ulonglong),
    ]


class c_nvmlSample_t(PrintableStructure):
    _fields_ = [
        ('timeStamp', c_ulonglong),
        ('sampleValue', c_nvmlValue_t),
    ]


class c_nvmlViolationTime_t(PrintableStructure):
    _fields_ = [
        ('referenceTime', c_ulonglong),
        ('violationTime', c_ulonglong),
    ]


## VGPU Structures
# Added CUDA 9
_nvmlVgpuTypeId_t = c_uint;
_nvmlVgpuInstance_t = c_uint;


# Added CUDA 9.0
class c_nvmlVgpuInstanceUtilizationSample_t(PrintableStructure):
    _fields_ = [
        ('vgpuInstance', _nvmlVgpuInstance_t),
        ('timeStamp', c_ulonglong),
        ('smUtil', c_nvmlValue_t),
        ('memUtil', c_nvmlValue_t),
        ('encUtil', c_nvmlValue_t),
        ('decUtil', c_nvmlValue_t),
    ]


# Added CUDA 9.0
class c_nvmlVgpuProcessUtilizationSample_t(PrintableStructure):
    _fields_ = [
        ('vgpuInstance', _nvmlVgpuInstance_t),
        ('pid', c_uint),
        ('processName', c_char * NVML_VGPU_NAME_BUFFER_SIZE),
        ('timeStamp', c_ulonglong),
        ('smUtil', c_uint),
        ('memUtil', c_uint),
        ('encUtil', c_uint),
        ('decUtil', c_uint),
    ]


# Added CUDA 9
class c_nvmlProcessUtilizationSample_t(PrintableStructure):
    _fields_ = [
        ('pid', c_uint),
        ('timeStamp', c_ulonglong),
        ('smUtil', c_uint),
        ('memUtil', c_uint),
        ('encUtil', c_uint),
        ('decUtil', c_uint),
    ]


# Added CUDA 9
class c_nvmlGridLicensableFeature_t(PrintableStructure):
    _fields_ = [
        ('featureCode', _nvmlGridLicenseFeatureCode_t),
        ('featureState', c_uint),
        ('licenseInfo', c_char * NVML_GRID_LICENSE_BUFFER_SIZE),
        # Added CUDA 10.1
        ('productName', c_char * NVML_GRID_LICENSE_BUFFER_SIZE),
        # Added CUDA 10.2
        ('featureEnabled', c_uint),
    ]


# Added CUDA 9
class c_nvmlGridLicensableFeatures_t(PrintableStructure):
    _fields_ = [
        ('isGridLicenseSupported', c_int),
        ('licensableFeaturesCount', c_uint),
        ('gridLicensableFeatures', c_nvmlGridLicensableFeature_t * NVML_GRID_LICENSE_FEATURE_MAX_COUNT),
    ]


## Field Values
# Added CUDA 9.0
class c_nvmlFieldValue_t(PrintableStructure):
    _fields_ = [
        ('fieldId', c_uint),
        # Changed from unused to scopeId in CUDA 11.0
        ('scopeId', c_uint),
        ('timestamp', c_longlong),
        ('latencyUsec', c_longlong),
        ('valueType', _nvmlValueType_t),
        ('nvmlReturn', _nvmlReturn_t),
        ('value', c_nvmlValue_t),
    ]


## Unit structs
class struct_c_nvmlUnit_t(Structure):
    pass  # opaque handle


c_nvmlUnit_t = POINTER(struct_c_nvmlUnit_t)


# Added in 2.285
class c_nvmlHwbcEntry_t(PrintableStructure):
    _fields_ = [
        ('hwbcId', c_uint),
        ('firmwareVersion', c_char * 32),
    ]


# Added CUDA 9
class c_nvmlLedState_t(PrintableStructure):
    _fields_ = [
        ('cause', c_char * 256),
        ('color', _nvmlLedColor_t),
    ]


# Added CUDA 9
class c_nvmlUnitInfo_t(PrintableStructure):
    _fields_ = [
        ('name', c_char * 96),
        ('id', c_char * 96),
        ('serial', c_char * 96),
        ('firmwareVersion', c_char * 96),
    ]


# Added CUDA 9
class c_nvmlPSUInfo_t(PrintableStructure):
    _fields_ = [
        ('state', c_char * 256),
        ('current', c_uint),
        ('voltage', c_uint),
        ('power', c_uint),
    ]


# Added CUDA 9
class c_nvmlUnitFanInfo_t(PrintableStructure):
    _fields_ = [
        ('speed', c_uint),
        ('state', _nvmlFanState_t),
    ]


# Added CUDA 9
class c_nvmlUnitFanSpeeds_t(PrintableStructure):
    _fields_ = [
        ('fans', c_nvmlUnitFanInfo_t * 24),
        ('count', c_uint),
    ]


## Event structures
class struct_c_nvmlEventSet_t(Structure):
    pass  # opaque handle


c_nvmlEventSet_t = POINTER(struct_c_nvmlEventSet_t)

nvmlEventTypeSingleBitEccError = 0x0000000000000001
nvmlEventTypeDoubleBitEccError = 0x0000000000000002
nvmlEventTypePState = 0x0000000000000004
nvmlEventTypeXidCriticalError = 0x0000000000000008
nvmlEventTypeClock = 0x0000000000000010
nvmlEventTypeNone = 0x0000000000000000
nvmlEventTypeAll = (
        nvmlEventTypeNone |
        nvmlEventTypeSingleBitEccError |
        nvmlEventTypeDoubleBitEccError |
        nvmlEventTypePState |
        nvmlEventTypeClock |
        nvmlEventTypeXidCriticalError
)


class c_nvmlEventData_t(PrintableStructure):
    _fields_ = [
        ('device', c_nvmlDevice_t),
        ('eventType', c_ulonglong),
        ('eventData', c_ulonglong),
        # Added CUDA 11
        ('gpuInstanceId', c_uint),
        ('computeInstanceId', c_uint),
    ]
    _fmt_ = {'eventType': "0x%08X"}


## Clock Throttle Reasons defines
nvmlClocksThrottleReasonGpuIdle = 0x0000000000000001
nvmlClocksThrottleReasonApplicationsClocksSetting = 0x0000000000000002
nvmlClocksThrottleReasonUserDefinedClocks = nvmlClocksThrottleReasonApplicationsClocksSetting  # deprecated, use nvmlClocksThrottleReasonApplicationsClocksSetting
nvmlClocksThrottleReasonSwPowerCap = 0x0000000000000004
nvmlClocksThrottleReasonHwSlowdown = 0x0000000000000008
nvmlClocksThrottleReasonUnknown = 0x8000000000000000
nvmlClocksThrottleReasonNone = 0x0000000000000000
nvmlClocksThrottleReasonAll = (
        nvmlClocksThrottleReasonNone |
        nvmlClocksThrottleReasonGpuIdle |
        nvmlClocksThrottleReasonApplicationsClocksSetting |
        nvmlClocksThrottleReasonSwPowerCap |
        nvmlClocksThrottleReasonHwSlowdown |
        nvmlClocksThrottleReasonUnknown
)


## Account Statistics
class c_nvmlAccountingStats_t(PrintableStructure):
    _fields_ = [
        ('gpuUtilization', c_uint),
        ('memoryUtilization', c_uint),
        ('maxMemoryUsage', c_ulonglong),
        ('time', c_ulonglong),
        ('startTime', c_ulonglong),
        ('isRunning', c_uint),
        ('reserved', c_uint * 5)
    ]


## Encoder structs
# Added CUDA 9.0
class c_nvmlEncoderSessionInfo_t(PrintableStructure):
    _fields_ = [
        ('sessionId', c_uint),
        ('pid', c_uint),
        ('vgpuInstance', _nvmlVgpuInstance_t),
        ('codecType', _nvmlEncoderType_t),
        ('hResolution', c_uint),
        ('vResolution', c_uint),
        ('averageFps', c_uint),
        ('averageLatency', c_uint),
    ]


## Frame Buffer Capture Structures
# Added CUDA 10.0
class c_nvmlFBCStats_t(PrintableStructure):
    _fields_ = [
        ('sessionsCount', c_uint),
        ('averageFPS', c_uint),
        ('averageLatency', c_uint),
    ]


# Added CUDA 10.0
class c_nvmlFBCSessionInfo_t(PrintableStructure):
    _fields_ = [
        ('sessionId', c_uint),
        ('pid', c_uint),
        ('vgpuInstance', _nvmlVgpuInstance_t),
        ('displayOrdinal', c_uint),
        ('sessionType', _nvmlFBCSessionType_t),
        ('sessionFlags', c_uint),
        ('hMaxResolution', c_uint),
        ('vMaxResolution', c_uint),
        ('hResolution', c_uint),
        ('vResolution', c_uint),
        ('averageFPS', c_uint),
        ('averageLatency', c_uint),

    ]


# MIG Structures
# Added CUDA 11.0
class c_nvmlGpuInstancePlacement_t(PrintableStructure):
    _fields_ = [
        ('start', c_uint),
        ('size', c_uint)
    ]


# Added CUDA 11.0
class c_nvmlGpuInstanceProfileInfo_t(PrintableStructure):
    _fields_ = [
        ('id', c_uint),
        ('isP2pSupported', c_uint),
        ('sliceCount', c_uint),
        ('instanceCount', c_uint),
        ('multiprocessorCount', c_uint),
        ('copyEngineCount', c_uint),
        ('decoderCount', c_uint),
        ('encoderCount', c_uint),
        ('jpegCount', c_uint),
        ('ofaCount', c_uint),
        ('memorySizeMB', c_longlong)
    ]


# Added CUDA 11.0
class c_nvmlGpuInstanceInfo_t(PrintableStructure):
    _fields_ = [
        ('device', c_nvmlDevice_t),
        ('id', c_uint),
        ('profileId', c_uint),
        ('placement', c_nvmlGpuInstancePlacement_t)
    ]


class struct_c_nvmlGpuInstance_t(Structure):
    pass  # opaque handle


c_nvmlGpuInstance_t = POINTER(struct_c_nvmlGpuInstance_t)


class c_nvmlComputeInstanceProfileInfo_t(PrintableStructure):
    _fields_ = [
        ('id', c_uint),
        ('sliceCount', c_uint),
        ('instanceCount', c_uint),
        ('multiprocessorCount', c_uint),
        ('sharedCopyEngineCount', c_uint),
        ('sharedDecoderCount', c_uint),
        ('sharedEncoderCount', c_uint),
        ('sharedJpegCount', c_uint),
        ('sharedJpegCount', c_uint)
    ]


class c_nvmlComputeInstanceInfo_t(PrintableStructure):
    _fields_ = [
        ('device', c_nvmlDevice_t),
        ('gpuInstance', c_nvmlGpuInstance_t),
        ('id', c_uint),
        ('profileId', c_uint)
    ]


class struct_c_nvmlComputeInstance_t(Structure):
    pass  # opaque handle


c_nvmlComputeInstance_t = POINTER(struct_c_nvmlComputeInstance_t)


## ========================================================================== ##
##                                                                            ##
##                       NVML Library Function Wrappers                       ##
##                                                                            ##
## ========================================================================== ##

def _load_nvml_library():
    """
    Load the library if it isn't loaded already
    """
    global nvml_lib

    if (nvml_lib == None):
        # lock to ensure only one caller loads the library
        lib_load_lock.acquire()

        try:
            # ensure the library still isn't loaded
            if (nvml_lib == None):
                try:
                    if (sys.platform[:3] == "win"):
                        # cdecl calling convention
                        # load nvml.dll from %ProgramFiles%/NVIDIA Corporation/NVSMI/nvml.dll
                        nvml_lib = CDLL(os.path.join(os.getenv("ProgramFiles", "C:/Program Files"),
                                                     "NVIDIA Corporation/NVSMI/nvml.dll"))
                    else:
                        # assume linux
                        nvml_lib = CDLL("libnvidia-ml.so.1")
                except OSError as ose:
                    check_return(NVML_ERROR_LIBRARY_NOT_FOUND)
                if (nvml_lib == None):
                    check_return(NVML_ERROR_LIBRARY_NOT_FOUND)
        finally:
            # lock is always freed
            lib_load_lock.release()


def nvmlInit():
    """Initialize NVML.

    Uses nvmlInit_v2() from the underlying NVML library.

    Args:
        None

    Returns:
        None
    """

    #
    # Initialize the library
    #
    _load_nvml_library()

    fn = get_func_pointer("nvmlInit_v2")
    ret = fn()
    check_return(ret)

    # Atomically update refcount
    global nvml_lib_refcount
    lib_load_lock.acquire()
    nvml_lib_refcount += 1
    lib_load_lock.release()
    return None


def nvmlInitWithFlags(flags):
    _load_nvml_library()

    fn = get_func_pointer("nvmlInitWithFlags")
    ret = fn(c_uint(flags))
    check_return(ret)

    # Atomically update refcount
    global nvml_lib_refcount
    lib_load_lock.acquire()
    nvml_lib_refcount += 1
    lib_load_lock.release()
    return None


def nvmlShutdown():
    """Shutdown NVML.

    Uses nvmlShutdown() from the underlying NVML library.

    Args:
        None

    Returns:
        None
    """
    #
    # Leave the library loaded, but shutdown the interface
    #
    fn = get_func_pointer("nvmlShutdown")
    ret = fn()
    check_return(ret)

    # Atomically update refcount
    global nvml_lib_refcount
    lib_load_lock.acquire()
    if (0 < nvml_lib_refcount):
        nvml_lib_refcount -= 1
    lib_load_lock.release()
    return None


# Added in 2.285
def nvml_error_string(result):
    fn = get_func_pointer("nvmlErrorString")
    fn.restype = c_char_p  # otherwise return is an int
    ret = fn(result)
    return ret


# Added in 2.285
def nvmlSystemGetNVMLVersion():
    c_version = create_string_buffer(NVML_SYSTEM_NVML_VERSION_BUFFER_SIZE)
    fn = get_func_pointer("nvmlSystemGetNVMLVersion")
    ret = fn(c_version, c_uint(NVML_SYSTEM_NVML_VERSION_BUFFER_SIZE))
    check_return(ret)
    return c_version.value


# Added in 2.285
def nvmlSystemGetProcessName(pid):
    c_name = create_string_buffer(1024)
    fn = get_func_pointer("nvmlSystemGetProcessName")
    ret = fn(c_uint(pid), c_name, c_uint(1024))
    check_return(ret)
    return c_name.value


def nvmlSystemGetDriverVersion():
    c_version = create_string_buffer(NVML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE)
    fn = get_func_pointer("nvmlSystemGetDriverVersion")
    ret = fn(c_version, c_uint(NVML_SYSTEM_DRIVER_VERSION_BUFFER_SIZE))
    check_return(ret)
    return c_version.value


def nvmlSystemGetCudaDriverVersion():
    ver = c_int(0);
    fn = get_func_pointer("nvmlSystemGetCudaDriverVersion")
    ret = fn(byref(ver))
    check_return(ret)
    return ver.value


# Added in 2.285
def nvmlSystemGetHicVersion():
    c_count = c_uint(0)
    hics = None
    fn = get_func_pointer("nvmlSystemGetHicVersion")

    # get the count
    ret = fn(byref(c_count), None)

    # this should only fail with insufficient size
    if ((ret != NVML_SUCCESS) and
            (ret != NVML_ERROR_INSUFFICIENT_SIZE)):
        raise NVMLError(ret)

    # if there are no hics
    if (c_count.value == 0):
        return []

    hic_array = c_nvmlHwbcEntry_t * c_count.value
    hics = hic_array()
    ret = fn(byref(c_count), hics)
    check_return(ret)
    return hics


## Unit get functions
def nvmlUnitGetCount():
    c_count = c_uint()
    fn = get_func_pointer("nvmlUnitGetCount")
    ret = fn(byref(c_count))
    check_return(ret)
    return c_count.value


def nvmlUnitGetHandleByIndex(index):
    c_index = c_uint(index)
    unit = c_nvmlUnit_t()
    fn = get_func_pointer("nvmlUnitGetHandleByIndex")
    ret = fn(c_index, byref(unit))
    check_return(ret)
    return unit


def nvmlUnitGetUnitInfo(unit):
    c_info = c_nvmlUnitInfo_t()
    fn = get_func_pointer("nvmlUnitGetUnitInfo")
    ret = fn(unit, byref(c_info))
    check_return(ret)
    return c_info


def nvmlUnitGetLedState(unit):
    c_state = c_nvmlLedState_t()
    fn = get_func_pointer("nvmlUnitGetLedState")
    ret = fn(unit, byref(c_state))
    check_return(ret)
    return c_state


def nvmlUnitGetPsuInfo(unit):
    c_info = c_nvmlPSUInfo_t()
    fn = get_func_pointer("nvmlUnitGetPsuInfo")
    ret = fn(unit, byref(c_info))
    check_return(ret)
    return c_info


def nvmlUnitGetTemperature(unit, type):
    c_temp = c_uint()
    fn = get_func_pointer("nvmlUnitGetTemperature")
    ret = fn(unit, c_uint(type), byref(c_temp))
    check_return(ret)
    return c_temp.value


def nvmlUnitGetFanSpeedInfo(unit):
    c_speeds = c_nvmlUnitFanSpeeds_t()
    fn = get_func_pointer("nvmlUnitGetFanSpeedInfo")
    ret = fn(unit, byref(c_speeds))
    check_return(ret)
    return c_speeds


# added to API
def nvmlUnitGetDeviceCount(unit):
    c_count = c_uint(0)
    # query the unit to determine device count
    fn = get_func_pointer("nvmlUnitGetDevices")
    ret = fn(unit, byref(c_count), None)
    if (ret == NVML_ERROR_INSUFFICIENT_SIZE):
        ret = NVML_SUCCESS
    check_return(ret)
    return c_count.value


def nvmlUnitGetDevices(unit):
    c_count = c_uint(nvmlUnitGetDeviceCount(unit))
    device_array = c_nvmlDevice_t * c_count.value
    c_devices = device_array()
    fn = get_func_pointer("nvmlUnitGetDevices")
    ret = fn(unit, byref(c_count), c_devices)
    check_return(ret)
    return c_devices


## Device get functions
def nvmlDeviceGetCount():
    c_count = c_uint()
    fn = get_func_pointer("nvmlDeviceGetCount_v2")
    ret = fn(byref(c_count))
    check_return(ret)
    return c_count.value


def nvmlDeviceGetAttributes(handle):
    attributes = c_nvmlDeviceAttributes_t()
    fn = get_func_pointer("nvmlDeviceGetAttributes")
    ret = fn(handle, byref(attributes))
    check_return(ret)
    return attributes


def nvmlDeviceGetHandleByIndex(index):
    c_index = c_uint(index)
    device = c_nvmlDevice_t()
    fn = get_func_pointer("nvmlDeviceGetHandleByIndex_v2")
    ret = fn(c_index, byref(device))
    check_return(ret)
    return device


def nvmlDeviceGetHandleBySerial(serial):
    c_serial = c_char_p(serial)
    device = c_nvmlDevice_t()
    fn = get_func_pointer("nvmlDeviceGetHandleBySerial")
    ret = fn(c_serial, byref(device))
    check_return(ret)
    return device


def nvmlDeviceGetHandleByUUID(uuid):
    c_uuid = c_char_p(uuid)
    device = c_nvmlDevice_t()
    fn = get_func_pointer("nvmlDeviceGetHandleByUUID")
    ret = fn(c_uuid, byref(device))
    check_return(ret)
    return device


def nvmlDeviceGetHandleByPciBusId(pciBusId):
    c_busId = c_char_p(pciBusId)
    device = c_nvmlDevice_t()
    fn = get_func_pointer("nvmlDeviceGetHandleByPciBusId_v2")
    ret = fn(c_busId, byref(device))
    check_return(ret)
    return device


def nvmlDeviceGetName(handle):
    c_name = create_string_buffer(NVML_DEVICE_NAME_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetName")
    ret = fn(handle, c_name, c_uint(NVML_DEVICE_NAME_BUFFER_SIZE))
    check_return(ret)
    return c_name.value


def nvmlDeviceGetBoardId(handle):
    c_id = c_uint();
    fn = get_func_pointer("nvmlDeviceGetBoardId")
    ret = fn(handle, byref(c_id))
    check_return(ret)
    return c_id.value


def nvmlDeviceGetMultiGpuBoard(handle):
    c_multiGpu = c_uint();
    fn = get_func_pointer("nvmlDeviceGetMultiGpuBoard")
    ret = fn(handle, byref(c_multiGpu))
    check_return(ret)
    return c_multiGpu.value


def nvmlDeviceGetBrand(handle):
    c_type = _nvmlBrandType_t()
    fn = get_func_pointer("nvmlDeviceGetBrand")
    ret = fn(handle, byref(c_type))
    check_return(ret)
    return c_type.value


def nvmlDeviceGetSerial(handle):
    c_serial = create_string_buffer(NVML_DEVICE_SERIAL_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetSerial")
    ret = fn(handle, c_serial, c_uint(NVML_DEVICE_SERIAL_BUFFER_SIZE))
    check_return(ret)
    return c_serial.value


def nvmlDeviceGetMemoryAffinity(handle, nodeSetSize, scope):
    nodeSet_array = c_ulonglong * nodeSetSize
    c_affinity = nodeSet_array()
    fn = get_func_pointer("nvmlDeviceGetMemoryAffinity")
    ret = fn(handle, nodeSetSize, byref(c_affinity), scope)
    check_return(ret)
    return c_affinity


def nvmlDeviceGetCpuAffinity(handle, cpuSetSize):
    affinity_array = c_ulonglong * cpuSetSize
    c_affinity = affinity_array()
    fn = get_func_pointer("nvmlDeviceGetCpuAffinity")
    ret = fn(handle, cpuSetSize, byref(c_affinity))
    check_return(ret)
    return c_affinity


def nvmlDeviceGetCpuAffinityWithinScope(handle, cpuSetSize, scope):
    affinity_array = c_ulonglong * cpuSetSize
    c_affinity = affinity_array()
    fn = get_func_pointer("nvmlDeviceGetCpuAffinityWithinScope")
    ret = fn(handle, cpuSetSize, byref(c_affinity), scope)
    check_return(ret)
    return c_affinity


def nvmlDeviceSetCpuAffinity(handle):
    fn = get_func_pointer("nvmlDeviceSetCpuAffinity")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceClearCpuAffinity(handle):
    fn = get_func_pointer("nvmlDeviceClearCpuAffinity")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceGetMinorNumber(handle):
    c_minor_number = c_uint()
    fn = get_func_pointer("nvmlDeviceGetMinorNumber")
    ret = fn(handle, byref(c_minor_number))
    check_return(ret)
    return c_minor_number.value


def nvmlDeviceGetP2PStatus(handle1, handle2, index):
    status = nvmlGpuP2PStatus_t()
    fn = get_func_pointer("nvmlDeviceGetP2PStatus")
    ret = fn(handle1, handle2, index, byref(status))
    check_return(ret)
    return status


def nvmlDeviceGetUUID(handle):
    c_uuid = create_string_buffer(NVML_DEVICE_UUID_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetUUID")
    ret = fn(handle, byref(c_uuid), c_uint(NVML_DEVICE_UUID_BUFFER_SIZE))
    check_return(ret)
    return c_uuid.value


def nvmlVgpuInstanceGetMdevUUID(vgpuInstance):
    c_mdevUuid = create_string_buffer(NVML_DEVICE_UUID_BUFFER_SIZE)
    fn = get_func_pointer("nvmlVgpuInstanceGetMdevUUID")
    ret = fn(vgpuInstance, c_mdevUuid, NVML_DEVICE_UUID_BUFFER_SIZE)
    check_return(ret)
    return c_mdevUuid.value


def nvmlDeviceGetBoardPartNumber(handle):
    length = c_uint(256)
    c_partNumber = create_string_buffer(length)
    fn = get_func_pointer("nvmlDeviceGetBoardPartNumber")
    ret = fn(handle, byref(c_partNumber), length)
    check_return(ret)
    return c_partNumber.value


def nvmlDeviceGetInforomVersion(handle, infoRomObject):
    c_version = create_string_buffer(NVML_DEVICE_INFOROM_VERSION_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetInforomVersion")
    ret = fn(handle, _nvmlInforomObject_t(infoRomObject),
             c_version, c_uint(NVML_DEVICE_INFOROM_VERSION_BUFFER_SIZE))
    check_return(ret)
    return c_version.value


# Added in 4.304
def nvmlDeviceGetInforomImageVersion(handle):
    c_version = create_string_buffer(NVML_DEVICE_INFOROM_VERSION_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetInforomImageVersion")
    ret = fn(handle, c_version, c_uint(NVML_DEVICE_INFOROM_VERSION_BUFFER_SIZE))
    check_return(ret)
    return c_version.value


# Added in 4.304
def nvmlDeviceGetInforomConfigurationChecksum(handle):
    c_checksum = c_uint()
    fn = get_func_pointer("nvmlDeviceGetInforomConfigurationChecksum")
    ret = fn(handle, byref(c_checksum))
    check_return(ret)
    return c_checksum.value


# Added in 4.304
def nvmlDeviceValidateInforom(handle):
    fn = get_func_pointer("nvmlDeviceValidateInforom")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceGetDisplayMode(handle):
    c_mode = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetDisplayMode")
    ret = fn(handle, byref(c_mode))
    check_return(ret)
    return c_mode.value


def nvmlDeviceGetDisplayActive(handle):
    c_mode = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetDisplayActive")
    ret = fn(handle, byref(c_mode))
    check_return(ret)
    return c_mode.value


def nvmlDeviceGetPersistenceMode(handle):
    c_state = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetPersistenceMode")
    ret = fn(handle, byref(c_state))
    check_return(ret)
    return c_state.value


def nvmlDeviceGetPciInfo(handle):
    c_info = nvmlPciInfo_t()
    try:
        fn = get_func_pointer("nvmlDeviceGetPciInfo_v3")
    except AttributeError:
        fn = get_func_pointer("nvmlDeviceGetPciInfo_v2")
    ret = fn(handle, byref(c_info))
    check_return(ret)
    return c_info


def nvmlDeviceGetClockInfo(handle, type):
    c_clock = c_uint()
    fn = get_func_pointer("nvmlDeviceGetClockInfo")
    ret = fn(handle, _nvmlClockType_t(type), byref(c_clock))
    check_return(ret)
    return c_clock.value


# Added in 2.285
def nvmlDeviceGetMaxClockInfo(handle, type):
    c_clock = c_uint()
    fn = get_func_pointer("nvmlDeviceGetMaxClockInfo")
    ret = fn(handle, _nvmlClockType_t(type), byref(c_clock))
    check_return(ret)
    return c_clock.value


# Added in 4.304
def nvmlDeviceGetApplicationsClock(handle, type):
    c_clock = c_uint()
    fn = get_func_pointer("nvmlDeviceGetApplicationsClock")
    ret = fn(handle, _nvmlClockType_t(type), byref(c_clock))
    check_return(ret)
    return c_clock.value


# Added in 5.319
def nvmlDeviceGetDefaultApplicationsClock(handle, type):
    c_clock = c_uint()
    fn = get_func_pointer("nvmlDeviceGetDefaultApplicationsClock")
    ret = fn(handle, _nvmlClockType_t(type), byref(c_clock))
    check_return(ret)
    return c_clock.value


# Added in 4.304
def nvmlDeviceGetSupportedMemoryClocks(handle):
    # first call to get the size
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetSupportedMemoryClocks")
    ret = fn(handle, byref(c_count), None)

    if (ret == NVML_SUCCESS):
        # special case, no clocks
        return []
    elif (ret == NVML_ERROR_INSUFFICIENT_SIZE):
        # typical case
        clocks_array = c_uint * c_count.value
        c_clocks = clocks_array()

        # make the call again
        ret = fn(handle, byref(c_count), c_clocks)
        check_return(ret)

        procs = []
        for i in range(c_count.value):
            procs.append(c_clocks[i])

        return procs
    else:
        # error case
        raise NVMLError(ret)


# Added in 4.304
def nvmlDeviceGetSupportedGraphicsClocks(handle, memoryClockMHz):
    # first call to get the size
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetSupportedGraphicsClocks")
    ret = fn(handle, c_uint(memoryClockMHz), byref(c_count), None)

    if (ret == NVML_SUCCESS):
        # special case, no clocks
        return []
    elif (ret == NVML_ERROR_INSUFFICIENT_SIZE):
        # typical case
        clocks_array = c_uint * c_count.value
        c_clocks = clocks_array()

        # make the call again
        ret = fn(handle, c_uint(memoryClockMHz), byref(c_count), c_clocks)
        check_return(ret)

        procs = []
        for i in range(c_count.value):
            procs.append(c_clocks[i])

        return procs
    else:
        # error case
        raise NVMLError(ret)


def nvmlDeviceGetFanSpeed(handle):
    c_speed = c_uint()
    fn = get_func_pointer("nvmlDeviceGetFanSpeed")
    ret = fn(handle, byref(c_speed))
    check_return(ret)
    return c_speed.value


def nvmlDeviceGetFanSpeed_v2(handle, fan):
    c_speed = c_uint()
    fn = get_func_pointer("nvmlDeviceGetFanSpeed_v2")
    ret = fn(handle, c_uint(fan), byref(c_speed))
    check_return(ret)
    return c_speed.value


def nvmlDeviceGetTemperature(handle, sensor):
    c_temp = c_uint()
    fn = get_func_pointer("nvmlDeviceGetTemperature")
    ret = fn(handle, _nvmlTemperatureSensors_t(sensor), byref(c_temp))
    check_return(ret)
    return c_temp.value


def nvmlDeviceGetTemperatureThreshold(handle, threshold):
    c_temp = c_uint()
    fn = get_func_pointer("nvmlDeviceGetTemperatureThreshold")
    ret = fn(handle, _nvmlTemperatureThresholds_t(threshold), byref(c_temp))
    check_return(ret)
    return c_temp.value


# DEPRECATED use nvmlDeviceGetPerformanceState
def nvmlDeviceGetPowerState(handle):
    c_pstate = _nvmlPstates_t()
    fn = get_func_pointer("nvmlDeviceGetPowerState")
    ret = fn(handle, byref(c_pstate))
    check_return(ret)
    return c_pstate.value


def nvmlDeviceGetPerformanceState(handle):
    c_pstate = _nvmlPstates_t()
    fn = get_func_pointer("nvmlDeviceGetPerformanceState")
    ret = fn(handle, byref(c_pstate))
    check_return(ret)
    return c_pstate.value


def nvmlDeviceGetPowerManagementMode(handle):
    c_pcapMode = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetPowerManagementMode")
    ret = fn(handle, byref(c_pcapMode))
    check_return(ret)
    return c_pcapMode.value


def nvmlDeviceGetPowerManagementLimit(handle):
    c_limit = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPowerManagementLimit")
    ret = fn(handle, byref(c_limit))
    check_return(ret)
    return c_limit.value


# Added in 4.304
def nvmlDeviceGetPowerManagementLimitConstraints(handle):
    c_minLimit = c_uint()
    c_maxLimit = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPowerManagementLimitConstraints")
    ret = fn(handle, byref(c_minLimit), byref(c_maxLimit))
    check_return(ret)
    return [c_minLimit.value, c_maxLimit.value]


# Added in 4.304
def nvmlDeviceGetPowerManagementDefaultLimit(handle):
    c_limit = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPowerManagementDefaultLimit")
    ret = fn(handle, byref(c_limit))
    check_return(ret)
    return c_limit.value


# Added in 331
def nvmlDeviceGetEnforcedPowerLimit(handle):
    c_limit = c_uint()
    fn = get_func_pointer("nvmlDeviceGetEnforcedPowerLimit")
    ret = fn(handle, byref(c_limit))
    check_return(ret)
    return c_limit.value


def nvmlDeviceGetPowerUsage(handle):
    c_mWatts = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPowerUsage")
    ret = fn(handle, byref(c_mWatts))
    check_return(ret)
    return c_mWatts.value


def nvmlDeviceGetTotalEnergyConsumption(handle):
    c_mJoules = c_uint()
    fn = get_func_pointer("nvmlDeviceGetTotalEnergyConsumption")
    ret = fn(handle, byref(c_mJoules))
    check_return(ret)
    return c_mJoules.value


# Added in 4.304
def nvmlDeviceGetGpuOperationMode(handle):
    c_currState = _nvmlGpuOperationMode_t()
    c_pendingState = _nvmlGpuOperationMode_t()
    fn = get_func_pointer("nvmlDeviceGetGpuOperationMode")
    ret = fn(handle, byref(c_currState), byref(c_pendingState))
    check_return(ret)
    return [c_currState.value, c_pendingState.value]


# Added in 4.304
def nvmlDeviceGetCurrentGpuOperationMode(handle):
    return nvmlDeviceGetGpuOperationMode(handle)[0]


# Added in 4.304
def nvmlDeviceGetPendingGpuOperationMode(handle):
    return nvmlDeviceGetGpuOperationMode(handle)[1]


def nvmlDeviceGetMemoryInfo(handle):
    """Retrieves memory object.

    Return object includes the amount of used, free and total memory available
    on the device, in bytes.

    Args:
        handle: The identifier of the target device

    Returns:
        memory: The return value. An `nvmlMemory_t` object

    """
    c_memory = c_nvmlMemory_t()
    fn = get_func_pointer("nvmlDeviceGetMemoryInfo")
    ret = fn(handle, byref(c_memory))
    check_return(ret)
    return c_memory


def nvmlDeviceGetBAR1MemoryInfo(handle):
    c_bar1_memory = c_nvmlBAR1Memory_t()
    fn = get_func_pointer("nvmlDeviceGetBAR1MemoryInfo")
    ret = fn(handle, byref(c_bar1_memory))
    check_return(ret)
    return c_bar1_memory


def nvmlDeviceGetComputeMode(handle):
    c_mode = _nvmlComputeMode_t()
    fn = get_func_pointer("nvmlDeviceGetComputeMode")
    ret = fn(handle, byref(c_mode))
    check_return(ret)
    return c_mode.value


def nvmlDeviceGetCudaComputeCapability(handle):
    major = c_int(0)
    minor = c_int(0)
    fn = get_func_pointer("nvmlDeviceGetCudaComputeCapability")
    ret = fn(handle, byref(major), byref(minor))
    check_return(ret)
    return [major.value, minor.value]


def nvmlDeviceGetEccMode(handle):
    c_currState = _nvmlEnableState_t()
    c_pendingState = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetEccMode")
    ret = fn(handle, byref(c_currState), byref(c_pendingState))
    check_return(ret)
    return [c_currState.value, c_pendingState.value]


# added to API
def nvmlDeviceGetCurrentEccMode(handle):
    return nvmlDeviceGetEccMode(handle)[0]


# added to API
def nvmlDeviceGetPendingEccMode(handle):
    return nvmlDeviceGetEccMode(handle)[1]


def nvmlDeviceGetTotalEccErrors(handle, errorType, counterType):
    c_count = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetTotalEccErrors")
    ret = fn(handle, _nvmlMemoryErrorType_t(errorType),
             _nvmlEccCounterType_t(counterType), byref(c_count))
    check_return(ret)
    return c_count.value


# This is deprecated, instead use nvmlDeviceGetMemoryErrorCounter
def nvmlDeviceGetDetailedEccErrors(handle, errorType, counterType):
    c_counts = c_nvmlEccErrorCounts_t()
    fn = get_func_pointer("nvmlDeviceGetDetailedEccErrors")
    ret = fn(handle, _nvmlMemoryErrorType_t(errorType),
             _nvmlEccCounterType_t(counterType), byref(c_counts))
    check_return(ret)
    return c_counts


# Added in 4.304
def nvmlDeviceGetMemoryErrorCounter(handle, errorType, counterType, locationType):
    c_count = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetMemoryErrorCounter")
    ret = fn(handle,
             _nvmlMemoryErrorType_t(errorType),
             _nvmlEccCounterType_t(counterType),
             _nvmlMemoryLocation_t(locationType),
             byref(c_count))
    check_return(ret)
    return c_count.value


def nvmlDeviceGetUtilizationRates(handle):
    c_util = c_nvmlUtilization_t()
    fn = get_func_pointer("nvmlDeviceGetUtilizationRates")
    ret = fn(handle, byref(c_util))
    check_return(ret)
    return c_util


def nvmlDeviceGetEncoderUtilization(handle):
    c_util = c_uint()
    c_samplingPeriod = c_uint()
    fn = get_func_pointer("nvmlDeviceGetEncoderUtilization")
    ret = fn(handle, byref(c_util), byref(c_samplingPeriod))
    check_return(ret)
    return [c_util.value, c_samplingPeriod.value]


def nvmlDeviceGetEncoderCapacity(handle, encoderType):
    capacity = c_uint()
    fn = get_func_pointer("nvmlDeviceGetEncoderCapacity")
    ret = fn(handle, _nvmlEncoderType_t(encoderType), byref(capacity))
    check_return(ret)
    return capacity.value


def nvmlDeviceGetEncoderStats(handle):
    count = c_uint()
    fps = c_uint()
    latency = c_uint()
    fn = get_func_pointer("nvmlDeviceGetEncoderStats")
    ret = fn(handle, byref(count), byref(fps), byref(latency))
    check_return(ret)
    return [count.value, fps.value, latency.value]


def nvmlDeviceGetEncoderSessions(handle):
    count = c_uint()
    info = c_nvmlEncoderSessionInfo_t()
    fn = get_func_pointer("nvmlDeviceGetEncoderSessions")
    ret = fn(handle, byref(count), byref(info))
    check_return(ret)
    return [count.value, info]


def nvmlDeviceGetDecoderUtilization(handle):
    c_util = c_uint()
    c_samplingPeriod = c_uint()
    fn = get_func_pointer("nvmlDeviceGetDecoderUtilization")
    ret = fn(handle, byref(c_util), byref(c_samplingPeriod))
    check_return(ret)
    return [c_util.value, c_samplingPeriod.value]


def nvmlDeviceGetFBCStats(handle):
    stats = c_nvmlFBCStats_t()
    fn = get_func_pointer("nvmlDeviceGetFBCStats")
    ret = fn(handle, byref(stats))
    check_return(ret)
    return stats


def nvmlDeviceGetFBCSessions(handle):
    info = c_nvmlFBCSessionInfo_t()
    count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetFBCSessions")
    fn(handle, byref(count), byref(info))
    ret = fn(handle, byref(count), byref(info))
    check_return(ret)
    return [count.value, info]


def nvmlDeviceGetPcieReplayCounter(handle):
    c_replay = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPcieReplayCounter")
    ret = fn(handle, byref(c_replay))
    check_return(ret)
    return c_replay.value


def nvmlDeviceGetDriverModel(handle):
    c_currModel = _nvmlDriverModel_t()
    c_pendingModel = _nvmlDriverModel_t()
    fn = get_func_pointer("nvmlDeviceGetDriverModel")
    ret = fn(handle, byref(c_currModel), byref(c_pendingModel))
    check_return(ret)
    return [c_currModel.value, c_pendingModel.value]


# added to API
def nvmlDeviceGetCurrentDriverModel(handle):
    return nvmlDeviceGetDriverModel(handle)[0]


# added to API
def nvmlDeviceGetPendingDriverModel(handle):
    return nvmlDeviceGetDriverModel(handle)[1]


# Added in 2.285
def nvmlDeviceGetVbiosVersion(handle):
    c_version = create_string_buffer(NVML_DEVICE_VBIOS_VERSION_BUFFER_SIZE)
    fn = get_func_pointer("nvmlDeviceGetVbiosVersion")
    ret = fn(handle, c_version, c_uint(NVML_DEVICE_VBIOS_VERSION_BUFFER_SIZE))
    check_return(ret)
    return c_version.value


# Added in 2.285
def nvmlDeviceGetComputeRunningProcesses(handle):
    # first call to get the size
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetComputeRunningProcesses")
    ret = fn(handle, byref(c_count), None)

    if (ret == NVML_SUCCESS):
        # special case, no running processes
        return []
    elif (ret == NVML_ERROR_INSUFFICIENT_SIZE):
        # typical case
        # oversize the array incase more processes are created
        c_count.value = c_count.value * 2 + 5
        proc_array = c_nvmlProcessInfo_t * c_count.value
        c_procs = proc_array()

        # make the call again
        ret = fn(handle, byref(c_count), c_procs)
        check_return(ret)

        procs = []
        for i in range(c_count.value):
            # use an alternative struct for this object
            obj = struct_to_friendly_object(c_procs[i])
            if (obj.usedGpuMemory == NVML_VALUE_NOT_AVAILABLE_ulonglong.value):
                # special case for WDDM on Windows, see comment above
                obj.usedGpuMemory = None
            procs.append(obj)

        return procs
    else:
        # error case
        raise NVMLError(ret)


def nvmlDeviceGetGraphicsRunningProcesses(handle):
    # first call to get the size
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetGraphicsRunningProcesses")
    ret = fn(handle, byref(c_count), None)

    if (ret == NVML_SUCCESS):
        # special case, no running processes
        return []
    elif (ret == NVML_ERROR_INSUFFICIENT_SIZE):
        # typical case
        # oversize the array incase more processes are created
        c_count.value = c_count.value * 2 + 5
        proc_array = c_nvmlProcessInfo_t * c_count.value
        c_procs = proc_array()

        # make the call again
        ret = fn(handle, byref(c_count), c_procs)
        check_return(ret)

        procs = []
        for i in range(c_count.value):
            # use an alternative struct for this object
            obj = struct_to_friendly_object(c_procs[i])
            if (obj.usedGpuMemory == NVML_VALUE_NOT_AVAILABLE_ulonglong.value):
                # special case for WDDM on Windows, see comment above
                obj.usedGpuMemory = None
            procs.append(obj)

        return procs
    else:
        # error case
        raise NVMLError(ret)


def nvmlDeviceGetAutoBoostedClocksEnabled(handle):
    c_isEnabled = _nvmlEnableState_t()
    c_defaultIsEnabled = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetAutoBoostedClocksEnabled")
    ret = fn(handle, byref(c_isEnabled), byref(c_defaultIsEnabled))
    check_return(ret)
    return [c_isEnabled.value, c_defaultIsEnabled.value]
    # Throws NVML_ERROR_NOT_SUPPORTED if hardware doesn't support setting auto boosted clocks


## Set functions
def nvmlUnitSetLedState(unit, color):
    fn = get_func_pointer("nvmlUnitSetLedState")
    ret = fn(unit, _nvmlLedColor_t(color))
    check_return(ret)
    return None


def nvmlDeviceSetPersistenceMode(handle, mode):
    fn = get_func_pointer("nvmlDeviceSetPersistenceMode")
    ret = fn(handle, _nvmlEnableState_t(mode))
    check_return(ret)
    return None


def nvmlDeviceSetComputeMode(handle, mode):
    fn = get_func_pointer("nvmlDeviceSetComputeMode")
    ret = fn(handle, _nvmlComputeMode_t(mode))
    check_return(ret)
    return None


def nvmlDeviceSetEccMode(handle, mode):
    fn = get_func_pointer("nvmlDeviceSetEccMode")
    ret = fn(handle, _nvmlEnableState_t(mode))
    check_return(ret)
    return None


def nvmlDeviceClearEccErrorCounts(handle, counterType):
    fn = get_func_pointer("nvmlDeviceClearEccErrorCounts")
    ret = fn(handle, _nvmlEccCounterType_t(counterType))
    check_return(ret)
    return None


def nvmlDeviceSetDriverModel(handle, model):
    fn = get_func_pointer("nvmlDeviceSetDriverModel")
    ret = fn(handle, _nvmlDriverModel_t(model))
    check_return(ret)
    return None


def nvmlDeviceSetGpuLockedClocks(handle, minClock, maxClock):
    fn = get_func_pointer("nvmlDeviceSetGpuLockedClocks")
    ret = fn(handle, c_uint(minClock), c_uint(maxClock))
    check_return(ret)
    return None


def nvmlDeviceResetGpuLockedClocks(handle):
    fn = get_func_pointer("nvmlDeviceResetGpuLockedClocks")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceSetAutoBoostedClocksEnabled(handle, enabled):
    fn = get_func_pointer("nvmlDeviceSetAutoBoostedClocksEnabled")
    ret = fn(handle, _nvmlEnableState_t(enabled))
    check_return(ret)
    return None
    # Throws NVML_ERROR_NOT_SUPPORTED if hardware doesn't support setting auto boosted clocks


def nvmlDeviceSetDefaultAutoBoostedClocksEnabled(handle, enabled, flags):
    fn = get_func_pointer("nvmlDeviceSetDefaultAutoBoostedClocksEnabled")
    ret = fn(handle, _nvmlEnableState_t(enabled), c_uint(flags))
    check_return(ret)
    return None
    # Throws NVML_ERROR_NOT_SUPPORTED if hardware doesn't support setting auto boosted clocks


# Added in 4.304
def nvmlDeviceSetApplicationsClocks(handle, maxMemClockMHz, maxGraphicsClockMHz):
    fn = get_func_pointer("nvmlDeviceSetApplicationsClocks")
    ret = fn(handle, c_uint(maxMemClockMHz), c_uint(maxGraphicsClockMHz))
    check_return(ret)
    return None


# Added in 4.304
def nvmlDeviceResetApplicationsClocks(handle):
    fn = get_func_pointer("nvmlDeviceResetApplicationsClocks")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceGetClock(handle, clockType, clockId):
    freq = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetClock")
    ret = fn(handle, clockType, clockId, byref(freq))
    check_return(ret)
    return freq.value


def nvmlDeviceGetMaxCustomerBoostClock():
    freq = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetMaxCustomerBoostClock")
    ret = fn(handle, clockType, byref(freq))
    check_return(ret)
    return freq.value


# Added in 4.304
def nvmlDeviceSetPowerManagementLimit(handle, limit):
    fn = get_func_pointer("nvmlDeviceSetPowerManagementLimit")
    ret = fn(handle, c_uint(limit))
    check_return(ret)
    return None


# Added in 4.304
def nvmlDeviceSetGpuOperationMode(handle, mode):
    fn = get_func_pointer("nvmlDeviceSetGpuOperationMode")
    ret = fn(handle, _nvmlGpuOperationMode_t(mode))
    check_return(ret)
    return None


# Added in 2.285
def nvmlEventSetCreate():
    fn = get_func_pointer("nvmlEventSetCreate")
    eventSet = c_nvmlEventSet_t()
    ret = fn(byref(eventSet))
    check_return(ret)
    return eventSet


# Added in 2.285
def nvmlDeviceRegisterEvents(handle, eventTypes, eventSet):
    fn = get_func_pointer("nvmlDeviceRegisterEvents")
    ret = fn(handle, c_ulonglong(eventTypes), eventSet)
    check_return(ret)
    return None


# Added in 2.285
def nvmlDeviceGetSupportedEventTypes(handle):
    c_eventTypes = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetSupportedEventTypes")
    ret = fn(handle, byref(c_eventTypes))
    check_return(ret)
    return c_eventTypes.value


# Added in 2.285
# raises NVML_ERROR_TIMEOUT exception on timeout
def nvmlEventSetWait(eventSet, timeoutms):
    fn = get_func_pointer("nvmlEventSetWait_v2")
    data = c_nvmlEventData_t()
    ret = fn(eventSet, byref(data), c_uint(timeoutms))
    check_return(ret)
    return data


# Added in 2.285
def nvmlEventSetFree(eventSet):
    fn = get_func_pointer("nvmlEventSetFree")
    ret = fn(eventSet)
    check_return(ret)
    return None


def nvmlDeviceModifyDrainState(pciInfo, state):
    fn = get_func_pointer("nvmlDeviceModifyDrainState")
    ret = fn(byref(pciInfo), _nvmlEnableState_t(state))
    check_return(ret)
    return None


def nvmlDeviceQueryDrainState(pciInfo):
    state = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceQueryDrainState")
    ret = fn(byref(pciInfo), byref(state))
    check_return(ret)
    return state.value


def nvmlDeviceRemoveGpu(pciInfo, gpuState, linkState):
    fn = get_func_pointer("nvmlDeviceRemoveGpu_v2")
    ret = fn(byref(pciInfo), _nvmlDetachGpuState_t(gpuState), _nvmlPcieLinkState_t(linkState))
    check_return(ret)
    return None


def nvmlDeviceDiscoverGpus(pciInfo):
    fn = get_func_pointer("nvmlDeviceDiscoverGpus")
    ret = fn(byref(pciInfo))
    check_return(ret)
    return None


def nvmlDeviceGetFieldValues(handle, count):
    values = (c_nvmlFieldValue_t * count)()
    fn = get_func_pointer("nvmlDeviceGetFieldValues")
    ret = fn(handle, c_int(count), values)
    check_return(ret)
    return values


def nvmlDeviceGetVirtualizationMode(handle):
    mode = _nvmlGpuVirtualizationMode()
    fn = get_func_pointer("nvmlDeviceGetVirtualizationMode")
    ret = fn(handle, byref(mode))
    check_return(ret)
    return mode.value


# Added in 3.295
def nvmlDeviceOnSameBoard(handle1, handle2):
    fn = get_func_pointer("nvmlDeviceOnSameBoard")
    onSameBoard = c_int()
    ret = fn(handle1, handle2, byref(onSameBoard))
    check_return(ret)
    return onSameBoard.value != 0


# Added in 3.295
def nvmlDeviceGetCurrPcieLinkGeneration(handle):
    fn = get_func_pointer("nvmlDeviceGetCurrPcieLinkGeneration")
    gen = c_uint()
    ret = fn(handle, byref(gen))
    check_return(ret)
    return gen.value


# Added in 3.295
def nvmlDeviceGetMaxPcieLinkGeneration(handle):
    fn = get_func_pointer("nvmlDeviceGetMaxPcieLinkGeneration")
    gen = c_uint()
    ret = fn(handle, byref(gen))
    check_return(ret)
    return gen.value


# Added in 3.295
def nvmlDeviceGetCurrPcieLinkWidth(handle):
    fn = get_func_pointer("nvmlDeviceGetCurrPcieLinkWidth")
    width = c_uint()
    ret = fn(handle, byref(width))
    check_return(ret)
    return width.value


# Added in 3.295
def nvmlDeviceGetMaxPcieLinkWidth(handle):
    fn = get_func_pointer("nvmlDeviceGetMaxPcieLinkWidth")
    width = c_uint()
    ret = fn(handle, byref(width))
    check_return(ret)
    return width.value


# Added in 4.304
def nvmlDeviceGetSupportedClocksThrottleReasons(handle):
    c_reasons = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetSupportedClocksThrottleReasons")
    ret = fn(handle, byref(c_reasons))
    check_return(ret)
    return c_reasons.value


# Added in 4.304
def nvmlDeviceGetCurrentClocksThrottleReasons(handle):
    c_reasons = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetCurrentClocksThrottleReasons")
    ret = fn(handle, byref(c_reasons))
    check_return(ret)
    return c_reasons.value


# Added in 5.319
def nvmlDeviceGetIndex(handle):
    fn = get_func_pointer("nvmlDeviceGetIndex")
    c_index = c_uint()
    ret = fn(handle, byref(c_index))
    check_return(ret)
    return c_index.value


# Added in 5.319
def nvmlDeviceGetAccountingMode(handle):
    c_mode = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetAccountingMode")
    ret = fn(handle, byref(c_mode))
    check_return(ret)
    return c_mode.value


def nvmlDeviceSetAccountingMode(handle, mode):
    fn = get_func_pointer("nvmlDeviceSetAccountingMode")
    ret = fn(handle, _nvmlEnableState_t(mode))
    check_return(ret)
    return None


def nvmlDeviceClearAccountingPids(handle):
    fn = get_func_pointer("nvmlDeviceClearAccountingPids")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceGetAccountingStats(handle, pid):
    stats = c_nvmlAccountingStats_t()
    fn = get_func_pointer("nvmlDeviceGetAccountingStats")
    ret = fn(handle, c_uint(pid), byref(stats))
    check_return(ret)
    if (stats.maxMemoryUsage == NVML_VALUE_NOT_AVAILABLE_ulonglong.value):
        # special case for WDDM on Windows, see comment above
        stats.maxMemoryUsage = None
    return stats


def nvmlDeviceGetAccountingPids(handle):
    count = c_uint(nvmlDeviceGetAccountingBufferSize(handle))
    pids = (c_uint * count.value)()
    fn = get_func_pointer("nvmlDeviceGetAccountingPids")
    ret = fn(handle, byref(count), pids)
    check_return(ret)
    return map(int, pids[0:count.value])


def nvmlDeviceGetAccountingBufferSize(handle):
    bufferSize = c_uint()
    fn = get_func_pointer("nvmlDeviceGetAccountingBufferSize")
    ret = fn(handle, byref(bufferSize))
    check_return(ret)
    return int(bufferSize.value)


def nvmlDeviceGetRetiredPages(device, sourceFilter):
    c_source = _nvmlPageRetirementCause_t(sourceFilter)
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetRetiredPages")

    # First call will get the size
    ret = fn(device, c_source, byref(c_count), None)

    # this should only fail with insufficient size
    if ((ret != NVML_SUCCESS) and
            (ret != NVML_ERROR_INSUFFICIENT_SIZE)):
        raise NVMLError(ret)

    # call again with a buffer
    # oversize the array for the rare cases where additional pages
    # are retired between NVML calls
    c_count.value = c_count.value * 2 + 5
    page_array = c_ulonglong * c_count.value
    c_pages = page_array()
    ret = fn(device, c_source, byref(c_count), c_pages)
    check_return(ret)
    return map(int, c_pages[0:c_count.value])


def nvmlDeviceGetRetiredPages_v2(device, sourceFilter):
    c_source = _nvmlPageRetirementCause_t(sourceFilter)
    c_count = c_uint(0)
    c_timestamps = c_ulonglong(0)
    fn = get_func_pointer("nvmlDeviceGetRetiredPages_v2")

    # First call will get the size
    ret = fn(device, c_source, byref(c_count), None, byref(c_timestamps))

    # this should only fail with insufficient size
    if ((ret != NVML_SUCCESS) and
            (ret != NVML_ERROR_INSUFFICIENT_SIZE)):
        raise NVMLError(ret)

    # call again with a buffer
    # oversize the array for the rare cases where additional pages
    # are retired between NVML calls
    c_count.value = c_count.value * 2 + 5
    page_array = c_ulonglong * c_count.value
    c_pages = page_array()
    ret = fn(device, c_source, byref(c_count), c_pages, byref(c_timestamps))
    check_return(ret)
    return map(int, c_pages[0:c_count.value], c_timestamps.value)


def nvmlDeviceGetRetiredPagesPendingStatus(device):
    c_pending = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetRetiredPagesPendingStatus")
    ret = fn(device, byref(c_pending))
    check_return(ret)
    return int(c_pending.value)


def nvmlDeviceGetRemappedRows(handle):
    corrRows = c_uint()
    uncRows = c_uint()
    pending = c_uint()
    failure = c_uint()
    fn = get_func_pointer("nvmlDeviceGetRemappedRows")
    ret = fn(handle, byref(corrRows), byref(uncRows), byref(pending), byref(failure))
    check_return(ret)
    return [corrRows.value, uncRows.value, pending.value, failure.value]


def nvmlDeviceGetArchitecture(handle):
    architecture = nvmlDeviceArchitecture_t()
    fn = get_func_pointer("nvmlDeviceGetArchitecture")
    ret = fn(handle, byref(architecture))
    check_return(ret)
    return architecture.value


def nvmlDeviceGetAPIRestriction(device, apiType):
    c_permission = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetAPIRestriction")
    ret = fn(device, _nvmlRestrictedAPI_t(apiType), byref(c_permission))
    check_return(ret)
    return int(c_permission.value)


def nvmlDeviceSetAPIRestriction(handle, apiType, isRestricted):
    fn = get_func_pointer("nvmlDeviceSetAPIRestriction")
    ret = fn(handle, _nvmlRestrictedAPI_t(apiType), _nvmlEnableState_t(isRestricted))
    check_return(ret)
    return None


def nvmlDeviceGetBridgeChipInfo(handle):
    bridgeHierarchy = c_nvmlBridgeChipHierarchy_t()
    fn = get_func_pointer("nvmlDeviceGetBridgeChipInfo")
    ret = fn(handle, byref(bridgeHierarchy))
    check_return(ret)
    return bridgeHierarchy


def nvmlDeviceGetSamples(device, sampling_type, timeStamp):
    c_sampling_type = _nvmlSamplingType_t(sampling_type)
    c_time_stamp = c_ulonglong(timeStamp)
    c_sample_count = c_uint(0)
    c_sample_value_type = _nvmlValueType_t()
    fn = get_func_pointer("nvmlDeviceGetSamples")

    ## First Call gets the size
    ret = fn(device, c_sampling_type, c_time_stamp, byref(c_sample_value_type), byref(c_sample_count), None)

    # Stop if this fails
    if (ret != NVML_SUCCESS):
        raise NVMLError(ret)

    sampleArray = c_sample_count.value * c_nvmlSample_t
    c_samples = sampleArray()
    ret = fn(device, c_sampling_type, c_time_stamp, byref(c_sample_value_type), byref(c_sample_count), c_samples)
    check_return(ret)
    return (c_sample_value_type.value, c_samples[0:c_sample_count.value])


def nvmlDeviceGetViolationStatus(device, perfPolicyType):
    c_perfPolicy_type = _nvmlPerfPolicyType_t(perfPolicyType)
    c_violTime = c_nvmlViolationTime_t()
    fn = get_func_pointer("nvmlDeviceGetViolationStatus")

    ## Invoke the method to get violation time
    ret = fn(device, c_perfPolicy_type, byref(c_violTime))
    check_return(ret)
    return c_violTime


def nvmlDeviceGetPcieThroughput(device, counter):
    c_util = c_uint()
    fn = get_func_pointer("nvmlDeviceGetPcieThroughput")
    ret = fn(device, _nvmlPcieUtilCounter_t(counter), byref(c_util))
    check_return(ret)
    return c_util.value


def nvmlSystemGetTopologyGpuSet(cpuNumber):
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlSystemGetTopologyGpuSet")

    # First call will get the size
    ret = fn(cpuNumber, byref(c_count), None)

    if ret != NVML_SUCCESS:
        raise NVMLError(ret)
    print(c_count.value)
    # call again with a buffer
    device_array = c_nvmlDevice_t * c_count.value
    c_devices = device_array()
    ret = fn(cpuNumber, byref(c_count), c_devices)
    check_return(ret)
    return map(None, c_devices[0:c_count.value])


def nvmlDeviceGetTopologyNearestGpus(device, level):
    c_count = c_uint(0)
    fn = get_func_pointer("nvmlDeviceGetTopologyNearestGpus")

    # First call will get the size
    ret = fn(device, level, byref(c_count), None)

    if ret != NVML_SUCCESS:
        raise NVMLError(ret)

    # call again with a buffer
    device_array = c_nvmlDevice_t * c_count.value
    c_devices = device_array()
    ret = fn(device, level, byref(c_count), c_devices)
    check_return(ret)
    return map(None, c_devices[0:c_count.value])


def nvmlDeviceGetTopologyCommonAncestor(device1, device2):
    c_level = _nvmlGpuTopologyLevel_t()
    fn = get_func_pointer("nvmlDeviceGetTopologyCommonAncestor")
    ret = fn(device1, device2, byref(c_level))
    check_return(ret)
    return c_level.value


def nvmlDeviceFreezeNvLinkUtilizationCounter(device, link, counter, freeze):
    """Freeze the NVLINK utilization counters.

    Freeze the NVLINK utilization counters. Both the receive and transmit
    counters are operated on by this function.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        freeze: NVML_FEATURE_ENABLED(1) = freeze the rx and tx counters
                NVML_FEATURE_DISABLED(0) = unfreeze the rx and tx counters

    """
    c_link = c_uint(link)
    c_counter = c_uint(counter)
    fn = get_func_pointer("nvmlDeviceFreezeNvLinkUtilizationCounter")
    ret = fn(device, c_link, c_counter, _nvmlEnableState_t(freeze))
    return check_return(ret)


def nvmlDeviceGetNvLinkCapability(device, link, cap):
    """Retrieve the capability of a specified NvLinklink.

    Retrieves the requested capability from the device's NvLink for the link
    specified. Please refer to the nvmlNvLinkCapability_t structure for the
    specific caps that can be queried. The return value should be treated as a
    boolean.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        capability: Specifies the nvmlNvLinkCapability_t to be queried

    Returns:
        cap_result: A boolean for the queried capability indicating that feature
        is available

    """
    c_link = c_uint(link)
    c_cap_result = c_bool()
    fn = get_func_pointer("nvmlDeviceGetNvLinkCapability")
    ret = fn(device, c_link, _nvmlNvLinkCapability_t(cap), byref(c_cap_result))
    check_return(ret)
    return c_cap_result.value


def nvmlDeviceGetNvLinkErrorCounter(device, link, counter):
    """Retrieve the specified error counter value.

    Retrieves the specified error counter value. Please refer to
    _nvmlNvLinkErrorCounter_t for error counters that are available.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        counter: Specifies the NvLink counter to be queried

    Returns:
        value: The specified counter value

    """
    c_link = c_uint(link)
    c_cap_result = c_bool()
    c_value = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetNvLinkErrorCounter")
    ret = fn(device, c_link, _nvmlNvLinkErrorCounter_t(counter), byref(c_value))
    check_return(ret)
    return c_value.value


def nvmlDeviceGetNvLinkRemotePciInfo(device, link):
    """Retrieve the PCI information for the remote node on a NvLink link.

    Retrieves the PCI information for the remote node on a NvLink link. Note:
    pciSubSystemId is not filled in this function and is indeterminate.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

    Returns:
        pci: nvmlPciInfo_t of the remote node for the specified link

    """
    c_link = c_uint(link)
    c_pci = c_nvmlPciInfo_t()
    fn = get_func_pointer("nvmlDeviceGetNvLinkRemotePciInfo_v2")
    ret = fn(device, c_link, byref(c_pci))
    check_return(ret)
    return c_pci


def nvmlDeviceGetNvLinkState(device, link):
    """Retrieve the state of the device's NvLink for the link specified.

    Retrieves the state of the device's NvLink for the link specified.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

    Returns:
        mode: nvmlEnableState_t where NVML_FEATURE_ENABLED indicates that the
        link is active and NVML_FEATURE_DISABLED indicates it is inactive.

    """
    c_link = c_uint(link)
    c_mode = _nvmlEnableState_t()
    fn = get_func_pointer("nvmlDeviceGetNvLinkState")
    ret = fn(device, c_link, byref(c_mode))
    check_return(ret)
    return c_mode.value


def nvmlDeviceGetNvLinkUtilizationControl(device, link, counter):
    """Get NVLINK utilization counter control information

    Get the NVLINK utilization counter control information for the specified
    counter, 0 or 1. Please refer to nvmlNvLinkUtilizationControl_t for the
    structure definition. [Note: nvmlNvLinkUtilizationControl_t not documented]

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        counter: Specifies the counter that should be set (0 or 1)

    Returns:
        control: The nvmlNvLinkUtilizationControl_t object (an integer)

    """
    c_link = c_uint(link)
    c_counter = c_uint(counter)
    c_control = _nvmlNvLinkUtilizationControl_t()
    fn = get_func_pointer("nvmlDeviceGetNvLinkUtilizationControl")
    ret = fn(device, c_link, c_counter, byref(c_control))
    check_return(ret)
    return c_control.value


def nvmlDeviceGetNvLinkUtilizationCounter(device, link, counter):
    """Retrieve an NVLINK utilization counter.

    Retrieve the NVLINK utilization counter based on the current control for a
    specified counter. In general it is good practice to use
    nvmlDeviceSetNvLinkUtilizationControl before reading the utilization
    counters as they have no default state.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        counter: Specifies the counter that should be set (0 or 1)

    Returns:
        rxtx_dict: Dictionary with `rx` key (value is "receive" counter) and
        `tx` key (value is "transmit" counter)

    """
    c_link = c_uint(link)
    c_counter = c_uint(counter)
    c_rx = c_ulonglong()
    c_tx = c_ulonglong()
    fn = get_func_pointer("nvmlDeviceGetNvLinkUtilizationCounter")
    ret = fn(device, c_link, c_counter, byref(c_rx), byref(c_tx))
    check_return(ret)
    rxtx_dict = {'rx': c_rx.value, 'tx': c_tx.value}
    return rxtx_dict


def nvmlDeviceGetNvLinkVersion(device, link):
    """Retrieve NvLink version.

    Retrieves the version of the device's NvLink for the link specified.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

    Returns:
        version: Requested NvLink version (uint)

    """
    c_link = c_uint(link)
    c_version = c_uint()
    fn = get_func_pointer("nvmlDeviceGetNvLinkVersion")
    ret = fn(device, c_link, byref(c_version))
    check_return(ret)
    return c_version.value


def nvmlDeviceResetNvLinkErrorCounters(device, link):
    """Reset all error counters to zero.

    Resets all error counters to zero. Please refer to nvmlNvLinkErrorCounter_t
    for the list of error counters that are reset.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

    """
    c_link = c_uint(link)
    fn = get_func_pointer("nvmlDeviceResetNvLinkErrorCounters")
    ret = fn(device, c_link)
    return check_return(ret)


def nvmlDeviceResetNvLinkUtilizationCounter(device, link, counter):
    """Reset the NVLINK utilization counters.

    Reset the NVLINK utilization counters. Both the receive and transmit
    counters are operated on by this function.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        counter: Specifies the counter that should be reset (0 or 1)

    """
    c_link = c_uint(link)
    c_counter = c_uint(counter)
    fn = get_func_pointer("nvmlDeviceResetNvLinkUtilizationCounter")
    ret = fn(device, c_link, c_counter)
    return check_return(ret)


def nvmlDeviceSetNvLinkUtilizationControl(device, link, counter, control, reset):
    """Set the NVLINK utilization counter control.

    Set the NVLINK utilization counter control information for the specified
    counter, 0 or 1. Please refer to nvmlNvLinkUtilizationControl_t for the
    structure definition. Performs a reset of the counters if the reset
    parameter is non-zero. Note: nvmlNvLinkUtilizationControl_t is an integer.

    Args:
        device: The identifier of the target device

        link: Specifies the NvLink link to be queried (uint)

        counter: Specifies the counter that should be set (0 or 1)

        reset: Resets the counters on set if non-zero (uint)

        control: The nvmlNvLinkUtilizationControl_t control setting
                 Note: 0 == cycles, 1 == packets, 2 == bytes

    """
    c_link = c_uint(link)
    c_counter = c_uint(counter)
    c_control = _nvmlNvLinkUtilizationControl_t(control)
    c_reset = c_uint(reset)
    fn = get_func_pointer("nvmlDeviceSetNvLinkUtilizationControl")
    ret = fn(device, c_link, c_counter, byref(c_control), c_reset)
    return check_return(ret)


## MIG Functions ##

def nvmlDeviceSetMigMode(handle, mode):
    status = _nvmlReturn_t()
    fn = get_func_pointer("nvmlDeviceSetMigMode")
    ret = fn(handle, c_uint(mode), byref(status))
    check_return(ret)
    return status.value


def nvmlDeviceGetMigMode(handle):
    currentMode = c_uint()
    pendingMode = c_uint()
    fn = get_func_pointer("nvmlDeviceGetMigMode")
    ret = fn(handle, byref(currentMode), byref(pendingMode))
    check_return(ret)
    return [currentMode, pendingMode]


def nvmlDeviceGetGpuInstanceProfileInfo(handle, profile):
    info = nvmlGpuInstanceProfileInfo_t()
    fn = get_func_pointer("nvmlDeviceGetGpuInstanceProfileInfo")
    ret = fn(handle, c_uint(profile), byref(info))
    check_return(ret)
    return info


def nvmlDeviceGetGpuInstancePossiblePlacements(handle, profileId):
    count = 0  # TODO: get count
    fn = get_func_pointer("nvmlDeviceGetGpuInstancePossiblePlacements")


def nvmlDeviceGetGpuInstanceRemainingCapacity(handle, profileId):
    count = c_uint()
    fn = get_func_pointer("nvmlDeviceGetGpuInstanceRemainingCapacity")
    ret = fn(handle, profileId, byref(count))
    check_return(ret)
    return count


def nvmlDeviceCreateGpuInstance(handle, profileId):
    instance = c_nvmlGpuInstance_t()
    fn = get_func_pointer("nvmlDeviceCreateGpuInstance")
    ret = fn(handle, profileId, byref(instance))
    check_return(ret)
    return instance


def nvmlGpuInstanceDestroy(handle):
    fn = get_func_pointer("nvmlGpuInstanceDestroy")
    ret = fn(handle)
    check_return(ret)
    return None


def nvmlDeviceGetGpuInstances(handle, profileId):
    count = 0  # TODO: get count
    fn = get_func_pointer("nvmlDeviceGetGpuInstances")


def nvmlDeviceGetGpuInstanceById(handle, id):
    instance = c_nvmlGpuInstance_t()
    fn = get_func_pointer("nvmlDeviceGetGpuInstanceById")
    ret = fn(handle, id, byref(instance))
    check_return(ret)
    return instance


def nvmlGpuInstanceGetInfo(instance):
    info = c_nvmlGpuInstanceInfo_t()
    fn = get_func_pointer("nvmlGpuInstanceGetInfo")
    ret = fn(instance, byref(info))
    check_return(ret)
    return info


def nvmlGpuInstanceGetComputeInstanceProfileInfo(instance, profile, engProfile):
    info = nvmlComputeInstanceProfileInfo_t()
    fn = get_func_pointer("nvmlGpuInstanceGetComputeInstanceProfileInfo")
    ret = fn(instance, c_uint(profile), c_uint(engProfile), byref(info))
    check_return(ret)
    return info


def nvmlGpuInstanceGetComputeInstanceRemainingCapacity(instance, profileId):
    count = c_uint()
    fn = get_func_pointer("nvmlGpuInstanceGetComputeInstanceRemainingCapacity")
    ret = fn(instance, profileId, byref(count))
    check_return(ret)
    return count.value


def nvmlGpuInstanceCreateComputeInstance(instance, profileId):
    computeInstance = c_nvmlComputeInstance_t()
    fn = get_func_pointer("nvmlGpuInstanceCreateComputeInstance")
    ret = fn(instance, profileId, byref(computeInstance))
    check_return(ret)
    return computeInstance


def nvmlComputeInstanceDestroy(instance):
    fn = get_func_pointer("nvmlComputeInstanceDestroy")
    ret = fn(instance)
    check_return(ret)
    return None


def nvmlGpuInstanceGetComputeInstances(gpuInstance, profileId):
    count = c_uint()
    computeInstances = c_nvmlComputeInstance_t()
    fn = get_func_pointer("nvmlGpuInstanceGetComputeInstances")
    ret = fn(gpuInstance, profileId, byref(computeInstances), byref(count))

    computeInstances = (c_nvmlComputeInstance_t * count)()
    ret = fn(gpuInstance, profileId, byref(computeInstances), byref(count))
    check_return(ret)
    return [computeInstances, count]


def nvmlGpuInstanceGetComputeInstanceById(gpuInstance, id):
    computeInstance = c_nvmlComputeInstance_t()
    fn = get_func_pointer("nvmlGpuInstanceGetComputeInstanceById")
    ret = fn(gpuInstance, id, byref(computeInstance))
    check_return(ret)
    return computeInstance


def nvmlComputeInstanceGetInfo(computeInstance):
    info = c_nvmlComputeInstanceProfileInfo_t()
    fn = get_func_pointer("nvmlComputeInstanceGetInfo")
    ret = fn(computeInstance, byref(info))
    check_return(ret)
    return info


def nvmlDeviceIsMigDeviceHandle(handle):
    isMig = c_uint()
    fn = get_func_pointer("nvmlDeviceIsMigDeviceHandle")
    ret = fn(handle, byref(isMig))
    check_return(ret)
    return False if isMig.value == 0 else True


def nvmlDeviceGetGpuInstanceId(device):
    id = c_uint()
    fn = get_func_pointer("nvmlDeviceGetGpuInstanceId")
    ret = fn(device, byref(id))
    check_return(ret)
    return id.value


def nvmlDeviceGetComputeInstanceId(device):
    id = c_uint()
    fn = get_func_pointer("nvmlDeviceGetComputeInstanceId")
    ret = fn(device, byref(id))
    check_return(ret)
    return id.value


def nvmlDeviceGetMaxMigDeviceCount(device):
    count = c_uint()
    fn = get_func_pointer("nvmlDeviceGetMaxMigDeviceCount")
    ret = fn(device, byref(count))
    check_return(ret)
    return count.value