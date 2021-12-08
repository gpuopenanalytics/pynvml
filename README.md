Python bindings to the NVIDIA Management Library
================================================

Provides a Python interface to GPU management and monitoring functions.

This is a wrapper around the NVML library.
For information about the NVML library, see the NVML developer page
http://developer.nvidia.com/nvidia-management-library-nvml

As of version 11.0.0, the NVML-wrappers used in pynvml are identical
to those published through [nvidia-ml-py](https://pypi.org/project/nvidia-ml-py/).

Note that this file can be run with 'python -m doctest -v README.txt'
although the results are system dependent

Requires
--------
Python 3, or an earlier version with the ctypes module.

Installation
------------

    pip install .

Usage
-----

You can use the lower level nvml bindings

```python
>>> from pynvml import *
>>> nvmlInit()
>>> print("Driver Version:", nvmlSystemGetDriverVersion())
Driver Version: 410.00
>>> deviceCount = nvmlDeviceGetCount()
>>> for i in range(deviceCount):
...     handle = nvmlDeviceGetHandleByIndex(i)
...     print("Device", i, ":", nvmlDeviceGetName(handle))
...
Device 0 : Tesla V100

>>> nvmlShutdown()
```

Or the higher level nvidia_smi API

```python
from pynvml.smi import nvidia_smi
nvsmi = nvidia_smi.getInstance()
nvsmi.DeviceQuery('memory.free, memory.total')
```

```python
from pynvml.smi import nvidia_smi
nvsmi = nvidia_smi.getInstance()
print(nvsmi.DeviceQuery('--help-query-gpu'), end='\n')
```

Functions
---------
Python methods wrap NVML functions, implemented in a C shared library.
Each function's use is the same with the following exceptions:

- Instead of returning error codes, failing error codes are raised as
  Python exceptions.

    ```python
    >>> try:
    ...     nvmlDeviceGetCount()
    ... except NVMLError as error:
    ...     print(error)
    ...
    Uninitialized
    ```

- C function output parameters are returned from the corresponding
  Python function left to right.

    ```c
    nvmlReturn_t nvmlDeviceGetEccMode(nvmlDevice_t device,
                                      nvmlEnableState_t *current,
                                      nvmlEnableState_t *pending);
    ```

    ```python
    >>> nvmlInit()
    >>> handle = nvmlDeviceGetHandleByIndex(0)
    >>> (current, pending) = nvmlDeviceGetEccMode(handle)
    ```

- C structs are converted into Python classes.

    ```c
    nvmlReturn_t DECLDIR nvmlDeviceGetMemoryInfo(nvmlDevice_t device,
                                                 nvmlMemory_t *memory);
    typedef struct nvmlMemory_st {
        unsigned long long total;
        unsigned long long free;
        unsigned long long used;
    } nvmlMemory_t;
    ```

    ```python
    >>> info = nvmlDeviceGetMemoryInfo(handle)
    >>> print "Total memory:", info.total
    Total memory: 5636292608
    >>> print "Free memory:", info.free
    Free memory: 5578420224
    >>> print "Used memory:", info.used
    Used memory: 57872384
    ```

- Python handles string buffer creation.

    ```c
    nvmlReturn_t nvmlSystemGetDriverVersion(char* version,
                                            unsigned int length);
    ```

    ```python
    >>> version = nvmlSystemGetDriverVersion();
    >>> nvmlShutdown()
    ```

For usage information see the NVML documentation.

Variables
---------

All meaningful NVML constants and enums are exposed in Python.

The NVML_VALUE_NOT_AVAILABLE constant is not used.  Instead None is mapped to the field.

NVML Permissions
----------------

Many of the `pynvml` wrappers assume that the underlying NVIDIA Management Library (NVML) API can be used without admin/root privileges.  However, it is certainly possible for the system permissions to prevent pynvml from querying GPU performance counters. For example:

```
$ nvidia-smi nvlink -g 0
GPU 0: Tesla V100-SXM2-32GB (UUID: GPU-96ab329d-7a1f-73a8-a9b7-18b4b2855f92)
NVML: Unable to get the NvLink link utilization counter control for link 0: Insufficient Permissions
```

A simple way to check the permissions status is to look for `RmProfilingAdminOnly` in the driver `params` file (Note that `RmProfilingAdminOnly == 1` means that admin/sudo access is required):

```
$ cat /proc/driver/nvidia/params | grep RmProfilingAdminOnly
RmProfilingAdminOnly: 1
```

For more information on setting/unsetting the relevant admin privileges, see [these notes](https://developer.nvidia.com/nvidia-development-tools-solutions-ERR_NVGPUCTRPERM-permission-issue-performance-counters) on resolving `ERR_NVGPUCTRPERM` errors.


Release Notes
-------------

-   Version 2.285.0
    - Added new functions for NVML 2.285.  See NVML documentation for more information.
    - Ported to support Python 3.0 and Python 2.0 syntax.
    - Added nvidia_smi.py tool as a sample app.
-   Version 3.295.0
    - Added new functions for NVML 3.295.  See NVML documentation for more information.
    - Updated nvidia_smi.py tool
      - Includes additional error handling
-   Version 4.304.0
    - Added new functions for NVML 4.304.  See NVML documentation for more information.
    - Updated nvidia_smi.py tool
-   Version 4.304.3
    - Fixing nvmlUnitGetDeviceCount bug
-   Version 5.319.0
    - Added new functions for NVML 5.319.  See NVML documentation for more information.
-   Version 6.340.0
    - Added new functions for NVML 6.340.  See NVML documentation for more information.
-   Version 7.346.0
    - Added new functions for NVML 7.346.  See NVML documentation for more information.
-   Version 7.352.0
    - Added new functions for NVML 7.352.  See NVML documentation for more information.
-   Version 8.0.0
    - Refactor code to a nvidia_smi singleton class
    - Added DeviceQuery that returns a dictionary of (name, value).
    - Added filter parameters on DeviceQuery to match query api in nvidia-smi
    - Added filter parameters on XmlDeviceQuery to match query api in nvidia-smi
    - Added integer enumeration for filter strings to reduce overhead for performance monitoring.
    - Added loop(filter) method with async and callback support
-   Version 8.0.1
    - Restructuring directories into two packages (pynvml and nvidia_smi)
    - Adding initial tests for both packages
    - Some name-convention cleanup in pynvml
-   Version 8.0.2
    - Added NVLink function wrappers for pynvml module
-   Version 8.0.3
    - Added versioneer
    - Fixed nvmlDeviceGetNvLinkUtilizationCounter bug
-   Version 8.0.4
    - Added nvmlDeviceGetTotalEnergyConsumption
    - Added notes about NVML permissions
    - Fixed version-check testing
-   Version 11.0.0
    - Updated nvml.py to CUDA 11
    - Updated smi.py DeviceQuery to R460
    - Aligned nvml.py with latest nvidia-ml-py deployment
-   Version 11.4.0
    - Updated nvml.py to CUDA 11.4
    - Updated smi.py NVML_BRAND_NAMES
    - Aligned nvml.py with latest nvidia-ml-py deployment (11.495.46)
