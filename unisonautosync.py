#!/usr/bin/env python

"""
Unison Auto Sync

Synchronize files that change (monitored via fsevents) using unison.
"""

from fsevents import Observer
import threading
from subprocess import call
from socket import gethostname

OBSERVER = Observer()
OBSERVER.start()

#### EDIT HERE ####
HOME          = "/Users/alakazam/"
LOCALSRC      = "/Users/alakazam/Dropbox/Work4Labs"
REMOTEDST     = "ssh://olefloch@lab3.work4labs.com/"
UNISONOPTIONS = [
    "-batch", "-times=true", '-prefer=/Users/alakazam/Dropbox/Work4Labs',
    '-ignore=Path */log', '-ignore=Path */cache', '-ignore=Path */web/web_*',
    '-ignore=Path *.unison*', '-confirmbigdel=false']
UNISONCMD     = "/opt/local/bin/unison"
###################

BASE_INTERVAL    = 1 # sec
CURRENT_INTERVAL = BASE_INTERVAL

MUST_SYNC = True

def fs_event_callback(subpath, mask):
    """
    The callback that will be called when a sync is needed. It sets a global
    flag to true.
    
    FIXME: Use classes...
    """
    global MUST_SYNC
 
    MUST_SYNC = True
    print "must sync"

#Timer Callback
def timer_callback():
    """
    Method called in a loop, every few seconds, that checks to see if a
    modification has been made.
    """
    global CURRENT_INTERVAL, MUST_SYNC
  
    if MUST_SYNC:
        cmd = [UNISONCMD, LOCALSRC, REMOTEDST] + UNISONOPTIONS
        print cmd
        ret = call(cmd)
    
        if ret == 0:
            MUST_SYNC = False
            CURRENT_INTERVAL = BASE_INTERVAL
      
            call(
                ['/Users/Alakazam/.scripts/growl.sh', 'Unison sync done !'],
                env={'G_TITLE': 'Unison'})
        else:
            print "Failed."
            CURRENT_INTERVAL = CURRENT_INTERVAL * 2
            print "wait %s seconds" % CURRENT_INTERVAL
            call(
                ['/Users/Alakazam/.scripts/growl.sh', '-high',
                    ('[FAIL] Unison sync FAILED, waiting %d seconds !'
                        % CURRENT_INTERVAL)],
                env={'G_TITLE': 'Unison'})
  
    threading.Timer( CURRENT_INTERVAL, timer_callback ).start()

#Setup Callbacks
from fsevents import Stream

threading.Timer(BASE_INTERVAL, timer_callback).start()
OBSERVER.schedule(Stream(fs_event_callback, LOCALSRC))
