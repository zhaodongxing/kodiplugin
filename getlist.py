#!/usr/bin/env python
#encoding=utf-8

import requests
from lxml import etree
import re
import json
import commands
from urlparse import urlparse,parse_qs
import urllib
import sys

headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'}

def html_page(url,payload=None):
    r = requests.get(url,headers=headers,params=payload)
    if r.status_code != 200:
        raise "%s get page error"%url 
    return r.content

def get_movie_list(url,payload):
    r = html_page(url,payload)
    tree = etree.HTML(r) 
    xlist = tree.xpath('//li[@class="list_item"]')
    mlist = {}
    pattern = re.compile(r'href="(.*html)"\s*class="figure"')
    for xm in xlist:
        mov     = str(xm.xpath('.//strong[@class="figure_title"]/a/@title')[0])
        mov_url = pattern.search(etree.tostring(xm)).group(1)
        mlist[mov] = mov_url
    return mlist

def get_children_serial(url):
    r = html_page(url)
    tree = etree.HTML(r)
    xlist = tree.xpath('//div[@class="player_side_bd"]')[0]
    xlist = xlist.xpath('//div[@id="video_scroll_wrap"]/div')
    spans = xlist[1].xpath('./span')
    eps =[]
    for span in spans:
        pattern =  re.compile(r'href="(.*)\s*.*title="(.*)">')
        match = pattern.search(etree.tostring(span,encoding='utf8'))
        surl='https://v.qq.com' + match.group(1)
        title=match.group(2)
        eps.append((title,surl))
    return eps

def get_tv_serial(url):
    r = html_page(url)
    tree = etree.HTML(r)
    xlist = tree.xpath('//div[@class="player_side_bd"]')[0]
    xlist = xlist.xpath('//div[@id="video_scroll_wrap"]/div')
    spans = xlist[1].xpath('./span')
    eps =[]
    for span in spans:
        pattern =  re.compile(r'href="(.*)\s*.*title="(.*)">')
        match = pattern.search(etree.tostring(span,encoding='utf8'))
        surl='https://v.qq.com' + match.group(1)
        title=match.group(2)
        eps.append((title,surl))
    return eps

def get_variety_serial(url):
    r = html_page(url)
    tree = etree.HTML(r)
    xlist = tree.xpath('//div[@class="player_side_bd"]')[0]
    xlist = xlist.xpath('//ul[@class="figures_list _column_list"]/li')
    eps =[]
    for li in xlist:
        pattern =  re.compile(r'href="(.*)\s*.*title="(.*)"\s*class')
        match = pattern.search(etree.tostring(li,encoding='utf8'))
        surl='https://v.qq.com' + match.group(1)
        title=match.group(2)
        eps.append((title,surl))
    return eps


class Tencent:
    def __init__(self,url):
        self.url = url
        self.vid = self.get_vid()
        self.index = 1
        self.url_prefix = ''
        
    def get_vid(self):
        r = html_page(self.url)
        pattern =  re.compile(r'vid"\s*:\s*"\s*([^"]+)"')
        match = pattern.search(r)
        if match == None:
            raise "vid is None"
        return match.group(1)
    
    def get_info(self):
        api = 'http://vv.video.qq.com/getinfo?otype=json&appver=3%2E2%2E19%2E333&platform=11&defnpayver=1&vid='+self.vid
        info = html_page(api)
        video_json = json.loads(info[len('QZOutputJson='):-1])
        self.ti = video_json['vl']['vi'][0]['ti']
        self.lnk = video_json['vl']['vi'][0]['lnk']
        self.idx = iter((i for i in range(1,video_json['vl']['vi'][0]['cl']['fc'] + 1)))
        self.url_prefix = video_json['vl']['vi'][0]['ul']['ui'][0]['url']
        self.url_prefix = urlparse(self.url_prefix)._replace(netloc='lmbsy.qq.com').geturl()  # fast

        parts_formats = video_json['fl']['fi']
        self.quality = ''
        for part_format in parts_formats:
            self.format_id = part_format['id']
            self.format_sl = part_format['sl']
            self.quality = part_format['name']
            '''
            print part_format['name']
            if part_format['name'] == 'fhd':
                self.format_id = part_format['id']
                self.format_sl = part_format['sl']
                self.quality = 'fhd'
                break
            elif part_format['name'] == 'shd':
                self.format_id = part_format['id']
                self.format_sl = part_format['sl']
                self.quality = 'shd'
            '''

    def format_vurl(self):
        return '{prefix}/{filename}?vkey={key}'.format(prefix=self.url_prefix,filename=self.filename,key=self.vkey)

    def get_v_url(self):
        idx= self.idx.next()
        status,info_url=commands.getstatusoutput('python3 %s/vkey.py %s %d %s %s'%(sys.path[0],self.vid,self.format_id,idx,self.lnk))
        self.filename = parse_qs(info_url.split('?')[1])['filename'][0]
        r = html_page(info_url)
        ijson = json.loads(r[len('QZOutputJson='):-1])
        if 'key' in ijson:
            self.vkey = ijson['key']
        else:
            raise StopIteration
        return self.format_vurl() 

def getMlist(mov):
    qq = Tencent(mov)
    qq.get_info()
    mlist=[]
    try:
        while True:
            mlist.append(qq.get_v_url())
    except StopIteration:
        pass
    return mlist


if __name__ == '__main__':
    getMlist('https://v.qq.com/x/cover/arsauzhxjbnw8pk.html')

   


