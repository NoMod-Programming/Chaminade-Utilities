"""
ncspider.py - By Hazel Pedemonte. MIT License.

A simple "enough" spider for NetClassroom, a horribly
written piece of ASP.NET garbage, with no understanding
of security.
"""

import posixpath
import re
import requests
from bs4 import BeautifulSoup

NC_BASE_URL = "http://netclassroom.chaminade.org"
NC_LOGIN_URL = NC_BASE_URL + "/NetClassroom7/Forms/login.aspx"


class NetclassroomSpider(object):
    """
    The class for the Netclassroom Spider.

    Create an instance with:
        NetclassroomSpider(username, password)
    """

    def __init__(self, username, password):
        """
        The initializer for NetclassroomSpider.

        Set up the username + password for this class,
        get the netclassroom session ready, and scrape
        the necessary cookies
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.req = None
        self.session.headers = {
            'User-Agent': 'NCSpyder/1.0',
            'Referer': NC_LOGIN_URL,
        }

    def navigate_to_page(self, eventtarget, eventargument, fakeinputs = None):
        """
        Navigate to the specified page.

        Reproduces the *horrible* ASP.NET post request handler
        used in the web version of NetClassroom
        """
        doc = BeautifulSoup(self.req.text, 'html.parser')
        the_form = doc.find(id="Form1")
        inputs = {}
        for inputtag in the_form.find_all('input'):
            inputs[inputtag['name']] = inputtag.get('value', '')
        inputs['__postbackAction'] = 'dont_save'
        inputs['__EVENTTARGET'] = eventtarget
        inputs['__EVENTARGUMENT'] = eventargument
        inputs['availableWidth'] = '800'
        inputs['availableHeight'] = '600'
        for inputname, inputvalue in (fakeinputs or {}).items():
            inputs[inputname] = inputvalue
        form_action = doc.body.form.get('action')
        form_post = posixpath.join(posixpath.dirname(NC_LOGIN_URL),
                                   form_action)
        self.req = self.session.post(
            form_post,
            data=inputs
        )

    def login(self):
        """
        Log into NetClassroom.

        Make sure to collect the login cookies for use later on.
        """
        # Get the login page and parse it:
        self.req = self.session.get(NC_LOGIN_URL)
        doc = BeautifulSoup(self.req.text, 'html.parser')

        # Get the login form and fill the username and password
        inputs = {}
        for inputtag in doc.body.form.find_all('input'):
            inputs[inputtag['name']] = inputtag.get('value', '')
        inputs['sid'] = self.username
        inputs['pin'] = self.password

        # Post to the login page, which collects the login cookies
        self.req = self.session.post(
            NC_LOGIN_URL,
            data=inputs
            )

        # Check for a successful login
        login_success = 'loading' in self.req.text.lower()
        if login_success:
            return True
        raise RuntimeError(
            "Login failed for user \"{}\"".format(self.username)
            )

    def getclasses(self):
        """
        Return a list of all the classes for the current user.

        Requires login, and might only work with Chaminade.
        """
        self.navigate_to_page('myMenuId$Menu1', 'mnuPerformance')
        # Actually get the classes now
        doc = BeautifulSoup(self.req.text, 'html.parser')
        class_spinner = doc.find(id='_ctl14_cpWhatever_lstWhatever')
        classes = {}
        for option_spinner in class_spinner.find_all('option'):
            classes[','.join(option_spinner.text.split(',')[1:]).strip()] = option_spinner['value']
        return classes

    def get_courses(self):
        return list(self.getclasses().keys())

    def grades_for_class(self, courseId):
        """
        Return the grade, in a double.

        Requires login, and might only work with Chaminade.
        """ 
        self.navigate_to_page('_ctl14$cpWhatever$lstWhatever','',{'_ctl14:cpWhatever:lstWhatever':courseId})
        doc = BeautifulSoup(self.req.text, 'html.parser')
        nc_content = doc.find(id='ncContent_webDG')
        grade_text = nc_content.div.find_all('span')[0].text.split(':')[-1]
        grade_float = float(grade_text)
        return grade_float

    def course_schedule(self):
        """
        Return the current schedule for today.

        Requires login, and only works with Chaminade.
        """
        self.__init__(self.username, self.password)
        self.login()
        self.navigate_to_page('myMenuId:Menu1','mnuScheduleCalendar')
        doc = BeautifulSoup(self.req.text, 'html.parser')
        date_div = doc.find(id='Table1')
        curr_schedule = []
        for date_span in date_div.find_all('span'):
            mat = re.match(r'(?P<block>\w),.*?, (?P<course_name>.*?),\s*(?P<teacher>.*?),\s*(?P<classroom>.*)', date_span.text)
            if mat:
                curr_schedule.append((mat.group('block'), mat.group('course_name'), mat.group('teacher'), mat.group('classroom')))
        return curr_schedule


def main():
    """
    Simple test program.

    Logins to NetClassroom and print a list of all classes.
    """
    spider = NetclassroomSpider(input("Username: "), input("Password: "))
    spider.login()
    print(spider.getclasses())
    for course_name, course_id in spider.getclasses().items():
        print("Grade for class \"{}\":".format(course_name).ljust(75, ' ') + str(spider.grades_for_class(course_id)))
    print("Current schedule:")
    print(spider.course_schedule())

if __name__ == "__main__":
    main()
