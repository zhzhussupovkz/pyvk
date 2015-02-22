# -*- coding: utf-8 -*-

import urllib
import urllib2
import cookielib
import lxml.html
import urlparse
import ast

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

    # post request
    def post_request(self, url, data):
        data = urllib.urlencode(data)
        try:
            resp = self.opener.open(self.vk_url+ '/' + url, data)
            if resp.getcode() == 200:
                return resp.read()
        except Exception, e:
            print e

    # login
    def action_login(self):
        qd = self.get_ip_h()
        data = {
            'act' : qd.get('act'),
            'to' : '',
            '_origin' : qd.get('_origin'),
            'ip_h' : qd.get('ip_h'),
            'utf8' : qd.get('utf8'),
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
    def get_my_friends(self):
        friends = []
        friends_page = self.get_page(self.vk_url + '/friends')
        if friends_page:
            tree = lxml.html.fromstring(friends_page)
            my_id = tree.xpath('.//input[@name="id"]/@value')
            data = {
                'act' : 'load_friends_silent',
                'al' : '1',
                'gid' : '0',
                'id' : my_id[0],
            }
            friends_data = self.post_request("al_friends.php", data)
            start = friends_data.find('all')
            end = friends_data.find(',\"all_requests\"')
            final = friends_data[start:end].replace('all":', '').strip()
            friends_list = ast.literal_eval(final)
            for f in friends_list:
                friends.append('id' + f[0])
        return friends

    # get my groups
    def get_my_groups(self):
        groups = []
        groups_page = self.get_page(self.vk_url + '/groups')
        if groups_page:
            tree = lxml.html.fromstring(groups_page)
            my_id = tree.xpath('.//input[@name="id"]/@value')
            data = {
                'act' : 'get_list',
                'al' : '1',
                'mid' : my_id[0],
                'tab' : 'groups',
            }
            groups_data = self.post_request("al_groups.php", data)
            start = groups_data.find('[[')
            final = groups_data[start:].replace('[[', '').replace(']]', '').strip()
            for gl in final.split('],['):
                gid = str(gl.split(',')[2])
                if gid.isdigit():
                    groups.append('public' + gid)
        return groups

    # get user's friends
    def get_friends(self, user_id):
        friends = []
        data = {
            'act' : 'load_friends_silent',
            'al' : '1',
            'gid' : '0',
            'id' : user_id,
        }
        friends_data = self.post_request("al_friends.php", data)
        start = friends_data.find('all')
        end = friends_data.find(']]}') + 2
        final = friends_data[start:end].replace('all":', '').strip()
        friends_list = ast.literal_eval(final)
        for f in friends_list:
            friends.append('id' + f[0])
        return friends

    # get user's audios
    def get_audios(self, user_id):
        audios = []
        data = {
            'act' : 'load_audios_silent',
            'al' : '1',
            'id' : user_id,
            'please_dont_ddos':'1',
        }
        audios_data = self.post_request('audio', data)
        start = audios_data.find('all')
        end = audios_data.find(']]}') + 2
        final = audios_data[start:end].replace('all":', '').strip()
        audios_list = ast.literal_eval(final)
        for a in audios_list:
            mp3 = a[2][:a[2].find('.mp3')+4]
            audios.append(mp3)
        return audios

mylogin = 'mylogin'
mypass = 'mypass'

bot = Pyvk(login = mylogin, password = mypass)
print bot.get_my_friends()
print bot.get_my_groups()

