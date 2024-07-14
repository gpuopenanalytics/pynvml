from .smi import nvidia_smi

from pynvml._version import get_versions
__version__ = get_versions()['version']
del get_versions
