import urllib, urllib2
import json
import xbmc, xbmcgui, xbmcplugin

from resources.lib import common

def log(txt):
  if isinstance (txt, str):
    txt = txt.decode("utf-8")
  message = u'%s: %s' % ('SESAMESTREET', txt)
  xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)

def build_url(query):
  return common.base_url + '?' + urllib.urlencode(query)

def getHTML(uri, mobile=False):
  if mobile == True:
    url = common.sesame_m_base_url + '/' + uri
  else:
    url = common.sesame_base_url + '/' + uri
  html = urllib.urlopen(url)
  return html.read()
