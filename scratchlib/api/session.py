import json
import re
import requests
from exceptions import LoginError, ChangePassError


class Session:
    def __init__(self, username: str, password: str, lang: str = "en"):
        self.username: str = username
        self.password: str = password
        self.headers: dict = {}
        self.cookies: str = ""
        self.lang: str = lang
        self.session_id: str = self.get_sessionid(self.username, self.password)
        self.csrf_token: str = self.get_csrf()
        self.update_headers()

    def relogin(self):
        self.session_id: str = self.get_sessionid(self.username, self.password)
        self.csrf_token: str = self.get_csrf()
        self.update_headers()

    def change_password(self, new_pass: str) -> None:
        payload = json.dumps({"csrfmiddlewaretoken": self.csrf_token, "old_password": self.password,
                              "new_password1": new_pass, "new_password2": new_pass})
        req = requests.post("https://scratch.mit.edu/accounts/password_change/", headers=self.headers, data=payload)
        if req.status_code != 302:
            raise ChangePassError("Password has already been changed or you are banned from scratch")
        self.password = new_pass
        self.relogin()

    def change_country(self, country: str) -> None:
        country = country.replace(" ", "+")
        payload = json.dumps({"csrfmiddlewaretoken": self.csrf_token, "country": country})
        requests.post("https://scratch.mit.edu/accounts/settings/", headers=self.headers, data=payload)

    def update_headers(self) -> None:
        self.cookies = f"scratchcsrftoken={self.csrf_token};scratchsessionsid={self.session_id};" \
                       f"scratchlanguage={self.lang}"
        self.headers = {
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/75.0.3770.142 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": self.cookies,
            "referer": "https://scratch.mit.edu",
        }

    @staticmethod
    def get_csrf():
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "Cookie": f"scratchlanguage=en;permissions=%7B%7D;",
            "referer": "https://scratch.mit.edu",
        }
        req = requests.get("https://scratch.mit.edu/csrf_token/", headers=headers)
        try:
            csrf = re.search("scratchcsrftoken=(.*?);", req.headers["Set-Cookie"]).group(1)
        except Exception:
            LoginError("Can't get CSRF token")
        else:
            return csrf

    @staticmethod
    def get_sessionid(username, password) -> str:
        _headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            "x-csrftoken": "a",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://scratch.mit.edu",
            "Cookie": "scratchcsrftoken=a;scratchlanguage=ru;"
        }
        payload = json.dumps({"username": username, "password": password})
        request = requests.post(
            "https://scratch.mit.edu/login/", data=payload, headers=_headers
        )
        try:
            session_id = str(re.search('"(.*)"', request.headers["Set-Cookie"]).group())
        except Exception:
            raise LoginError("Login credits are wrong or you banned on scratch")
        return session_id
