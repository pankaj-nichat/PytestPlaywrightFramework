
from dotenv import load_dotenv
import os

from controller.base import BaseClass

load_dotenv()

class OnCallFunctions(BaseClass):

    def __init__(self):
        super().__init__()
        self.login_url = "https://rtqawww.securly.com/24/login"
        self.enable_automation_url = os.getenv("ENABLE_AUTOMATION_URL")

    def login_to_On_call(self, page, email):
        # Only perform login steps
        self.enable_automation(page)
        self.login_to_url_on_page(page, self.login_url, email)
        # try:
        #     page.wait_for_selector('[data-testid="dashboard_queue_auditor_record-25973__button"]', timeout=5000)
        # except Exception:
        #     raise AssertionError("Dashboard did not load or expected element not found after login.")
        print(page)
        # return page

    # --- LoginPage functionality ---
    def login_to_url_on_page(self, page, login_url, email, google_signin_text='Google "G" Logo Sign in with', submit_text='Submit'):
        page.goto(login_url)
        page.get_by_role("link", name=google_signin_text).click()
        page.get_by_role("textbox").fill(email)
        page.get_by_role("button", name=submit_text).click()

    # def select_(self, page):
    #     page.get_by_test_id("dashboard_queue_auditor_record-25973__button").get_by_text("

    def select_dashboard_record(self, page):
        page.get_by_test_id("dashboard_queue_auditor_record-25973__button").get_by_text("rtqa1securly.com").click()

    def send_email(self, page):
        page.get_by_test_id("dashboard_case-overview__send-email-button").click()

    def open_email_history(self, page):
        page.get_by_test_id("email_incident-type__open-history-link").click()

    def add_activity_1(self, page):
        page.get_by_test_id("history_flagged-tab_activity-1__add-activity-button").click()

    def add_activity_12(self, page):
        page.get_by_test_id("history_flagged-tab_activity-12__add-activity-button").click()

    def close(self, page):
        page.get_by_role("button", name="Close").click()

    
