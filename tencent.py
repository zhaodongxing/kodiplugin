# -*- coding: utf-8 -*-

import xbmcplugin, xbmcgui, xbmcswift2
from getlist import get_movie_list,get_info,getMlist
import urllib
from urlparse import parse_qs

print sys.argv

handle=int(sys.argv[1])
addonUrl = sys.argv[0]

if sys.argv[2] == '':
    movie    = xbmcgui.ListItem('电影')
    tv = xbmcgui.ListItem('电视剧')
    cartoon = xbmcgui.ListItem('动画片')
    music  = xbmcgui.ListItem('音乐')
    xbmcplugin.addDirectoryItem(handle, addonUrl+'?type=movie&offset=0', movie, True)
    xbmcplugin.addDirectoryItem(handle, addonUrl+'?type=cartoon&offset=0', cartoon, True)
    xbmcplugin.addDirectoryItem(handle, addonUrl+'?type=tv&offset=0', tv, True)
    xbmcplugin.addDirectoryItem(handle, addonUrl+'?type=music&offset=0', music, True)
    xbmcplugin.endOfDirectory(handle)
else:
    query = parse_qs(urllib.sys.argv[2][1:])
    if 'path' in query:
        mlist = getMlist(urllib.unquote(query['path'][0]))
        program=xbmcgui.ListItem('play')
        plist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        plist.clear()
        if len(mlist) == 1:
            plist.add(mlist[0])
        else:
            plist.add('stack://' + ' , '.join(mlist))
        xbmc.Player().play(plist,program)
    else:
        offset = int(query['offset'][0])
        params={'offset':offset,'sort':5}
        vtype=query['type'][0]
        suburl='http://v.qq.com/x/list/%s'%vtype
        movs = get_movie_list(suburl,params) 
        for title,url in movs.iteritems():
            program=xbmcgui.ListItem(title)
            xbmcplugin.addDirectoryItem(handle, addonUrl+"?path="+url, program, True)
        nx=xbmcgui.ListItem('next')
        xbmcplugin.addDirectoryItem(handle, addonUrl+"?type=%s&offset=%d"%(vtype,offset+30), nx, True)
        if offset > 0:
            pre=xbmcgui.ListItem('previous')
            xbmcplugin.addDirectoryItem(handle, addonUrl+"?type=%s&offset=%d"%(vtype,offset-30), pre, True)
        xbmcplugin.endOfDirectory(handle)

