from anvil import *
import anvil.server
from ._anvil_designer.LoginFormTemplate import LoginFormTemplate

class LoginForm(LoginFormTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        # developer info
        try:
            self.label_dev.text = """Developer: Rizbi Islam\nRole: QA Engineer & Data Processing Enthusiast\nLocation: Bangladesh"""
        except Exception:
            pass

    def btn_login_click(self, **event_args):
        username = self.txt_username.text.strip()
        key = self.txt_key.text.strip()
        if not username or not key:
            alert('Enter username and production key.')
            return
        ok = anvil.server.call('login_user', username, key)
        if ok:
            open_form('MainForm')
            alert(f'Welcome, {username}!')
        else:
            alert('Invalid credentials or/or key expired.')
