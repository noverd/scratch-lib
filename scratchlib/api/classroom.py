import bs4
import requests


class ClassRoom:
    def __init__(self, classroom_id: int):
        self.id: int = classroom_id

    def get_members_from_page(self, page: int = 1):
        soup = bs4.BeautifulSoup(requests.get(f"https://scratch.mit.edu/classes/{self.id}/students/?page={page}").text,
                                 "html"
                                 ".parser")
        return \
            [_.find("span").contents[1].contents[0].strip() for _ in soup.find_all("li", {"class": "user thumb item"})]