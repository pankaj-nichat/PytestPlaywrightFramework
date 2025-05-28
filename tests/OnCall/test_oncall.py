import logging
import time

import pytest
import allure
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controller.OnCallFunctions import OnCallFunctions
logger = logging.getLogger(__name__)


class TestOnCallTestKeywords:

    OnCallFunctions = OnCallFunctions()

    @pytest.fixture()
    def browser_setup(self):
        # self.browser_on_call=self.OnCallFunctions.create_browser()
        # self.browser_on_aware = self.OnCallFunctions.create_browser()
        # self.student_browser = self.OnCallFunctions.create_browser()
        return self.OnCallFunctions
        # logger.info(page)
        # return page
        # self.page = self.pages[self.browser]
        # return "Hi"

    @allure.feature("OnCall")
    @allure.story("Smoke")
    @allure.tag("smoke", "critical")
    # @keyword("Dashboard Action")
    def test_on_smoke(self, browser_setup):
        # page= browser_setup.pages[self.browser_on_call]
        # page.goto("https://www.yatra.com/")
        # page.get_by_role("tab", name="Hotels, 2 of").click()
        # page.close()
        print("Smoke")

    @allure.feature("OnCall")
    @allure.story("Smoke")
    @allure.tag("First", "critical")
    # @keyword("Dashboard Action")
    def test_on_first(self, browser_setup):
        # context= browser_setup.contexts[self.browser_on_call]
        # page= context.new_page()
        # time.sleep(10)
        # page.goto("https://www.paytm.com/")
        # logger.info("First")
        # page.close()
        logger.info("First Test")

    @allure.feature("OnCall")
    @allure.story("Second")
    @allure.tag("Second", "critical")
    # @keyword("Dashboard Action")
    def test_on_second(self):
        logger.info("First")

    @allure.feature("OnCall")
    @allure.story("Second")
    @allure.tag("Second", "critical")
    # @keyword("Dashboard Action")
    def test_on_third(self):
        logger.info("First")


        # on_call= browser_setup[self.browser_on_call]
        # email="autoqa@securly.com"
        # # self.page=
        # self.OnCallFunctions.login_to_On_call(on_call, email)
        # on_call.get_by_test_id("header__search-input").click()
        # on_call.get_by_test_id("header__search-input").fill("a")
        # on_call.get_by_test_id("header__search-button").click()


    @allure.feature("aware")
    @pytest.mark.smoke
    # @keyword("Dashboard Action")
    def test_on_aware(self):
        logger.info("New")# on_call = browser_setup[self.browser_on_call]
        # email = "autoqa@securly.com"
        # # self.page=
        # self.OnCallFunctions.login_to_On_call(on_call, email)
        # on_call.get_by_test_id("header__search-input").click()
        # on_call.get_by_test_id("header__search-input").fill("a")
        # on_call.get_by_test_id("header__search-button").click()

    @allure.feature("aware")
    # @keyword("Dashboard Action")
    def test_on_new(self):
        logger.info("New Test")
        # on_call = browser_setup[self.browser_on_call]
        # email = "autoqa@securly.com"
        # # self.page=
        # self.OnCallFunctions.login_to_On_call(on_call, email)
        # on_call.get_by_test_id("header__search-input").click()
        # on_call.get_by_test_id("header__search-input").fill("a")
        # on_call.get_by_test_id("header__search-button").click()



        # self.OnCallFunctions.select_(on_call)

    # def test_do_some_actions(self):

        # self.select_dashboard_record(page)
        # self.send_email(page)
        # self.open_email_history(page)
        # self.add_activity_1(page)
        # self.add_activity_12(page)
        # self.close(page)

