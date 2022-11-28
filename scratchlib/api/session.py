import json
import re
import requests
from exceptions import LoginError


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

