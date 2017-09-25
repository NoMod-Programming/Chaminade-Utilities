"""
bbspider.py - By Hazel Pedemonte. MIT License.

A simple "enough" spider for Blackboard, a horribly
written piece of JavaScript and ASP.NET garbabe,
with a very basic understanding of security.
"""

import requests
from bs4 import BeautifulSoup

BB_BASE_URL = "https://www.chaminadeonline.org"


class BlackboardSpider(object):
    """
    The class for the Blackboard Spider.

    Create an instance with:
        BlackboardSpider(username, password)
    """

    def __init__(self, username, password):
        """
        The initializer for BlackboardSpider.

        Set up the username + password for this class,
        get the Blackboard session ready, and scrape
        the necessary cookies
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.req = None
        self.session.headers = {
        }

    def login(self):
        """
        Log into Blackboard.

        Make sure to collect the login cookies for use later on.
        """
        self.req = self.session.get(BB_BASE_URL)
        doc = BeautifulSoup(self.req.text, 'html.parser')
        loginform = doc.find('form', {"name": "login"})
        inputs = {}
        for inputtag in loginform.find_all('input'):
            inputs[inputtag['name']] = inputtag.get('value', '')
        inputs['user_id'] = self.username
        inputs['password'] = self.password
        self.req = self.session.post(
            BB_BASE_URL + loginform['action'],
            data=inputs,
            allow_redirects=True
        )

    def get_classes(self):
        """
        Return a list of courses.

        Requires login to use.
        """
        self.req = self.session.post(
            BB_BASE_URL + "/webapps/portal/execute/tabs/tabAction",
            data={
                'action': 'refreshAjaxModule',
                'modId': '_22_1',
                'tabId': '_2_1',
                'tab_tab_group_id': '_2_1',
            }
        )
        doc = BeautifulSoup(self.req.text, 'html.parser')
        doc = BeautifulSoup(doc.find_all(text=True)[-1], 'html.parser')
        class_listing = doc.find("ul", class_="courseListing")
        courses = []
        for course in class_listing.find_all('li'):
            course_name = (course.find('a').text)
            courses.append(':'.join(course_name.split(':')[1:]).strip())
        return courses


def main():
    """
    Simple test program.

    Logins to Blackboard and prints a list of courses.
    """
    spider = BlackboardSpider(input("Username: "), input("Password: "))
    spider.login()
    print(spider.get_classes())

if __name__ == "__main__":
    main()
