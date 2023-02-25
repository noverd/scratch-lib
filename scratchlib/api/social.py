import scratchlib.api.session as session
from scratchlib.api.exceptions import UserGettingError, UnauthorizedError, StudioGettingError, ProjectUnsharedError, ProjectGettingError
import json


class Project:
    def __init__(self, scratch_session: session.Session, project_id: int, author_username = None):
        self.author_username = author_username
        self.session = scratch_session.session
        self.scratch_session = scratch_session
        self.id: int = project_id
        self.update()

    def update(self):
        try:
            data = self.session.get(f"https://api.scratch.mit.edu/projects/{self.id}/").json()
        except:
            raise ProjectGettingError("Can't get project")
        self.title: str = data["title"]
        self.description: str = data["description"]
        self.instructions: str = data["instructions"]
        self.visibility: bool = data["visibility"] == "visible"
        self.public: bool = data["public"]
        self.comments_allowed: bool = data["comments_allowed"]
        self.is_published: bool = data["is_published"]
        self.author: User = User(self.scratch_session, data["author"], username=self.author_username)
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
        try:
            self.project_token: str = data["project_token"]
        except:
            raise ProjectUnsharedError("Can't working with Unshared Project")

    def get_remixes(self, all=False, limit=20, offset=0):
        if all:
            projects = []
            while True:
                res = self.session.get(
                    f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?limit=40&offset={offset}").json()
                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            projects = self.session.get(
                f"https://api.scratch.mit.edu/projects/{self.id}/remixes/?limit={limit}&offset={offset}"
            ).json()

        return [Project(self.scratch_session, _) for _ in projects]

    def remix(self, title: str, return_id=False):
        url = f'https://projects.scratch.mit.edu/?is_remix=1&original_id={self.id}&title={title}'
        json_data = self.session.post(url, json=self.get_scripts()).json()
        if json_data["status"] != "ok":
            return None
        if return_id:
            return int(json_data["content-name"])
        else:
            return Project(self.scratch_session, json_data["content-name"], self.scratch_session.username)

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

    def view(self):
        self.session.post(f"https://api.scratch.mit.edu/users/{self.author.username}/projects/{str(self.id)}/views/")

    def set_thumbnail(self, filename: str):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t change project thumbnail - This is not your project.")
        with open(filename, "rb") as f:
            self.session.post(
                f"https://scratch.mit.edu/internalapi/project/thumbnail/{str(self.id)}/set/", data=f.read()
            )

    def unshare(self):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t unshare project - This is not your project.")
        self.session.put(f"https://api.scratch.mit.edu/proxy/projects/{str(self.id)}/unshare/")

    def toggle_commenting(self):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t toggle project commenting - This is not your project.")
        data = json.dumps({"comments_allowed": not self.comments_allowed})
        self.comments_allowed = not self.comments_allowed
        self.session.put(f"https://api.scratch.mit.edu/projects/{str(self.id)}/", data=data).json()

    def turn_on_commenting(self):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t turn on project commenting - This is not your project.")
        data = json.dumps({"comments_allowed": True})
        self.comments_allowed = True
        self.session.put(f"https://api.scratch.mit.edu/projects/{str(self.id)}/", data=data).json()

    def turn_off_commenting(self):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t turn off project commenting - This is not your project.")
        data = json.dumps({"comments_allowed": False})
        self.comments_allowed = False
        self.session.put(f"https://api.scratch.mit.edu/projects/{str(self.id)}/", data=data).json()

    def share(self):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t share project - This is not your project.")
        self.session.put(f"https://api.scratch.mit.edu/proxy/projects/{str(self.id)}/share/")

    def set_title(self, title: str):
        if self.scratch_session.username != self.author.username:
            raise UnauthorizedError("Can`t change project title - This is not your project.")
        data = {"title": title}
        self.session.put(f"https://api.scratch.mit.edu/projects/{str(self.id)}", data=json.dumps(data))

    def get_scripts(self):
        try:
            return self.session.get(
                f"https://projects.scratch.mit.edu/{str(self.id)}?token={str(self.project_token)}"
            ).json()
        except:
            raise ProjectUnsharedError("Can't working with Unshared Project")


class User:
    def __init__(self, scratch_session: session.Session, user, username: str = None):
        self.session = scratch_session.session
        self.username = username
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

    def update(self):
        data = self.session.get(f"https://api.scratch.mit.edu/users/{self.username}").json()
        try:
            data["code"]
        except Exception:
            pass  # All OK
        else:
            raise UserGettingError(data["code"])
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

    def toggle_commenting(self):
        if self.session.username != self.username:
            raise UnauthorizedError("Can`t toggle profile commenting - This is not your profile/user.")
        self.session.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/toggle-comments/")

    def post_comment(self, content: str, parent_id="", comment_id="") -> None:
        data = {
            "commentee_id": comment_id,
            "content": content,
            "parent_id": parent_id,
        }
        self.session.post(f"https://scratch.mit.edu/site-api/comments/user/{self.username}/add/", data=json.dumps(data))

    def get_followers(self, all=False, limit=20, offset=0, get_nick=False):
        if all:
            users = []
            offset = 0
            while True:
                res = self.session.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(self.session.get(
                f"https://api.scratch.mit.edu/users/{self.username}/followers/?limit={str(limit)}&offset={str(offset)}").json())

        if get_nick:
            return [i["username"] for i in users]
        return [User(self.session, user) for user in users]

    def get_favorites(self, all=False, limit=20, offset=0, get_id: bool = False):
        if all:
            projects = []
            offset = 0
            while True:
                res = self.session.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit=40&offset={str(offset)}"
                ).json()

                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            projects = list(
                self.session.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/favorites/?limit={str(limit)}&offset={str(offset)}"
                ).json()
            )

        if get_id:
            return [project["id"] for project in projects]
        return [Project(self.session, project) for project in projects]

    def get_projects(self, all=False, limit=20, offset=0, get_id: bool = False):
        if all:
            offset = 0
            projects = []
            while True:
                res = self.session.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit=40&offset={str(offset)}"
                ).json()
                projects += res
                if len(res) != 40:
                    break
                offset += 40
        else:

            projects = self.session.get(
                f"https://api.scratch.mit.edu/users/{self.username}/projects/?limit={str(limit)}&offset={str(offset)}"
            ).json()

        for x, i in enumerate(projects):
            projects[x].update({
                "author": self.username
            })
        if get_id:
            return [project["id"] for project in projects]

        return [Project(self.session, project) for project in projects]

    def get_following(self, all=False, limit=20, offset=0, get_nick=False):
        if all:
            users = []
            offset = 0
            while True:
                res = self.session.get(
                    f"https://api.scratch.mit.edu/users/{self.username}/following/?limit=40&offset={str(offset)}"
                ).json()

                users += res
                if len(res) != 40:
                    break
                offset += 40
        else:
            users = list(self.session.get(
                f"https://api.scratch.mit.edu/users/{self.username}/following/?limit={str(limit)}&offset={str(offset)}").json())

        if get_nick:
            return [i["username"] for i in users]
        return [User(self.session, user) for user in users]

    def follow(self):
        return self.session.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/add/?usernames={self.username}"
        ).json()

    def unfollow(self):
        return self.session.put(
            f"https://scratch.mit.edu/site-api/users/followers/{self.username}/remove/?usernames={self.username}"
        ).json()


class Studio:
    def __init__(self, scratch_session: session.Session, studio):
        self.session = scratch_session.session
        if isinstance(studio, int):
            self.username = studio
            data = self.session.get(f"https://api.scratch.mit.edu/users/{self.username}").json()
            try:
                data["code"]
            except Exception:
                pass  # All OK
            else:
                raise UserGettingError(data["code"])
        elif isinstance(studio, dict):
            data = studio
        else:
            raise StudioGettingError("Uncorrected type of argument 'studio'")
