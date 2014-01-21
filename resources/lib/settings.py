import sys
from resources.lib import common

generalVideonum = common.addon.getSetting('general videonum')
generalMuppetPictures = common.addon.getSetting('general muppetpictures') == 'true'
generalDebug = common.addon.getSetting('general debug') == 'true'
filterAgegroup = common.addon.getSetting('filter agegroup')

# set during runtime, not by the user
sessionCookie = common.addon.getSetting('cookie')

def get(id):
  return common.addon.getSetting(id)

def set(id, value):
  common.addon.setSetting(id, value)
