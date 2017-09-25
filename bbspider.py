"""
bbspider.py - By Hazel Pedemonte. MIT License.

A simple "enough" spider for Blackboard, a horribly
written piece of JavaScript and ASP.NET garbabe,
with a very basic understanding of security.
"""

import re
import requests
from bs4 import BeautifulSoup

BB_BASE_URL = "https://www.chaminadeonline.org"
COURSEID_REGEX = re.compile(r"id=(\w+)")


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

    def get_courses(self):
        """
        Return a list of courses and their ids.

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
        courses = {}
        for course in class_listing.find_all('li'):
            course_name = course.find('a').text
            course_name = (':'.join(course_name.split(':')[1:]).strip())
            course_id = course.find('a')['href']
            course_id = COURSEID_REGEX.search(course_id).group(1)
            courses[course_name] = course_id
        return courses

    def get_coursenames(self):
        """
        Return a list of course names.

        Requires login to use
        """
        return list(self.get_courses().keys())


def main():
    """
    Simple test program.

    Logins to Blackboard and prints a list of courses.
    """
    spider = BlackboardSpider(input("Username: "), input("Password: "))
    spider.login()
    print(spider.get_coursenames())

if __name__ == "__main__":
    main()
