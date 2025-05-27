from controller.base import BaseClass

class AwareFunctions(BaseClass):

    def __init__(self):
        super().__init__()
        self.login_url = "https://rtqawww.securly.com/app/aware/"

    def login_to_child(self,handle):
        page3 = self.pages[handle]
        page3.goto("https://www.saucedemo.com/v1/")
        page3.get_by_text("Accepted usernames are: standard_user locked_out_user problem_user").click()

