# -*- coding: utf-8 -*-

import xbmcplugin, xbmcgui
from getlist import get_movie_list,getMlist,get_children_serial,get_tv_serial,get_variety_serial
import urllib
from urlparse import parse_qs
from xbmcswift2 import Plugin
import sys
import os

url_children='http://v.qq.com/x/list/children'
url_movie='http://v.qq.com/x/list/movie'
url_tv='http://v.qq.com/x/list/tv'
url_variety='http://v.qq.com/x/list/variety'

plugin = Plugin()
@plugin.route('/')
def index():
    item_list = [
                 {'label': u'电影'.encode('utf-8'),'path': plugin.url_for('show_movie',page=0)},
                 {'label': u'动画片'.encode('utf-8'),'path': plugin.url_for('show_children',page=0)},
                 {'label': u'电视剧'.encode('utf-8'),'path': plugin.url_for('show_tv',page=0)},
                 {'label': u'综艺'.encode('utf-8'),'path': plugin.url_for('show_variety',page=0)}
                ]
    return item_list

@plugin.route('/tv/<page>/')
def show_tv(page):
    item_list=[]
    page=int(page)
    params={'offset':page*30,'sort':4}

    movs=get_movie_list(url_tv,params) 
    for title,url in movs.iteritems():
        item_list.append({'label':title,'path':plugin.url_for('show_tv_serial',url=url)})
    item_list.append({'label':u'下一页'.encode('utf-8'),'path':plugin.url_for('show_tv',page=page+1)})
    if page > 0:
        item_list.append({'label':u'上一页'.encode('utf-8'),'path':plugin.url_for('show_tv',page=page-1)})
    return item_list

@plugin.route('/tv_serial/<url>/')
def show_tv_serial(url):
    sublists = get_tv_serial(url)
    item_list=[]
    for t,u in sublists:
        item_list.append({'label':t,'path':plugin.url_for('show_video',url=u),'is_playable':True})
    return item_list

@plugin.route('/variety/<page>/')
def show_variety(page):
    item_list=[]
    page=int(page)
    params={'offset':page*30,'sort':4}

    movs=get_movie_list(url_variety,params) 
    for title,url in movs.iteritems():
        item_list.append({'label':title,'path':plugin.url_for('show_variety_serial',url=url)})
    item_list.append({'label':u'下一页'.encode('utf-8'),'path':plugin.url_for('show_variety',page=page+1)})
    if page > 0:
        item_list.append({'label':u'上一页'.encode('utf-8'),'path':plugin.url_for('show_variety',page=page-1)})
    return item_list

@plugin.route('/variety_serial/<url>/')
def show_variety_serial(url):
    sublists = get_variety_serial(url)
    item_list=[]
    for t,u in sublists:
        item_list.append({'label':t,'path':plugin.url_for('show_video',url=u),'is_playable':True})
    return item_list

@plugin.route('/movie/<page>/')
def show_movie(page):
    item_list=[]
    page=int(page)
    params={'offset':page*30,'sort':4}
    movs=get_movie_list(url_movie,params) 
    for title,url in movs.iteritems():
        item_list.append({'label':title,'path':plugin.url_for('show_video',url=url),'is_playable':True})
    item_list.append({'label':u'下一页'.encode('utf-8'),'path':plugin.url_for('show_movie',page=page+1)})
    if page > 0:
        item_list.append({'label':u'上一页'.encode('utf-8'),'path':plugin.url_for('show_movie',page=page-1)})
    return item_list

@plugin.route('/children/<page>/')
def show_children(page):
    item_list=[]
    page=int(page)
    params={'offset':page*30,'sort':4}

    movs=get_movie_list(url_children,params) 
    for title,url in movs.iteritems():
        item_list.append({'label':title,'path':plugin.url_for('show_children_serial',url=url)})
    item_list.append({'label':u'下一页'.encode('utf-8'),'path':plugin.url_for('show_children',page=page+1)})
    if page > 0:
        item_list.append({'label':u'上一页'.encode('utf-8'),'path':plugin.url_for('show_children',page=page-1)})
    return item_list

@plugin.route('/children_serial/<url>/')
def show_children_serial(url):
    sublists = get_children_serial(url)
    item_list=[]
    for t,u in sublists:
        item_list.append({'label':t,'path':plugin.url_for('show_video',url=u),'is_playable':True})
    return item_list

@plugin.route('/play/<url>/')
def show_video(url):
    mlist = getMlist(urllib.unquote(url))
    print mlist
    if len(mlist) == 1:
        plugin.set_resolved_url(mlist[0])
    else:
        plugin.set_resolved_url('stack://' + ' , '.join(mlist))


if __name__ == '__main__':
    plugin.run()

