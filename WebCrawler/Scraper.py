
from bs4 import BeautifulSoup
from http_requests import KeepAliveRequests

class Scraper:

    url_queue = {} # map[str] = 0
    url_blacklist = {} # map[str] = 0 
    flags = [] # list[str]

    logged_in = None

    cookie = None

    def __init__(self, username, password):
        self.requester = KeepAliveRequests("fring.ccs.neu.edu")
        self.fakebook_username = username
        self.fakebook_password = password

    def log_in(self):
        '''
        Logs into Fakebook.

        Requests the login page, gets a csrf token, and posts it to the login
        page along with a username and a password.

        Fakebook does not require a cookie to be sent along with the request,
        just that a login request is made (verified in Postman).
        '''
        login_url = "http://fring.ccs.neu.edu/accounts/login/"
        response = self.requester.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the csrf token, required to prevent invalid requests
        csrf_token = soup.find(attrs={'name': 'csrfmiddlewaretoken'}).get('value')

        resp = self.requester.post(login_url, data={
            "csrfmiddlewaretoken": csrf_token,
            "password": self.fakebook_password,
            "username": self.fakebook_username,
        }, headers={
            "Cookie": "csrftoken={};".format(csrf_token)
        })
        self.logged_in = True
        self.cookie = resp.response_headers['Set-Cookie'] + "; csrftoken={}".format(csrf_token)

    def log_out(self):
        self.logged_in = False
        resp = self.requester.get("http://fring.ccs.neu.edu/accounts/logout", headers={"Cookie": self.cookie})

    def is_logged_in(self):
        if self.logged_in is None:
            resp = self.requester.get("fring.ccs.neu.edu/fakebook/")
            return not (resp.status_code > 300 and resp.status_code < 400)
        else:
            return self.logged_in

    def get_page(self, url):
        if not self.is_logged_in():
            self.log_in()
        return self.requester.get(url, headers={"Cookie": self.cookie})

    def add_url_to_queue(self, url):
        '''
        Add URL to queue. If it's not in the queue or the blacklist, add it.
        If it's not in the http://fring.ccs.neu.edu/ domain, don't add it.
        '''
        actual_url = "http://fring.ccs.neu.edu" + url
        if self.url_queue.get(actual_url) is None and self.url_blacklist.get(actual_url) is None:
            # If this refers to any external domain (non relative)
            # we shouldnt scrape it.
            if ":" not in url:
                self.url_queue[actual_url] = 0

    def dissect_page(self, html_source):
        '''
        Dissects the given HTML source code to see if it can
        find any flags and adds to the queue of URLs to go to.
        Adds flags to the flags list.
        '''
        
        # url_queue = [] # list[str]
        soup = BeautifulSoup(html_source, 'html.parser')
        for link in soup.find_all('a'):
            self.add_url_to_queue(link.get('href'))

        for flag in soup.find_all(attrs={'class': 'secret_flag'}):
            #FLAG: 64-character
            temp = flag.string
            temp = temp.replace('FLAG: ', '')
            if temp not in self.flags:
                self.flags.append(temp)
                print temp


    def next_page(self):
        '''
        Goes to the next URL in the queue and returns the HTML.
        Adds that URL to the blacklist and removes it from the queue.
        Returns the Response object from getting that page.
        '''

        next_url = self.url_queue.keys()[0]
        self.url_queue.pop(next_url)

        self.url_blacklist[next_url] = 0

        response = self.get_page(next_url)

        # If we see the server errors, retry.
        while response.status_code >= 500:
            self.requester.initiate_connection()
            response = self.get_page(next_url)

        # If the server is a 403 or 404, abandon and go to the next page.
        if response.status_code >= 400:
            return self.next_page()

        if response.status_code == 301:
            return self.get_page(response.response_headers['Location'])

        return response


    def run(self):
        '''
        Scrapes through Fakebook looking for flags. Returns them once
        it finds 4 flags.
        '''

        response = self.get_page("http://fring.ccs.neu.edu/fakebook/")
        while len(self.flags) < 5:
            self.dissect_page(response.text)
            response = self.next_page()


        return self.flags

    def close(self):
        self.requester.sock.quit()

