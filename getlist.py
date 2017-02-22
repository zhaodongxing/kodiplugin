#!/usr/bin/env python
#encoding=utf-8

import requests
from lxml import etree
import re
import json

headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'}

def html_page(url,payload):
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

def get_vid(url,payload):
    r = html_page(url,payload)
    pattern =  re.compile(r'vid"\s*:\s*"\s*([^"]+)"')
    match = pattern.search(r)
    if match == None:
        raise "vid is None"
    vid = match.group(1)
    return vid 

def get_info(vid):
    info_api = 'http://vv.video.qq.com/getinfo?otype=json&appver=3%2E2%2E19%2E333&platform=11&defnpayver=1&vid=' + vid
    info=html_page(info_api,None)
    print info
    video_json = json.loads(info[len('QZOutputJson='):-1])
    parts_vid = video_json['vl']['vi'][0]['vid']
    parts_ti = video_json['vl']['vi'][0]['ti']
    parts_prefix = video_json['vl']['vi'][0]['ul']['ui'][0]['url']
    parts_formats = video_json['fl']['fi']

    best_quality = ''
    for part_format in parts_formats:
        if part_format['name'] == 'fhd':
            best_quality = 'fhd'
            break

        if part_format['name'] == 'shd':
            best_quality = 'shd'


    for part_format in parts_formats:
        if not part_format['name'] == best_quality:
            continue
        part_format_id = part_format['id']
        part_format_sl = part_format['sl']

        part_urls= []
        total_size = 0
        try:
            for part in range(1,100):
                filename = vid + '.p' + str(part_format_id % 1000) + '.' + str(part) + '.mp4'
                key_api = "http://vv.video.qq.com/getkey?otype=json&platform=11&format=%s&vid=%s&filename=%s" % (part_format_id, parts_vid, filename)
                key_info = html_page(key_api,None)
                key_json = json.loads(key_info[len('QZOutputJson='):-1])
                vkey = key_json['key']
                url = '%s/%s?vkey=%s' % (parts_prefix, filename, vkey)
                part_urls.append(url)
        except:
            pass
        return part_urls



def getMlist(url):
    vid = get_vid(url,None)    
    return get_info(vid)


