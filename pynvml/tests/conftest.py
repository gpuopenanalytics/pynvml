import pytest
import pynvml


XFAIL_UNSUPPORTED_HW = "Not supported on this hardware."

@pytest.hookimpl(hookwrapper=True)
def pytest_pyfunc_call(pyfuncitem):
    try:
        outcome = yield
        outcome.get_result()
    except pynvml.NVMLError_NotSupported:
        pytest.xfail(XFAIL_UNSUPPORTED_HW)
