# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib

from BeautifulSoup import BeautifulSoup

class Pyvk:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.login_url = 'https://login.vk.com'
        self.quick_login_url = 'https://login.vk.com/?act=login'
        self.vk_url = 'https://vk.com'

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), urllib2.HTTPRedirectHandler())
        self.opener.addheaders.append(('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36'))

        self.main_cookies = {}
        self.action_login()

    # login
    def action_login(self):
        data = {
            'act' : 'login',
            'to' : '',
            '_origin' : 'http://vk.com',
            'ip_h' : '9688341f22da58212d',
            'email' : self.login,
            'pass' : self.password,
            'expire' : '',
        }

        data = urllib.urlencode(data)
        try:
            resp = self.opener.open(self.quick_login_url, data)
            if resp.getcode() == 200:
                self.main_cookies = {
                    'remixsid' : self.cj._cookies['.vk.com']['/']['remixsid'].value,
                    'remixlang' : self.cj._cookies['.vk.com']['/']['remixlang'].value,
                    }
        except Exception, e:
            print e

    # get main page
    def get_main_page(self):
        return self.get_page(self.vk_url)

    # get page
    def get_page(self, url):
        if not self.main_cookies:
            self.action_login()
        try:
            resp = self.opener.open(url)
            if resp.getcode() == 200:
                return resp.read()
            else:
                return None
        except Exception, e:
            return None

    # get urls
    def get_urls(self, url):
        links = set()
        page = self.get_page()
        if page:
            soup = BeautifulSoup(page)
            for link in soup.findAll('a'):
                links.add(link.get('href'))
        return [links]

    # get my friends
    def get_my_friends(self, section = None):
        friends = []
        sections = ['all', 'online']
        if section and section in sections:
            friends_page = self.get_page(self.vk_url + '/friends?section=' + section)
        friends_page = self.get_page(self.vk_url + '/friends')
        if friends_page:
            soup = BeautifulSoup(friends_page)
            f_count = soup.findAll('em', attrs={'class' : "tab_counter"})[0].contents[0]
            for f in soup.findAll('a', attrs = {'class' : "si_owner"}):
                friend = {
                    'link' : self.vk_url + f['href'],
                    'name' : f.contents[0]
                }
                friends.append(friend)
        return friends

    # get my groups
    def get_my_groups(self):
        groups = []
        groups_page = self.get_page(self.vk_url + '/groups')
        if groups_page:
            soup = BeautifulSoup(groups_page)
            for g in soup.findAll('a', attrs = {'class' : 'simple_fit_item'}):
                groups.append(self.vk_url + g['href'])
        return groups

mylogin = 'mylogin'
mypass = 'mypass'

bot = Pyvk(login = mylogin, password = mypass)
print bot.get_groups()
