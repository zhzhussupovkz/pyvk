# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib

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

mylogin = 'mylogin'
mypass = 'mypass'

bot = Pyvk(login = mylogin, password = mypass)
bot.action_login()
