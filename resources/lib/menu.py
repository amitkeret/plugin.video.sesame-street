import xbmc, xbmcgui, xbmcplugin
from resources.lib import common, settings, utils

def addFolderItem(title, query={}, icon='DefaultFolder.png', thumb='DefaultFolder.png'):
  li = xbmcgui.ListItem(title, icon, thumb)
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=utils.build_url(query), listitem=li, isFolder=True)

def addVideoItem(video, original_video_data):
  li = xbmcgui.ListItem(video['title'])
  li.setInfo('video', {
    'count': video['uid'],
#    'playcount': getplaycountfrom...()
    'cast': video['cast'],
    'plot': video['description'],
    'plotoutline': video['description'],
    'title': video['title'],
    'originaltitle': video['title'],
    'sorttitle': video['title'],
    'tvshowtitle': common.tvshow_title,
    'code': common.tvshow_imdb
  })
  li.addStreamInfo('video', {
    'codec': video['file']['codec'],
    'aspect': round(video['width'] / video['height'], 2),
    'width': video['width'],
    'height': video['height']
  })
  li.setIconImage(video['images']['small'])
  li.setThumbnailImage(video['images']['medium'])
  li.setProperty('fanart_image', video['images']['large'])
  xbmcplugin.addDirectoryItem(handle=common.addon_handle, url=video['file']['url'], listitem=li)

def moreVideosBtn(args={}):
  if 'pagenum' in args:
    pagenum = int(args['pagenum']) + 1
  else:
    pagenum = 0
  # we want another batch of results, not the same ones again...
  if 'reset' in args:
    del args['reset']
  args.update({'page':'list_vids','pagenum':pagenum})
  utils.log(args)
  addFolderItem(common.l(30201), args)
