import sys
import urllib, urllib2, urlparse
import json
import xbmcgui
import xbmcplugin

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

sesame_base_domain = 'sesamestreet.org'
sesame_base_url = 'http://www.' + sesame_base_domain

xbmcplugin.setContent(addon_handle, 'movies')

def log(txt):
  if isinstance (txt, str):
    txt = txt.decode("utf-8")
  message = u'%s: %s' % ('SESAMESTREET', txt)
  xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def build_url(query):
  return base_url + '?' + urllib.urlencode(query)

post_data = {
  'serviceClassName': 'org.sesameworkshop.service.UmpServiceUtil',
  'serviceMethodName': 'getMediaItems',
  'serviceParameters': ["criteria","capabilities","resultsBiasingPolicy","context"],
  'criteria': {
    "qty":25,
    "reset": True,
    "type": "video"
  },
  'capabilities': {},
  'resultsBiasingPolicy': '',
  'context': {}
}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
req = urllib2.Request(sesame_base_url + '/c/portal/json_service', urllib.urlencode(post_data), headers)
videos_data = json.load(urllib2.urlopen(req))

for video in videos_data['content']:
  if len(video['source']) == 0:
    pass
  
  videoFile = video['source'][0]
  url = videoFile['fileName']
  
  li = xbmcgui.ListItem(video['title'])
  li.setInfo('video', {
    'count': video['sesameItemId'],
    'codec': videoFile['codec'],
    'plot': video['description'],
    'plotoutline': video['description'],
    'cast': video['character'].split(';'),
  })
  li.setIconImage(sesame_base_url + video['thumbnailSmall'])
  li.setThumbnailImage(sesame_base_url + video['thumbnailLarge'])
  li.addStreamInfo('video', {
    'codec': videoFile['codec'],
    'width': video['width'],
    'height': video['height'],
    'aspect': video['width'] / video['height']
  })
  li.setProperty('fanart_image', sesame_base_url + video['poster'])
  
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)


xbmcplugin.endOfDirectory(addon_handle)
