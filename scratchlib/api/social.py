import session
from exceptions import UserGettingError
import json


class Project:
    def __init__(self, scratch_session: session.Session, project_id: int):
        self.session = scratch_session.session
        self.scratch_session = scratch_session
        self.id: int = project_id
        self.update()

    def update(self):
        data = self.session.get(f"https://api.scratch.mit.edu/projects/{self.id}/").json()
        self.title: str = data["title"]
        self.description: str = data["description"]
        self.instructions: str = data["instructions"]
        self.visibility: bool = data["visibility"] == "visible"
        self.public: bool = data["public"]
        self.comments_allowed: bool = data["comments_allowed"]
        self.is_published: bool = data["is_published"]
        self.author: User = User(self.scratch_session, data["author"])
        self.image: str = data["instructions"]
        self.images: dict = data["image"]
        self.created: str = data["history"]["created"]
        self.modified: str = data["history"]["modified"]
        self.shared: str = data["history"]["shared"]
        self.instructions: str = data["instructions"]
        self.views: int = data["stats"]["views"]
        self.loves: int = data["stats"]["loves"]
        self.favorites: int = data["stats"]["favorites"]
        self.remixes: int = data["stats"]["remixes"]
        self.parent: int = data["remix"].get("parent")
        self.root: int = data["remix"]["root"]
        self.is_remix: bool = bool(self.parent)

    def post_comment(self, content, parent_id="", comment_id=""):
        data = {
            "commentee_id": comment_id,
            "content": content,
            "parent_id": parent_id,
        }
        return self.session.post(
            f"https://api.scratch.mit.edu/proxy/comments/project/{str(self.id)}/", data=json.dumps(data)
        ).json()

    def love(self):
        return self.session.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self.scratch_session.username}"
        ).json()["userLove"]

    def unlove(self):
        return self.session.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/loves/user/{self.scratch_session.username}"
        ).json()["userLove"]

    def favorite(self):
        return self.session.post(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self.scratch_session.username}"
        ).json()["userFavorite"]

    def unfavorite(self):
        return self.session.delete(
            f"https://api.scratch.mit.edu/proxy/projects/{self.id}/favorites/user/{self.scratch_session.username}"
        ).json()["userFavorite"]


class User:
    def __init__(self, scratch_session: session.Session, user):
        self.session = scratch_session.session
        if isinstance(user, str):
            self.username = user
            data = self.session.get(f"https://api.scratch.mit.edu/users/{self.username}").json()
            try:
                data["code"]
            except Exception:
                pass  # All OK
            else:
                raise UserGettingError(data["code"])
        elif isinstance(user, dict):
            data = user
        else:
            raise UserGettingError("Uncorrected type of argument 'user'")
        self.id: int = data["id"]
        self.scratch_team: bool = data["scratchteam"]
        self.join_time = data["history"]["joined"]
        self.profile_id: int = data["profile"]["id"]
        self.icons: dict = data["profile"]["images"]
        try:
            self.status = data["profile"]["status"]
            self.bio = data["profile"]["bio"]
            self.country = data["profile"]["country"]
        except KeyError:
            self.status = None
            self.bio = None
            self.country = None

    def get_activity_html(self, limit=10):
        r = self.session.get(f"https://scratch.mit.edu/messages/ajax/user-activity/?user={self.username}&max={limit}")
        return r.text

    def get_message_count(self) -> int:
        return self.session.get(f"https://api.scratch.mit.edu/users/{self.username}/messages/count/").json()["count"]

    def post_comment(self, content: str, parent_id="", comment_id="") -> None:
        data = {
            "commentee_id": comment_id,
            "content": content,
            "parent_id": parent_id,
        }
        self.session.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/", data=json.dumps(data))


class Studio:
    def __init__(self):
        pass


