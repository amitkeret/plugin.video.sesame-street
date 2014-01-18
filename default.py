import sys
import urllib, urllib2, urlparse
import json
import xbmcgui
import xbmcplugin

from BeautifulSoup import BeautifulSoup as bsoup

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

sesame_base_domain = 'sesamestreet.org'
sesame_base_url = 'http://www.' + sesame_base_domain
sesame_m_base_url = 'http://m.' + sesame_base_domain

videoNum = 25

xbmcplugin.setContent(addon_handle, 'movies')

def log(txt):
  if isinstance (txt, str):
    txt = txt.decode("utf-8")
  message = u'%s: %s' % ('SESAMESTREET', txt)
  xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def build_url(query):
  return base_url + '?' + urllib.urlencode(query)


def getHTML(uri, mobile=False):
  if (mobile == True):
    url = sesame_m_base_url + '/' + uri
  else:
    url = sesame_base_url + '/' + uri
  
  html = urllib.urlopen(url)
  return html.read()

def fetch_vids(filter={}, reset=True):
  post_data = {
    'serviceClassName': 'org.sesameworkshop.service.UmpServiceUtil',
    'serviceMethodName': 'getMediaItems',
    'serviceParameters': ["criteria","capabilities","resultsBiasingPolicy","context"],
    'criteria': {
      "qty": videoNum,
      "reset": reset,
      "type": "video"
    },
    'capabilities': {},
    'resultsBiasingPolicy': '',
    'context': {}
  }
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  req = urllib2.Request(sesame_base_url + '/c/portal/json_service', urllib.urlencode(post_data), headers)
  data = json.load(urllib2.urlopen(req))
  return data['content']

page = args.get('page', None)
if (page):
  page = page[0]

if page == 'topics':
  pass

elif page == 'recent':
  videos = fetch_vids()
  for video in videos:
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

elif page == 'muppets':
  html = getHTML('muppets', True)
  lis = bsoup(html).find('ul', {'id':'muppet-slideshow'}).findAll('li', {'class':'section'})
  
  for item in lis:
    log(item.a.img['src'])
    
    m_name = item.a['href'][item.a['href'].index('/muppets/') + len('/muppets/'):]
    m_name_pretty = ' '.join(m_name.split('-')).title()
    
    li = xbmcgui.ListItem(m_name_pretty)
    li.setIconImage(item.a.img['src'])
    li.setThumbnailImage(item.a.img['src'])
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='test', listitem=li)
    
else:
  li = xbmcgui.ListItem('Recent videos', iconImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'page':'recent'}), listitem=li, isFolder=True)
  li = xbmcgui.ListItem('Muppets', iconImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=build_url({'page':'muppets'}), listitem=li, isFolder=True)


xbmcplugin.endOfDirectory(addon_handle)
