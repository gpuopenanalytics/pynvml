import warnings
from pynvml_utils.smi import *

# Warn the user that this is the wrong module path
warnings.warn(
    "The pynvml.smi module is deprecated and will be removed "
    "in the next release of pynvml. Please use pynvml_utils:"
    "\n(e.g. `from pynvml_utils import nvidia_smi`)",
    FutureWarning,
)
