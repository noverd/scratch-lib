import json
import re
from typing import Tuple, Any

import requests
from exceptions import LoginError, ChangePassError


class Session:
    def __init__(self, username: str, password: str, lang: str = "en"):
        _headers = {
            "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.142 Safari/537.36',
            "x-requested-with": "XMLHttpRequest",
            "Cookie": f"scratchlanguage={lang};permissions=%7B%7D;",
            "referer": "https://scratch.mit.edu",
        }
        self.session = requests.Session()
        self.session.headers = _headers
        self.lang: str = lang
        self.username = username
        self.password = password
        self.login()

    def change_password(self, new_pass: str) -> None:
        payload = json.dumps({"csrfmiddlewaretoken": self.session.headers["X-CSRFToken"], "old_password": self.password,
                              "new_password1": new_pass, "new_password2": new_pass})
        req = self.session.post("https://scratch.mit.edu/accounts/password_change/", data=payload)
        if req.status_code != 302:
            raise ChangePassError("Password has already been changed or you are banned from scratch")
        self.password = new_pass
        self.login()

    def change_country(self, country: str) -> None:
        country = country.replace(" ", "+")
        payload = json.dumps({"csrfmiddlewaretoken": self.session.headers["X-CSRFToken"], "country": country})
        self.session.post("https://scratch.mit.edu/accounts/settings/", data=payload)
    def login(self):
        csrf = self.get_csrf()
        self.session.headers["X-CSRFToken"] = csrf
        self.session.headers[
            "Cookie"] = f"scratchcsrftoken={csrf};scratchlanguage={self.lang};"
        credit = self.get_credits()
        self.session.headers["X-Token"] = credit[1]
        self.session.headers[
            "Cookie"] = f"scratchcsrftoken={csrf};scratchlanguage={self.lang};scratchsessionsid={credit[0]};"

    def get_csrf(self):
        req = self.session.get("https://scratch.mit.edu/csrf_token/")
        try:
            csrf = re.search("scratchcsrftoken=(.*?);", req.headers["Set-Cookie"])[1]
        except Exception:
            LoginError("Can't get CSRF token")
        else:
            return csrf

    def get_credits(self) -> Tuple[str, str]:
        payload = json.dumps({"csrfmiddlewaretoken": self.session.headers["X-CSRFToken"], "username": self.username,
                              "password": self.password})
        request = self.session.post("https://scratch.mit.edu/login/", data=payload)
        try:
            session_id = str(re.search('"(.*)"', request.headers["Set-Cookie"]).group())
            token = request.json()[0]["token"]
        except Exception:
            raise LoginError("Login credits are wrong or you banned on scratch")
        return session_id, token
