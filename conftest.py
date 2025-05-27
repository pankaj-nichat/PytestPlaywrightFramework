import pytest
import logging
import allure

# Configure global logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Capture all logs

# def pytest_addoption(parser):
#     # parser.addoption("--browser", action="store", default="chromium")
#     # parser.addoption("--headed", action="store_true")


@pytest.fixture(autouse=True)
def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    # Add Allure logging handler
    class AllureLogger(logging.Handler):
        def emit(self, record):
            with allure.step(f'LOG ({record.levelname}): {record.getMessage()}'):
                pass

    if not any(isinstance(handler, AllureLogger) for handler in logger.handlers):
        logger.addHandler(AllureLogger())
