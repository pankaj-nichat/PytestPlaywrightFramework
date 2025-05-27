# PlayWrightWithPython

A Python automation framework using Playwright and Robot Framework, supporting both UI and API testing with a Page Object Model structure.

## Structure
- Controller/: Reusable methods and functions
- Pages/: Page Object Model locators
- Test/: Robot Framework test cases
- TestData/: Test data files
- config/: Global config and constants

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Install Playwright browsers: `python -m playwright install`
3. Run tests: `robot Test/test_login.robot`
