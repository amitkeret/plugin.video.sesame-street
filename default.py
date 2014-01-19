import sys
import urllib, urllib2, urlparse
import json
import xbmcgui
import xbmcplugin

from BeautifulSoup import BeautifulSoup as bsoup

import resources.lib.common as common
import resources.lib.settings as settings
import resources.lib.utils as utils

xbmcplugin.setContent(common.addon_handle, 'movies')

def fetch_vids(filters={}, reset=True):
  post_data = {
    'serviceClassName': 'org.sesameworkshop.service.UmpServiceUtil',
    'serviceMethodName': 'getMediaItems',
    'serviceParameters': ["criteria","capabilities","resultsBiasingPolicy","context"],
    'criteria': {
      "qty": settings.generalVideonum,
      "reset": reset,
      "type": "video",
      "filters": filters
    },
    'capabilities': {},
    'resultsBiasingPolicy': '',
    'context': {}
  }
  
  # check for age restriction
  if settings.filterAgegroup > 0:
    post_data['criteria']['filters']['age'] = settings.filterAgegroup
  
  utils.log(post_data)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  req = urllib2.Request(common.sesame_base_url + '/c/portal/json_service', urllib.urlencode(post_data), headers)
  data = json.load(urllib2.urlopen(req))
  if len(data['content']) == 0:
    return False
  return data['content']

def list_vids(videos):
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
    li.setIconImage(common.sesame_base_url + video['thumbnailSmall'])
    li.setThumbnailImage(common.sesame_base_url + video['thumbnailLarge'])
    li.addStreamInfo('video', {
      'codec': videoFile['codec'],
      'width': video['width'],
      'height': video['height'],
      'aspect': video['width'] / video['height']
    })
    li.setProperty('fanart_image', common.sesame_base_url + video['poster'])
    xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=url, listitem=li)

ok = True
page = common.args.get('page', None)
if page == 'topics':
  html = utils.getHTML('videos')
  lis = bsoup(html).find('select', {'class':'filter-topic filter'}).findAll('option')
  
  for item in lis:
    if item['value'] == '':
      continue
    li = xbmcgui.ListItem(item.string, iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'list_vids','topic':item['value']}), listitem=li, isFolder=True)
    
elif page == 'recent':
  videos = fetch_vids()
  list_vids(videos)

elif page == 'muppets':
  html = utils.getHTML('muppets', True)
  lis = bsoup(html).find('ul', {'id':'muppet-slideshow'}).findAll('li', {'class':'section'})
  
  for item in lis:
    m_name = item.a['href'][item.a['href'].index('/muppets/') + len('/muppets/'):]
    m_name_pretty = ' '.join(m_name.split('-')).title()
    
    li = xbmcgui.ListItem(m_name_pretty)
    li.setIconImage(item.a.img['src'])
    li.setThumbnailImage(item.a.img['src'])
    xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'list_vids','muppet':m_name_pretty}), listitem=li, isFolder=True)
    
elif page == 'list_vids':
#  utils.log(common.args)
  filters = {}
  try:
    if common.args['muppet']:
      filters['muppet'] = common.args['muppet']
  except:
    pass
  try:
    if common.args['topic']:
      filters['topic'] = int(common.args['topic'])
  except:
    pass
  videos = fetch_vids(filters)
  if videos==False:
    ok = False
    xbmcgui.Dialog().ok(common.addon_name, 'No videos were found.')
  else:
    list_vids(videos)
  
else:
  li = xbmcgui.ListItem('Recent videos', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'recent'}), listitem=li, isFolder=True)
  li = xbmcgui.ListItem('Muppets', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'muppets'}), listitem=li, isFolder=True)
  li = xbmcgui.ListItem('Topics', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'topics'}), listitem=li, isFolder=True)


if ok:
  xbmcplugin.endOfDirectory(common.addon_handle)
