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
import re

class Pyvk:

    FRIENDS_URL = 'al_friends.php'
    GROUPS_URL = 'al_groups.php'
    CLUBS_URL = 'al_fans.php'
    AUDIOS_URL = 'audio'
    PHOTOS_URL = 'al_photos.php'
    PAGE_URL = 'al_page.php'
    SEARCH_URL = 'al_search.php'

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.login_url = 'https://login.vk.com'
        self.vk_url = 'https://vk.com'
        self.mobile_vk_url = 'http://m.vk.com'

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
            friends_data = self.post_request(self.FRIENDS_URL, data)
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
            groups_data = self.post_request(self.GROUPS_URL, data)
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
        friends_data = self.post_request(self.FRIENDS_URL, data)
        start = friends_data.find('all')
        end = friends_data.find(']]}') + 2
        final = friends_data[start:end].replace('all":', '').strip()
        final = unicode(final, 'cp1251')
        friends_list = ast.literal_eval(final)
        for f in friends_list:
            # friends.append('id' + f[0])
            image = f[1]
            if 'camera' in f[1] or 'deactivated' in f[1]:
                image = self.vk_url + f[1]

            current = {
                'id' : f[0],
                'image' : image,
                'link' : self.vk_url + "/id" + f[0],
                'label' : f[5],
            }
            friends.append(current)
        return friends

    # get user's groups
    def get_groups(self, user_id):
        groups = []
        try:
            data = {
                'act' : 'load_idols',
                'al' : '1',
                'oid' : str(user_id),
            }

            groups_data = self.post_request(self.CLUBS_URL, data)
            if groups_data:
                start = groups_data.find('[[')
                final = groups_data[start:].replace('[[', '').replace(']]', '').strip()
                final = unicode(final, "cp1251")
                for g in final.split("],["):
                    g = '[' + g + ']'
                    g = g.replace('false', '0').replace('true', '1')

                    group_param_list = ast.literal_eval(g)

                    image = group_param_list[3]
                    if 'camera' in group_param_list[3] or 'deactivated' in group_param_list[3]:
                        image = self.vk_url + group_param_list[3]

                    current = {
                        'id' : re.sub("[^0-9]", "", str(group_param_list[0])),
                        'label' : group_param_list[2],
                        'image' : image,
                        'link' : self.vk_url + '/club' + str(re.sub("[^0-9]", "", str(group_param_list[0]))),
                    }

                    groups.append(current)
        except Exception, e:
            print e
        return groups

    # get user's audios
    def get_audios(self, user_id):
        audios = []
        data = {
            'act' : 'load_audios_silent',
            'al' : '1',
            'id' : user_id,
            'please_dont_ddos':'1',
        }
        audios_data = self.post_request(self.AUDIOS_URL, data)
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

    # download user's photo
    def download_photo(self, user_id):
        data = {
            'act' : 'fast_get_photo',
            'al' : '1',
            'oid' : user_id,
        }
        photo_data = self.post_request(self.PHOTOS_URL, data)
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
            print "Cannot download user's photo"
            print e

    # get user's photo link
    def get_photo_link(self, user_id):
        data = {
            'act' : 'fast_get_photo',
            'al' : '1',
            'oid' : user_id,
        }
        photo_data = self.post_request(self.PHOTOS_URL, data)
        start = photo_data.find('_id') - 2
        end = photo_data.find('}}') + 2
        try:
            final = json.loads(photo_data[start:end].strip())
            img_link = final.get('temp').get('base') + final.get('temp').get('z_')[0] + '.jpg'
            return img_link
        except Exception, e:
            print "Cannot get user's photo"
            print e
        return None

    # parse photo link from account page
    def parse_photo_link_from_page(self, user_id):
        page = self.get_page(self.vk_url + "/id%s" % user_id)
        if page:
            try:
                tree = lxml.html.fromstring(page)
                images = tree.xpath('.//img[@class="pp_img"]/@src')
                if images:
                    return images[0]
            except Exception, e:
                print e
        return None

    def clean_key(self, key):
        key = key.strip()
        cl = [".", "(", ")", ",", "@", " ", ".."]
        for c in cl:
            key = key.replace(c, "_")
        return key


    # get account name with photo
    def get_account_name(self, user_id):
        url = self.mobile_vk_url + "/id%s?act=info" % user_id
        info = {}
        page = self.get_page(url)
        if page:
            try:
                tree = lxml.html.fromstring(page)
                image = tree.xpath('.//img[@class="op_img"]/@src')
                pp_image = tree.xpath('.//img[@class="pp_img"]/@src')

                # account main image (from mobile version)
                if image:
                    info['image'] = image[0]
                elif pp_image:
                    info['image'] = pp_image[0]

                name = tree.xpath('.//div[@class="op_cont"]//h2[@class="op_header"]')
                pp_name = tree.xpath('.//div[@class="pp_cont"]//h2[@class="op_header"]')
                
                # account name in header
                if name:
                    info['name'] = name[0].text
                elif pp_name:
                    info['name'] = pp_name[0].text
            except Exception, e:
                print e
        return info

    # get group name with photo
    def get_group_name(self, group_id):
        url = self.mobile_vk_url + "/club%s" % group_id
        info = {}
        page = self.get_page(url)
        if page:
            try:
                tree = lxml.html.fromstring(page)
                image = tree.xpath('.//img[@class="op_img"]/@src')
                pp_image = tree.xpath('.//img[@class="pp_img"]/@src')

                # account main image (from mobile version)
                if image:
                    info['image'] = image[0]
                elif pp_image:
                    info['image'] = pp_image[0]

                name = tree.xpath('.//div[@class="op_cont"]//h2[@class="op_header"]')
                pp_name = tree.xpath('.//div[@class="pp_cont"]//h2[@class="op_header"]')
                
                # account name in header
                if name:
                    info['name'] = name[0].text
                elif pp_name:
                    info['name'] = pp_name[0].text
            except Exception, e:
                print e
        return info

    # parse account page
    def parse_account_page(self, user_id):
        url = self.mobile_vk_url + "/id%s?act=info" % user_id
        info = {}
        page = self.get_page(url)
        if page:
            try:
                tree = lxml.html.fromstring(page)
                image = tree.xpath('.//img[@class="op_img"]/@src')
                pp_image = tree.xpath('.//img[@class="pp_img"]/@src')

                # account main image (from mobile version)
                if image:
                    info['image'] = image[0]
                elif pp_image:
                    info['image'] = pp_image[0]

                name = tree.xpath('.//div[@class="op_cont"]//h2[@class="op_header"]')
                pp_name = tree.xpath('.//div[@class="pp_cont"]//h2[@class="op_header"]')

                # account name in header
                if name:
                    info['name'] = name[0].text
                elif pp_name:
                    info['name'] = pp_name[0].text


                # main info in profile
                p_info = tree.xpath('.//dl[@class="pinfo_row"]')
                if p_info:
                    last_key = None
                    for p in p_info:
                        elems = [k for k in p.iter() if k.text]
                        for elem in elems:
                            if elem.tag == 'dt':
                                info[elem.text] = ""
                                last_key = elem.text
                            else:
                                info[last_key] += elem.text + ","

                for l in tree.xpath('.//a[@class="button wide_button al_back"]'):
                    l.getparent().remove(l)

                p_info = tree.xpath('.//div[@class="profile_info"]')
                if p_info:
                    last_key = None
                    for p in p_info:
                        elems = [k for k in p.iter() if k.text]
                        for elem in elems:
                            if elem.tag == 'dt':
                                info[elem.text] = ""
                                last_key = elem.text
                            elif elem.tag != 'h4':
                                info[last_key] += elem.text + ","

                info = {self.clean_key(k) : v.strip(',') for k,v in info.iteritems()}

                # phones
                phones = []
                phones_text = tree.xpath('.//a[@class="si_phone"]')
                if phones_text:
                    for num in phones_text:
                        phones.append(re.sub("[^0-9]", "", num.text))

                info['phones'] = phones

            except Exception, e:
                print e
        return info

    # parse group page
    def parse_group_page(self, group_id):
        url = self.mobile_vk_url + "/club%s" % group_id
        info = {}
        page = self.get_page(url)
        if page:
            try:
                tree = lxml.html.fromstring(page)
                image = tree.xpath('.//img[@class="op_img"]/@src')
                pp_image = tree.xpath('.//img[@class="pp_img"]/@src')

                # account main image (from mobile version)
                if image:
                    info['image'] = image[0]
                elif pp_image:
                    info['image'] = pp_image[0]

                name = tree.xpath('.//div[@class="op_cont"]//h2[@class="op_header"]')
                pp_name = tree.xpath('.//div[@class="pp_cont"]//h2[@class="op_header"]')

                # account name in header
                if name:
                    info['name'] = name[0].text
                elif pp_name:
                    info['name'] = pp_name[0].text


                # main info in profile
                p_info = tree.xpath('.//dl[@class="pinfo_row"]')
                if p_info:
                    last_key = None
                    for p in p_info:
                        elems = [k for k in p.iter() if k.text]
                        for elem in elems:
                            if elem.tag == 'dt':
                                info[elem.text] = ""
                                last_key = elem.text
                            else:
                                info[last_key] += elem.text + ","

                for l in tree.xpath('.//a[@class="button wide_button al_back"]'):
                    l.getparent().remove(l)

                p_info = tree.xpath('.//div[@class="profile_info"]')
                if p_info:
                    last_key = None
                    for p in p_info:
                        elems = [k for k in p.iter() if k.text]
                        for elem in elems:
                            if elem.tag == 'dt':
                                info[elem.text] = ""
                                last_key = elem.text
                            elif elem.tag != 'h4':
                                info[last_key] += elem.text + ","

                pm_item_titles = tree.xpath('.//a[@class="pm_item"]')
                pm_item_values = tree.xpath('.//a[@class="pm_item"]//em[@class="pm_counter"]')
                if pm_item_titles and pm_item_values:
                    for i in range(0, len(pm_item_titles)):
                        info[pm_item_titles[i].text] = re.sub("[^0-9]", "", pm_item_values[i].text)

                info = {self.clean_key(k) : v.strip(',') for k,v in info.iteritems()}

                # phones
                phones = []
                phones_text = tree.xpath('.//a[@class="si_phone"]')
                if phones_text:
                    for num in phones_text:
                        phones.append(re.sub("[^0-9]", "", num.text))

                info['phones'] = phones

            except Exception, e:
                print e
        return info

    # get group members
    def get_group_members(self, group_id):
        # members = set()
        members = []
        j = 0
        data = {
            'act' : 'box',
            'al' : '1',
            'oid' : '-' + group_id,
            'tab' : 'members',
        }
        members_data = self.post_request(self.PAGE_URL, data)
        members_count_str = members_data[members_data.find('<span class="fans_count">'):members_data.find('</span></nobr>')]
        # count = members_count_str.replace('<span class="fans_count">', '').replace('<span class="num_delim">', '').replace('</span>', '').replace(' ', '')
        # c = int(count)/60
        count = re.sub("[^0-9]", "", members_count_str)
        c = int(count)/60 if int(count) < 240 else 4
        while j < c+1:
            if j == 0:
                members_data = self.post_request(self.PAGE_URL, data)
                if members_data:
                    start = members_data.find('div class="fans_rows"') - 1
                    end = members_data.find('a class="fans_more_link"') - 1
                    final = members_data[start:end]
                    final = unicode(final, 'cp1251')
                    tree = lxml.html.fromstring(final)
                    # user_ids = tree.xpath('.//a[@class="fans_fan_ph"]/@href')
                    user_ids = tree.xpath('.//div[@class="fans_fanph_wrap"]/@onmouseover')
                    images = tree.xpath('.//img[@class="fans_fan_img"]/@src')
                    labels = tree.xpath('.//div[@class="fans_fan_name"]//a')
                    # for user in user_ids:
                    #     members.add(user.replace('/', ''))
                    for i in range(0, len(user_ids)):
                        user_id = re.sub("[^0-9]", "", user_ids[i])
                        image = images[i]
                        if 'camera' in images[i] or 'deactivated' in images[i]:
                            image = self.vk_url + images[i]
                        current = {
                            'id' : user_id,
                            'link' : self.vk_url + "/id" + str(user_id),
                            'image' : image,
                            'label' : labels[i].text,
                        }
                        members.append(current)
            else:
                data['offset'] = j * 60
                members_data = self.post_request(self.PAGE_URL, data)
                if members_data:
                    start = members_data.find('div class="fans_fan_row inl_bl"') - 1
                    end = members_data.find('<!><!int>')
                    final = members_data[start:end]
                    final = unicode(final, 'cp1251')
                    tree = lxml.html.fromstring(final)
                    # user_ids = tree.xpath('.//a[@class="fans_fan_ph"]/@href')
                    # for user in user_ids:
                    #     members.add(user.replace('/', ''))
                    user_ids = tree.xpath('.//div[@class="fans_fanph_wrap"]/@onmouseover')
                    images = tree.xpath('.//img[@class="fans_fan_img"]/@src')
                    labels = tree.xpath('.//div[@class="fans_fan_name"]//a')
                    # for user in user_ids:
                    #     members.add(user.replace('/', ''))
                    for i in range(0, len(user_ids)):
                        user_id = re.sub("[^0-9]", "", user_ids[i])
                        image = images[i]
                        if 'camera' in images[i] or 'deactivated' in images[i]:
                            image = self.vk_url + images[i]
                        current = {
                            'id' : user_id,
                            'link' : self.vk_url + "/id" + str(user_id),
                            'image' : image,
                            'label' : labels[i].text,
                        }
                        members.append(current)
            j += 1
        # members = list(members)
        return members

    # simple people search
    def people_search(self, query):
        peoples = []
        j = 0
        data = {
            'al' : '1',
            'c[name]' : '1',
            'c[photo]' : '1',
            'c[q]' : query,
            'c[section]' : 'people',
            'change' : '1',
        }
        peoples_data = self.post_request(self.SEARCH_URL, data)
        try:
            f = peoples_data.find('"summary":"') + 11
            t = peoples_data.find('","auto_rows"')
            peoples_count_str = peoples_data[f:t].strip()
            count = re.sub("[^0-9]", "", peoples_count_str)
            c = int(count)/40 if int(count) < 200 else 5
            while j < c+1:
                if j == 0:
                    peoples_data = self.post_request(self.SEARCH_URL, data)
                    if peoples_data:
                        try:
                            start = peoples_data.find('<div class="people_row three_col_row clear_fix">')
                            end = peoples_data.find('<div id="show_more">')
                            final = peoples_data[start:end]
                            final = unicode(final, 'cp1251')
                            tree = lxml.html.fromstring(final)
                            user_ids = tree.xpath('.//div[@class="img search_bigph_wrap fl_l"]/@onmouseover')
                            images = tree.xpath('.//img[@class="search_item_img"]/@src')
                            labels = tree.xpath('.//div[@class="labeled name"]//a')
                            for i in range(0, len(user_ids)):
                                user_id = re.sub("[^0-9]", "", user_ids[i])
                                current = {
                                    'id' : user_id,
                                    'link' : self.vk_url + "/id" + str(user_id),
                                    'image' : images[i],
                                    'label' : labels[i].text,
                                }
                                peoples.append(current)
                                # peoples.add(re.sub("[^0-9]", "", user))
                        except Exception, e:
                            print e
                else:
                    data['offset'] = j * 40
                    peoples_data = self.post_request(self.SEARCH_URL, data)
                    if peoples_data:
                        try:
                            start = peoples_data.find('<div class="people_row three_col_row clear_fix">')
                            final = peoples_data[start:]
                            final = unicode(final, 'cp1251')
                            tree = lxml.html.fromstring(final)

                            user_ids = tree.xpath('.//div[@class="img search_bigph_wrap fl_l"]/@onmouseover')
                            images = tree.xpath('.//img[@class="search_item_img"]/@src')
                            for i in range(0, len(user_ids)):
                                user_id = re.sub("[^0-9]", "", user_ids[i])
                                current = {
                                    'id' : user_id,
                                    'link' : self.vk_url + "/id" + str(user_id),
                                    'image' : images[i],
                                    'label' : labels[i].text
                                }
                                peoples.append(current)
                        except Exception, e:
                            print e
                j += 1
        except Exception, e:
            print e
        return peoples

    # simple group search
    def group_search(self, query):
        groups = []
        j = 0
        data = {
            'al' : '1',
            'c[q]' : query,
            'c[section]' : 'communities',
            'change' : '1',
            'future' : '1',
        }
        groups_data = self.post_request(self.SEARCH_URL, data)
        try:
            f = groups_data.find('"summary":"') + 11
            t = groups_data.find('","auto_rows"')
            groups_count_str = groups_data[f:t].strip()
            count = re.sub("[^0-9]", "", groups_count_str)
            c = int(count)/20 if int(count) < 100 else 5
            while j < c+1:
                if j == 0:
                    groups_data = self.post_request(self.SEARCH_URL, data)
                    if groups_data:
                        try:
                            start = groups_data.find('<div class="groups_row three_col_row clear_fix">')
                            end = groups_data.find('<div id="show_more">')
                            final = groups_data[start:end]
                            final = unicode(final, 'cp1251')
                            tree = lxml.html.fromstring(final)
                            group_ids = tree.xpath('.//button[@class="flat_button secondary search_sub"]/@id')
                            images = tree.xpath('.//img[@class="search_item_img"]/@src')
                            labels = tree.xpath('.//div[@class="labeled title"]//a')
                            for i in range(0, len(group_ids)):
                                group_id = re.sub("[^0-9]", "", group_ids[i])
                                if 'community' in images[i]:
                                    images[i] = self.vk_url + images[i]
                                current = {
                                    'id' : group_id,
                                    'link' : self.vk_url + "/club" + str(group_id),
                                    'image' : images[i],
                                    'label' : labels[i].text_content(),
                                }
                                groups.append(current)
                        except Exception, e:
                            print e
                else:
                    data['offset'] = j * 20
                    groups_data = self.post_request(self.SEARCH_URL, data)
                    if groups_data:
                        try:
                            start = groups_data.find('<div class="groups_row three_col_row clear_fix">')
                            end = groups_data.find('<div id="show_more">')
                            final = groups_data[start:end]
                            final = unicode(final, 'cp1251')
                            tree = lxml.html.fromstring(final)
                            group_ids = tree.xpath('.//button[@class="flat_button secondary search_sub"]/@id')
                            images = tree.xpath('.//img[@class="search_item_img"]/@src')
                            labels = tree.xpath('.//div[@class="labeled title"]//a')
                            for i in range(0, len(group_ids)):
                                group_id = re.sub("[^0-9]", "", group_ids[i])
                                if 'community' in images[i]:
                                    images[i] = self.vk_url + images[i]
                                current = {
                                    'id' : group_id,
                                    'link' : self.vk_url + "/club" + str(group_id),
                                    'image' : images[i],
                                    'label' : labels[i].text_content(),
                                }
                                groups.append(current)
                        except Exception, e:
                            print e
                j += 1
        except Exception, e:
            print e
        return groups