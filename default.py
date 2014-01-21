import sys, re
import urllib, urllib2, urlparse
import json
import xbmcgui
import xbmcplugin

from BeautifulSoup import BeautifulSoup as bsoup

from resources.lib import common, settings, utils, session

xbmcplugin.setContent(common.addon_handle, 'movies')

def fetch_vids(filters={}, reset=False):
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
  headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Cookie': session.getCookie()}
  req = urllib2.Request(common.sesame_base_url + '/c/portal/json_service', urllib.urlencode(post_data), headers)
  res = urllib2.urlopen(req)
  session.parseCookieHeaders(res)
  data = json.load(res)
  if len(data['content']) == 0:
    return False
  return data['content']

def list_vids(videos):
  for video in videos:
    if len(video['source']) == 0:
      continue
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
  lis = bsoup(html).find('select', {'class':re.compile("filter-topic")}).findAll('option')
  
  for item in lis:
    if item['value'] == '':
      continue
    li = xbmcgui.ListItem(item.string, iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'list_vids','reset':1,'topic':int(item['value'])}), listitem=li, isFolder=True)
    
elif page == 'recent':
  videos = fetch_vids(reset=True)
  list_vids(videos)
  utils.moreVideosBtn()

elif page == 'muppets':
  # get JSON-formatted names
  html = utils.getHTML('ump-portlet/js/sw/sw.ump.js')
  match = re.findall("muppets\s+:\s+\[([\s\"a-zA-Z\|\,]+)\]", html)
  match = re.findall("\"([a-zA-Z\s\|]+)\"", match[0])
  muppets = {}
  for matchi in match:
    muppets.update({matchi.split('|')[0]: {'json-name': matchi.split('|')[1]}})
  
  # get pretty names and pictures
  if settings.generalMuppetPictures == 'true':
    html = utils.getHTML('muppets', True)
    lis = bsoup(html).find('ul', {'id':'muppet-slideshow'}).findAll('li', {'class':re.compile("section")})
    for item in lis:
      m_name = item.a['href'][item.a['href'].index('/muppets/') + len('/muppets/'):]
      m_name_pretty = ' '.join(m_name.split('-')).title()
      for k,muppet in muppets.items():
        if re.search(muppet['json-name'], m_name_pretty) != None:
          muppets[k].update({'pretty-name': m_name_pretty, 'image-src': item.a.img['src']})
          break;
  
  for k,muppet in muppets.items():
    li = xbmcgui.ListItem(muppet.get('pretty-name', muppet['json-name']), iconImage=muppet.get('image-src', ''), thumbnailImage=muppet.get('image-src', ''))
    xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'list_vids','reset':1,'muppet':muppet['json-name']}), listitem=li, isFolder=True)
    
elif page == 'list_vids':
  utils.log(common.args)
  filters = {}
  if common.args.get('muppet'):
    filters['muppet'] = common.args['muppet']
  if common.args.get('topic'):
    filters['topic'] = int(common.args['topic'])
  
  videos = fetch_vids(filters, bool(int(common.args.get('reset', 0))))
  if videos==False:
    ok = False
    xbmcgui.Dialog().ok(common.addon_name, 'No videos were found.')
  else:
    list_vids(videos)
    utils.moreVideosBtn(common.args)
  
else:
  li = xbmcgui.ListItem('Recent videos', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'recent'}), listitem=li, isFolder=True)
  li = xbmcgui.ListItem('Muppets', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'muppets'}), listitem=li, isFolder=True)
  li = xbmcgui.ListItem('Topics', iconImage='DefaultFolder.png', thumbnailImage='DefaultFolder.png')
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url({'page':'topics'}), listitem=li, isFolder=True)


if ok:
  xbmcplugin.endOfDirectory(common.addon_handle)
