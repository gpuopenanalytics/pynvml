import warnings
from nvml_utils.smi import *

# Warn the user that this is the wrong module path
warnings.warn(
    "The pynvml.smi module is deprecated and will be removed "
    "in the next release of pynvml. Please use nvml_utils:",
    "\n(e.g. `from nvml_utils import nvidia_smi`)",
    FutureWarning,
)
