# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
'''
Created on 12 August 2014

@author: Seko
@summary: Kodi Util library
'''
#---------------------------------------------------------------------

# ____________________        I M P O R T        ____________________
import urllib
import xbmcplugin
import xbmc
import sys
# ____________________     V A R I A B L E S     ____________________

# Get base_url, add_handle and arguments
__base_url__ = sys.argv[0]
__handle__ = None
if len(sys.argv) > 1:
    __handle__ = int(sys.argv[1]) 


# Get the kodi major version
if not sys.argv[0].endswith('test.py'):
    __kodiVersion__ =xbmc.getInfoLabel('System.BuildVersion')[0:2]
else:
    __kodiVersion__ = '17'
# ____________________       M E T H O D S       ____________________
def build_url(query):
    """
        Method to build an url
        @param url: the url to pass to the addon url
    """
    return __base_url__ + '?' + urllib.urlencode(query)


def addDirectoryItem(url, listItem, isFolder):
    """
        Method to add an item to current directory
        @param url: the item url
        @param listItem: the list item
        @param isFolder: boolean which indicates if the item is a folder or not
    """
    xbmcplugin.addDirectoryItem(handle=__handle__, 
                                url=url,
                                listitem=listItem, 
                                isFolder=isFolder)
    
def endOfDirectory(isCached=True):
    """"
        Method to declare the end of the directory
    """
    xbmcplugin.endOfDirectory(__handle__,cacheToDisc=isCached)    
    
def beginContentDirectory(content='addons'):
    """
        Method to begin the content of a directory
    """
    if int(__kodiVersion__) < 17:        
        xbmcplugin.setContent(__handle__, 'folder')
    else:
        xbmcplugin.setContent(__handle__, content)
    
    