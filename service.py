#!/usr/bin/python
# -*- coding: utf-8 -*-

from default import Cleaner
from settings import *
from utils import notify, debug
import xbmc, xbmcaddon
import simplejson as json


def autostart():
    """
    Starts the cleaning service.
    """
    cleaner = Cleaner()

    service_sleep = 4  # Lower than 4 causes too much stress on resource limited systems such as RPi
    ticker = 0
    delayed_completed = False

    while not cleaner.monitor.abortRequested():
        if get_setting(service_enabled):
            scan_interval_ticker = get_setting(scan_interval) * 60 / service_sleep
            delayed_start_ticker = get_setting(delayed_start) * 60 / service_sleep

            if delayed_completed and ticker >= scan_interval_ticker:
                results, _ = cleaner.clean_all()
                notify(results)
                ticker = 0
            elif not delayed_completed and ticker >= delayed_start_ticker:
                delayed_completed = True
                results, _ = cleaner.clean_all()
                notify(results)
                ticker = 0

            cleaner.monitor.waitForAbort(service_sleep)
            ticker += 1
        else:
            cleaner.monitor.waitForAbort(service_sleep)

    debug("Abort requested. Terminating.")
    return


    
class Main:
    def __init__( self ):
        debug('init main')
        self._service_setup()
        while (not xbmc.abortRequested):
            xbmc.sleep(1000)

    def _service_setup( self ):
        debug('installing service')
        self.Player = MyPlayer(action = self._service_janitor)

    def _service_janitor( self, video_type, expired_videos ):
        debug('service janitor')
        # mark as watched
        debug('%s to clean : %s (%s)' % (video_type, expired_videos['title'], expired_videos['filename']),xbmc.LOGNOTICE)
        try:
            cleaner = Cleaner()
            results, _ = cleaner.clean_all(video_type=video_type, expired_videos=expired_videos)
            # do janitor
            debug(results)
            notify(results)
        except:
            debug('failed to do janitor on video %s (filename= %s )' % (expired_videos['filename'],expired_videos['title']), xbmc.LOGNOTICE)
        
   
# monitor notifications
class MyPlayer(xbmc.Monitor):
    def __init__( self, *args, **kwargs ):
        debug('Player Class Init')
        xbmc.Monitor.__init__( self )
        self.action = kwargs['action']
        
    def onNotification( self, sender, method, data ):
        if sender == 'xbmc':
            # Replace with next condition to enable clean after marked seen in library
            
            # if method == 'Player.OnStop' or method == 'VideoLibrary.OnUpdate':
            if method == 'Player.OnStop':
                
                debug('xbmc %s' % method)
                result = json.loads(data)
                if method == 'Player.OnStop' or ( method == 'VideoLibrary.OnUpdate' and 'playcount' in result ):
                    # if viewing in file mode and playback stopped at the end
                    if 'item' in result and 'title' in result["item"] and result["end"]:
                        if result['item']['type'] == 'episode' or result['item']['type'] == 'movie' or result['item']['type'] == 'musicvideo':
                            # mark episode as watched
                            
                            xpired_videos = {'filename':result["item"]["file"],'title':result["item"]["title"]}
                            self.action(result['item']['type'] + 's',expired_videos)
                    elif method == 'Player.OnStop':
                        # wait 1s before marking episode
                        xbmc.sleep(1000)

if __name__ == "__main__":
    debug('chargement main service')
    if get_setting(instant_enabled):
        debug('service instant clean')
        Main()
    else:
        debug('run once')
        autostart()
