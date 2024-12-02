> [!WARNING]
> 
> **The `pynvml` module is NOT developed or maintained in this project!**
> 
> This project provides unofficial NVML Python utilities (i.e. the `pynvml_utils` module).
> The `pynvml_utils` module is intended for demonstration purposes only.
> There is no guarantee for long-term maintenence or support.
>
> The `pynvml_utils` module depends on the official NVML bindings
> published by NVIDIA under a different `nvidia-ml-py` project
> (see: https://pypi.org/project/nvidia-ml-py/).
>


Python utilities for the NVIDIA Management Library
===============================================================

This project provides unofficial Python utilities for the
NVIDIA Management Library (NVML).

For information about the NVML library, see the NVML developer page
http://developer.nvidia.com/nvidia-management-library-nvml


Requires
--------
`nvidia-ml-py`.


Installation
------------

    pip install .

Usage
-----

Bindings for the high-level `nvidia-smi` API are available
in `pynvml_utils.nvidia_smi`:

> [!WARNING]
> The `nvidia_smi` module is intended for demonstration purposes only.
> There is no guarantee for long-term maintenence or support.

```python
from pynvml_utils import nvidia_smi
nvsmi = nvidia_smi.getInstance()
nvsmi.DeviceQuery('memory.free, memory.total')
```

```python
from pynvml_utils import nvidia_smi
nvsmi = nvidia_smi.getInstance()
print(nvsmi.DeviceQuery('--help-query-gpu'), end='\n')
```

Release Notes
-------------

-   Version 12.0.0
    - Remove pynvml module and depend on nvidia-ml-py instead
    - Pin to nvidia-ml-py>=12.0.0,<13.0.0a0


Old Releases
------------

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
-   Version 11.4.1
    - Fix comma bugs in nvml.py
-   Version 11.5.0
    - Updated nvml.py to support CUDA 11.5 and CUDA 12
    - Aligned with latest nvidia-ml-py deployment (11.525.84)
-   Version 11.5.2
    - Relocated smi bindings to new pynvml_utils module
    - Updated README to encourage migration to nvidia-ml-py
-   Version 11.5.3
    - Update versioneer
