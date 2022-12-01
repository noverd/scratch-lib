import requests
import bs4
from typing import List


class ForumPost:
    def __init__(self, author, content, date, post_id: int, post_num: int):
        self.author: str = author
        self.content: str = content
        self.date = date
        self.post_id: int = post_id
        self.post_num: int = post_num


class Forum:
    def __init__(self, forum_id: int):
        self.forum_id: int = forum_id

    def get_posts(self) -> List[ForumPost]:
        soup = bs4.BeautifulSoup(requests.get(f"https://scratch.mit.edu/discuss/topic/{self.forum_id}").text, "html"
                                                                                                              ".parser")
        posts = soup.find_all("div", {"class": "blockpost roweven firstpost"})
        out = []
        for post in posts:
            post_id = int(post.find("a")["name"][5:])
            post_num = int(post.find("span", {"class": "conr"}).contents[0][1:])
            post_date = post.find_all("a")[1].contents[0]
            post_author = post.find("a", {"class": "black username"}).contents[0]
            post_content = ''
            for i in post.find("div", {"class": "post_body_html"}).contents:
                post_content = post_content + "\n" + str(i)
            out.append(ForumPost(post_author, post_content, post_date, post_id, post_num))
        return out
