import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--calls",
        action="store",
        default=1,
        type=int,
        help="Number of API calls to make",
    )
    parser.addoption(
        "--delay",
        action="store",
        default=0,
        type=float,
        help="Delay between API calls in seconds",
    )


@pytest.fixture
def calls(request):
    return request.config.getoption("--calls")


@pytest.fixture
def delay(request):
    return request.config.getoption("--delay")
