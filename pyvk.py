# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import lxml.html
import urlparse

class Pyvk:
    def __init__(self, login = None, password = None):
        self.login = login
        self.password = password
        self.login_url = 'https://login.vk.com'
        self.vk_url = 'https://vk.com'

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), urllib2.HTTPRedirectHandler())
        self.opener.addheaders.append(('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36'))
        self.qd = {}
        self.action_login()

    # get ip_h
    def get_ip_h(self):
        try:
            resp = self.opener.open(self.vk_url)
            if resp.getcode() == 200:
                page = resp.read()
                tree = lxml.html.fromstring(page)
                action = tree.xpath('.//form[@action]')[0].get('action')
                o = urlparse.urlparse(action)
                qd = urlparse.parse_qs(o.query)
                self.qd['ip_h'] = qd.get('ip_h')[0]
                self.qd['_origin'] = qd.get('_origin')[0]
                self.qd['act'] = qd.get('act')[0]
                self.qd['utf8'] = qd.get('utf8')[0]
                return self.qd
            else:
                return None
        except Exception, e:
            return None

    # login
    def action_login(self):
        qd = self.get_ip_h()
        data = {
            'act' : qd.get('act'),
            'to' : '',
            '_origin' : qd.get('_origin'),
            'ip_h' : qd.get('ip_h'),
            'email' : self.login,
            'pass' : self.password,
            'expire' : '',
        }

        data = urllib.urlencode(data)
        try:
            resp = self.opener.open(self.login_url, data)
            if resp.getcode() == 200:
                return self.cj._cookies
        except Exception, e:
            print e

    # get main page
    def get_main_page(self):
        return self.get_page(self.vk_url)

    # get page
    def get_page(self, url):
        if not self.cj._cookies:
            self.action_login()
        try:
            resp = self.opener.open(url)
            if resp.getcode() == 200:
                return resp.read()
            else:
                return None
        except Exception, e:
            return None

    # get my friends
    def get_my_friends(self, section = None):
        friends = []
        sections = ['all', 'online']
        if section and section in sections:
            friends_page = self.get_page(self.vk_url + '/friends?section=' + section)
        friends_page = self.get_page(self.vk_url + '/friends')
        if friends_page:
            tree = lxml.html.fromstring(friends_page)
            for f in tree.xpath('.//a[@class="si_owner"]/@href'):
                friends.append(f.replace('/', ''))
        return friends

    # get my groups
    def get_my_groups(self):
        groups = []
        groups_page = self.get_page(self.vk_url + '/groups')
        if groups_page:
            tree = lxml.html.fromstring(groups_page)
            for g in tree.xpath('.//a[@class="simple_fit_item"]/@href'):
                groups.append(self.vk_url + g)
        return groups

mylogin = 'mylogin'
mypass = 'mypass'

bot = Pyvk(login = mylogin, password = mypass)
print bot.get_my_friends()
print bot.get_my_groups()
