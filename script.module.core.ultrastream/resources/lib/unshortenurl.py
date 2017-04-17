# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
'''
Created on 02 Jan 2016

@author: Seko
@summary: Class for unshorten link

'''
#---------------------------------------------------------------------
# ____________________        I M P O R T        ____________________
import re
import urllib
import urllib2
import copy
import traceback
import cookielib
import time
import json
import xbmcgui
import constant
import webUtil
from urlparse import urlsplit

# ____________________         C L A S S         ____________________
class UnshortenUrl(object):
    
    
    PATTERN_VIIDME = r'viid\.me'
    PATTERN_CLLKME = r'cllkme\.com'
    PATTERN_SHST = r'sh\.st'
    PATTERN_SHST_WITH_FREEZE = r'http://sh.st/freeze/'
    PATTERN_DPSTREAM = r'https://www.dpstream.net/external_link/'
    
    def __init__(self):
        """
            Constructor
        """
        self.HEADER_CFG = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}
        self.cookiejar = cookielib.CookieJar()
        self.urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar),webUtil.SmartRedirectHandler())
        
        
    def unshortUrl(self,url):
        """
            Method to unshort url
            @param url: the url to unshort
            @return the final url 
        """
        newUrl = self._unshort(url)
        while url != newUrl:
            url = newUrl
            newUrl = self._unshort(url)
        return newUrl
    
    def _unshort(self,url):
        """
            Method to unshort url
            @param url: the url to unshort
            @return the final url 
        """
        domain = urlsplit(url).netloc

        if not domain:
            return url
        
        if re.search(self.PATTERN_VIIDME,url):
            return self._unshortshst(url,'viid.me')
        if re.search(self.PATTERN_CLLKME,url):
            return self._unshortshst(url,'cllkme.com')
        elif re.search(self.PATTERN_SHST_WITH_FREEZE,url):
            return self._unshortshst(url[20:])
        elif re.search(self.PATTERN_SHST,url):
            return self._unshortshst(url)
        elif re.search(self.PATTERN_DPSTREAM,url):
            return self._unshortdpstream(url)
        else:
            return url
        
    def _unshortshst(self,url,host='sh.st'):
        """
            Method to unshort Viid.me url
            @param url: the url to unshort
            @return the final url 
        """
        if url.endswith('/'):
            url = url[:-1]
        request = urllib2.Request(url, headers=self.HEADER_CFG)
        response = None 
        try: 
            response = self.urlOpener.open(request)
            if response is not None and response.getcode() == 200:
                content = response.read()
                sessionPattern = re.compile('(.*)(sessionId: ")(.{1,50})(",)(.*)',re.DOTALL)
                match = sessionPattern.match(content)
                if match is not None:
                    # __ Get adSessionId
                    adSessionId = match.group(3)
                    # __ Construct url
                    urlEnd  = 'http://'+host+'/shortest-url/end-adsession?'
                    data1   = {'adSessionId':adSessionId,'callback':'c'}
                    dataStr = urllib.urlencode(data1)
                    urlEnd+=dataStr
                    # ___ Define headers
                    headers1 = copy.copy(self.HEADER_CFG)
                    headers1["Host"]    = host
                    headers1["Referer"] = url
                    # ___ Sleep 5 seconds
                    currentSecond = 5
                    dp = xbmcgui.DialogProgress()
                    dp.create(constant.__addon__.getLocalizedString(33057),str(currentSecond)+' secondes')
                    while currentSecond > 0:
                        currentSecond = currentSecond-1
                        dp.update((5-currentSecond)*20, str(currentSecond)+' secondes')
                        time.sleep(1)
                    dp.close()
                    dp = None
                    # ___ Request the final url
                    requestEnd = urllib2.Request(urlEnd,headers=headers1)                  
                    responseEnd = None                    
                    try: 
                        responseEnd = self.urlOpener.open(requestEnd)                        
                    except urllib2.HTTPError as e:
                        responseEnd = e
                    except:
                        traceback.print_exc()
                        
                    if responseEnd is not None and responseEnd.getcode() == 200:
                        # ___ Get the destination url
                        contentEnd = responseEnd.read()                        
                        jsonResult = json.loads(contentEnd[6:-2].decode('utf-8'))
                        return jsonResult['destinationUrl']
        
        except:
            traceback.print_exc()
            
        return url
    
    
    def _unshortdpstream(self,url):
        """
            Method to unshort dpstream url
        """
        
        if url.endswith('/'):
            url = url[:-1]
        print url
        request = urllib2.Request(url, headers=self.HEADER_CFG)
        response = None 
        try: 
            response = self.urlOpener.open(request)
            if response is not None and response.getcode() == 200: 
                return response.geturl()
        except:
            traceback.print_exc()
        return url                