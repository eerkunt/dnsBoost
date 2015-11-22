#!/usr/bin/python
'''
DNS Boost Daemon for OSX
DNS Boost works

Dependencies :
    - unqlite
    - dns.resolver

TO-DO :
    - Static compile
    - Daemonize it
    - Multi-threading Support
    - Linux Support ( Gnome ? KDE ? WMless ? )
    - Windows Support
'''
from defs import customDNS
import logging

'''
    THIS IS WHERE YOU SHOULD CONFIGURE YOUR scripts
'''
serviceName = "Wi-Fi"                                                                   # This is Interface that you are using ( OSX )
networkSetup = "/usr/sbin/networksetup"                                                 # Path to networksetup
osaScript = "/usr/local/bin/terminal-notifier"                                          # Path to terminal-notifier. Install it via brew or gem
appIcon = "/Users/teeerkunt/Documents/SVN_Repository/scripts/dnsBoost/dnsBoost.png"     # This is the icon that you want to show in notifier
notificationSound = "Pop"                                                               # This is the sound that you want to hear on notification. ( Sound Preferences )
reattachToUserNamespace="/usr/local/bin/reattach-to-user-namespace"                     # Path to reattach-to-user-namespace. Install it via brew or gem
username="teeerkunt"                                                                    # The user that will get the notification. Should be a GUI user.
queryList = [ "google.com", "microsoft.com", "apple.com" ]                              # Which domains do we need to check ?
dbFile = "/Library/Application Support/dnsBoost"                                        # Database path that will be used for historical storing
logFile = "/Library/Application Support/dnsBoost/dnsBoost.log"                          # Logfile. Obvious, isn't it ? :)
'''
    Do not change anything below unless you know what you are doing
'''

logging.basicConfig(filename=logFile, filemode='w', level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
dnsObj = customDNS.DNS( "/etc/resolv.conf", dbFile, 1.0 )
dnsObj.sweepDnsServers( queryList )
dnsObj.updateScores()
dnsObj.currentPreferredDNS = dnsObj.findTheBestScore()

if ( dnsObj.notifyLoggedInUser(username, reattachToUserNamespace, osaScript, appIcon, notificationSound) is True ):
    logging.info(str(dnsObj.currentPreferredDNS)+" become the fastest DNS!")
    dnsObj.makeSystemWideChanges(networkSetup,serviceName)
else:
    logging.info(str(dnsObj.currentPreferredDNS)+" is still the fastest DNS!")
