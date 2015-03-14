# -*- coding: utf-8 -*-

# The MIT License (MIT)

# Copyright (c) 2015 Zhassulan Zhussupov

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urllib
import urllib2
import cookielib
import lxml.html
import urlparse
import ast
import sys
import os
import json

class Pyvk:

    FRIENDS = 'al_friends.php'
    GROUPS_URL = 'al_groups.php'
    AUDIOS_URL = 'audio'
    PHOTOS_URL = 'al_photos.php'
    PAGE_URL = 'al_page.php'

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

    # download user's audios
    def download_audios(self, user_id, n = 2):
        audios = self.get_audios(user_id)
        print "User: %s. Audios: %s (all), %s (download)" % (user_id, len(audios), n)
        if len(audios) > 0:
            for track in audios[:n]:
                trackname = track.split('/')[-1]
                filename = './id%s/%s' % (str(user_id), trackname)
                try:
                    resp = urllib2.urlopen(track)
                    if resp.getcode() == 200:
                        if not os.path.exists(os.path.dirname(filename)):
                            os.makedirs(os.path.dirname(filename))
                        size = resp.info().getheaders('Content-Length')[0]
                        print "Starting downloading track: %s. Size: %s bytes" % (track, size)
                        f = open(filename, "wb")
                        downloaded = 0
                        block = 2048
                        while True:
                            buffer = resp.read(block)
                            if not buffer:
                                break
                            downloaded += len(buffer)
                            f.write(buffer)
                            p = float(downloaded) / int(size)
                            status = r"{0}  [{1:.2%}]".format(downloaded, p)
                            status = status + chr(8)*(len(status)+1)
                            sys.stdout.write(status)
                        f.close()
                        print "Track %s: OK" % filename
                    else:
                        print "Track %s: NOK. Server response code: %s" % (filename, resp.getcode())
                except Exception, e:
                    print "Cannot download track %s: NOK" % filename
                    print e

    # get user's photo
    def get_photo(self, user_id):
        data = {
            'act' : 'fast_get_photo',
            'al' : '1',
            'oid' : user_id,
        }
        photo_data = self.post_request('al_photos.php', data)
        start = photo_data.find('_id') - 2
        end = photo_data.find('}}') + 2
        try:
            final = json.loads(photo_data[start:end].strip())
            img_link = final.get('temp').get('base') + final.get('temp').get('z_')[0] + '.jpg'
            resp = urllib2.urlopen(img_link)
            filename = './id%s.jpg' % user_id
            f = open(filename, "wb")
            f.write(resp.read())
            f.close()
        except Exception, e:
            print "Cannot get user's photo"
            print e

    # get group members
    def get_group_members(self, group_id):
        members = set()
        j = 0
        data = {
            'act' : 'box',
            'al' : '1',
            'oid' : '-' + group_id,
            'tab' : 'members',
        }
        members_data = self.post_request('al_page.php', data)
        members_count_str = members_data[members_data.find('<span class="fans_count">'):members_data.find('</span></nobr>')]
        count = members_count_str.replace('<span class="fans_count">', '').replace('<span class="num_delim">', '').replace('</span>', '').replace(' ', '')
        c = int(count)/60
        while j < c+1:
            if j == 0:
                members_data = self.post_request('al_page.php', data)
                if members_data:
                    start = members_data.find('div class="fans_rows"') - 1
                    end = members_data.find('a class="fans_more_link"') - 1
                    final = members_data[start:end]
                    tree = lxml.html.fromstring(final)
                    user_ids = tree.xpath('.//a[@class="fans_fan_ph"]/@href')
                    for user in user_ids:
                        members.add(user.replace('/', ''))
            else:
                data['offset'] = j * 60
                members_data = self.post_request('al_page.php', data)
                if members_data:
                    start = members_data.find('div class="fans_fan_row inl_bl"') - 1
                    end = members_data.find('<!><!int>')
                    final = members_data[start:end]
                    tree = lxml.html.fromstring(final)
                    user_ids = tree.xpath('.//a[@class="fans_fan_ph"]/@href')
                    for user in user_ids:
                        members.add(user.replace('/', ''))
            j += 1
        members = list(members)
        return members
