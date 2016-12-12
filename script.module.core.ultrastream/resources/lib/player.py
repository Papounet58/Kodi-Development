# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
'''
Created on 12 December 2016

@author: Seko
@summary: Player functions

'''
#---------------------------------------------------------------------

# ____________________     I M P O R T       ____________________
import xbmc
import xbmcgui
import xbmcplugin
import sys
import time
import miscFunctions
import urlresolver
import webUtil
import constant
import history
from unshortenurl import UnshortenUrl
from item import StreamItem
from logger import Logger

# ____________________     V A R I A B L E S     ____________________

# __ Init addon variable & Logger
__LOGGER__ = Logger('UltraStream')

# ____________________     F U N C T I O N S       ____________________
def displayVideoOptions(streamItem):
    """
        Method to display video options
        @param streamItem: the selected StreamItem   
    """
    
    __LOGGER__.log("Try to resolve url "+streamItem.getHref(),xbmc.LOGDEBUG)
    
    # ___ Try to unshort link
    unshort = UnshortenUrl()
    href = unshort.unshortUrl(streamItem.getHref())
    __LOGGER__.log('Unshort url : '+str(href))
    streamItem.setHref(href)
    
    # ___ Resolve url
    playableUrl = False
    progress = xbmcgui.DialogProgress()
    progress.create(constant.__addon__.getLocalizedString(70006),constant.__addon__.getLocalizedString(70009))
    try:
        playableUrl = urlresolver.resolve(streamItem.getHref())
    except:
        pass
    progress.close()
    __LOGGER__.log("Resolved url : "+str(playableUrl),xbmc.LOGDEBUG) 
    
    # ___If the url is resolved, play automatically if the setting is activated  
    if playableUrl != False  and isinstance(playableUrl,unicode) and constant.__addon__.getSetting('play_auto') == 'true':
        streamItem.setPlayableUrl(playableUrl)
        playVideo(streamItem)
        
    # ___If the url is resolved, display the the list of possibilities (Open in web browser, Play, Download or Download & Play )    
    elif playableUrl != False  and isinstance(playableUrl,unicode) and constant.__addon__.getSetting('play_auto') == 'false':
        
        streamItem.setPlayableUrl(playableUrl)
        if constant.__addon__.getSetting('downloader_module') == '0':
            # ___ Do not display download choice if the downloader is not set.
            liste = [constant.__addon__.getLocalizedString(70001),constant.__addon__.getLocalizedString(70002)]            
        else:
            liste = [constant.__addon__.getLocalizedString(70001),constant.__addon__.getLocalizedString(70002),constant.__addon__.getLocalizedString(70003)]
        
        selectDialog = xbmcgui.Dialog()
        select = selectDialog.select(constant.__addon__.getLocalizedString(70000), liste)
        if select == 0:
            playVideo(streamItem) 
        elif select == 1:        
            isRealDebrid = False
            
            # ___ If we use real-debrid, build the streaming page : 
            # ___     https://real-debrid.com/streaming-<MEDIA ID FOR REALDEBRID>
            if 'rdb.so' in str(playableUrl) or 'rdeb.io' in str(playableUrl):
                urlToPlay = "https://real-debrid.com/streaming-"+playableUrl.split("/")[4]                
                streamItem.setPlayableUrl(playableUrl)
                isRealDebrid = True
            
            # ___  For real-debrid we use firefox    
            if isRealDebrid:
                webUtil.openInWebbrowser(streamItem.getPlayableUrl(),constant.__addon__.getSetting('rd_web_browser'))   
            else:
                webUtil.openInWebbrowser(streamItem.getPlayableUrl(),constant.__addon__.getSetting('android_web_browser'))         
            
            # ___ Create or update the history
            history.createOrUpdateHistory(streamItem)
        elif select == 2:
            miscFunctions.downloadFile(streamItem, False)                              
          
    # __ Else display notification for unavailable link
    elif  constant.__addon__.getSetting('play_auto') == 'true':
        miscFunctions.displayNotification(constant.__addon__.getLocalizedString(70014),'info')
        
    # __ Else display limited options        
    else:
        __LOGGER__.log("Unable to resolve url "+streamItem.getHref(),xbmc.LOGWARNING)        
        
        # ___ Only display the option : Open in web browser
        liste = [constant.__addon__.getLocalizedString(70002)]            
            
        selectDialog = xbmcgui.Dialog()
        select = selectDialog.select(constant.__addon__.getLocalizedString(70000), liste)
        if select == 0:
            # ___ Open in web browser                
            isRealDebrid = False
            
            # ___ If we use real-debrid, build the streaming page : 
            # ___     https://real-debrid.com/streaming-<MEDIA ID FOR REALDEBRID>
            if 'rdb.so' in str(playableUrl) or 'rdeb.io' in str(playableUrl):
                urlToPlay = "https://real-debrid.com/streaming-"+playableUrl.split("/")[4]
                isRealDebrid = True
                streamItem.setPlayableUrl(urlToPlay)
            
            # ___  For real-debrid we use the selected web browser in settings -- Only for Android    
            if isRealDebrid:
                webUtil.openInWebbrowser(streamItem.getPlayableUrl(),constant.__addon__.getSetting('rd_web_browser'))   
            else:
                webUtil.openInWebbrowser(streamItem.getPlayableUrl(),constant.__addon__.getSetting('android_web_browser'))         
            
            # ___ Create or update the history     
            history.createOrUpdateHistory(streamItem)
        
        
def playVideo(streamItem):
    """
        Method to play a video
        @param streamItem: the streamItem to play        
    """
    __LOGGER__.log('Play url : '+streamItem.getPlayableUrl(),xbmc.LOGDEBUG)       
    
    # ___ Open the movie with KODI Player
    player = xbmc.Player()
    player.play(streamItem.getPlayableUrl())        
    
    # ___ Waiting to play the movie
    notplaying = True 
    videotimewatched = 0
    isComplete = 0
    percent = 0
    
    while notplaying :
        if player.isPlaying() :
            notplaying = False
        time.sleep(0.1) 
        
    # ___ While the movie is playing
    if xbmc.Player().isPlaying() :
        # ___ Get the total time
        videototaltime = xbmc.Player().getTotalTime()
        while player.isPlaying() :
            
            # ___ Get the current time
            videotimewatched = xbmc.Player().getTime()
            
            if videototaltime == 0:
                # ____Get the total time
                videototaltime = xbmc.Player().getTotalTime() 
            # ___ Sleep 500ms
            time.sleep(0.5)
    
   
    
    if videotimewatched is not None and videototaltime is not None and videotimewatched >= videototaltime:
        isComplete = 1
    else:
        isComplete = 0
        
    if videotimewatched is not None and videototaltime is not None and videototaltime > 0:
        percent = float( ( videotimewatched * 100 ) / videototaltime )
    else:
        percent = 0
                
    # ___ Create or update the history       
    history.createOrUpdateHistory(streamItem,videotimewatched,percent,isComplete)

    
def playStrm(listItems):
    """
        Method to play a .strm file
        @param streamItem : the StreamItem get from the .strm file
    """
    
    # ___ Display links choice
    dialog = xbmcgui.Dialog()
    listStr = []
    for index in range(0,len(listItems)):
        item = listItems[index]
        item.regenerateKodiTitle()
        listStr.append(item.getKodiTitle())
    result = dialog.select(constant.__addon__.getLocalizedString(70013), listStr)
    
    # ___ Until the link is not resolved, we display the links choice dialog
    error = False
    while result > -1 or error: 
        result = -1
        error = False
        # ___ Resolve url
        playableUrl = False
        progress = xbmcgui.DialogProgress()
        progress.create(constant.__addon__.getLocalizedString(70006),constant.__addon__.getLocalizedString(70009))
        try:
            playableUrl = urlresolver.resolve(listItems[result].getHref())
        except:
            # ___ If the url is not resolved, display link choice again.
            error = True   
            listItems[result].setKOLinkStatus()
            listItems[result].regenerateKodiTitle()
            listStr[result] = listItems[result].getKodiTitle()
            result = dialog.select(constant.__addon__.getLocalizedString(70013), listStr)
            
        progress.close()
        __LOGGER__.log("Resolved url : "+str(playableUrl),xbmc.LOGDEBUG) 
        
        # ___If the url is resolved, display the the list of possibilities (Open in web browser, Play, Download or Download & Play )
        if not error:
            if playableUrl != False  and isinstance(playableUrl,unicode) :        
                
                item = xbmcgui.ListItem(path=playableUrl)
                xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),True,item)
            
            else:
                # ___ If the url is not resolved, display link choice again.            
                error = True   
                listItems[result].setKOLinkStatus()
                listItems[result].regenerateKodiTitle()
                listStr[result] = listItems[result].getKodiTitle()
                result = dialog.select(constant.__addon__.getLocalizedString(70013), listStr)
                 