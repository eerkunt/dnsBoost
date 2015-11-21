#!/usr/bin/python
'''
This is a DNS tester&changer for OSX. Tested in El Capitan, should work on other distributions[1], too. It is recommended to run this script should run as scheduled[2].
Always read README.md for more detailed information

[1] Maverick+
[2] launchd, launchctl
'''
import dns.resolver
import time
import math
import re
import os

recursor = dns.resolver.Resolver()
recursor.timeout = recursor.lifetime


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
recursor.lifetime = 5.0                                                                 # How long we will wait for a timeout ?
'''
    Do not change anything below unless you know what you are doing
'''
myDnsServers = list()
responseTimes = dict()
dns.resolver.override_system_resolver(recursor)

''' Reading /etc/resolv.conf and fethcing DNS configuration '''
with open("/etc/resolv.conf") as configFile:
    contents = configFile.readlines()
validNSRegex = re.compile(r'nameserver (1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])')

for line in contents:
    match = validNSRegex.search(line)
    if ( match is not None ):
        myDnsServers.append(match.group(1)+"."+match.group(2)+"."+match.group(3)+"."+match.group(4))
        print "=> Added "+match.group(1)+"."+match.group(2)+"."+match.group(3)+"."+match.group(4)+" into the list."

for ns in myDnsServers:
    print "-> "+ns
    average = list()
    recursor.nameservers = [ ns ]
    for fqdn in queryList:
        timeStarted = time.time()
        try:
            answer = recursor.query(fqdn,'A')
            timeFinished = time.time()
            print "   * Resolved "+fqdn+" in "+str(timeFinished-timeStarted)
            average.append(timeFinished-timeStarted)
        except dns.exception.Timeout:
            print "   ! Timeout. Possibly dead DNS."
        except dns.exception.NXDOMAIN:
            print "   ! This DNS returns NXDOMAIN for "+fqdn
        except dns.exception.YXDOMAIN:
            print "   ! "+fqdn+" is too long for this DNS"
        except dns.exception.NoAnswer:
            print "   ? "+fqdn+" query returned with NULL answer."
        except dns.exception.NoNameServers:
            print "   ? "+ns+" is not a valid Name Server."

    if ( len(average) > 0 ):
        responseTimes[ns] = sum(average)/len(average)
    else:
        responseTimes[ns] = 999
    print "   = Average is "+str(responseTimes[ns])

''' Just to be sure that current preferred DNS server is not the fastest one.
    No need to give notification on every job run '''

if ( myDnsServers[0] is not sorted(responseTimes, key=responseTimes.get, reverse=False)[0] ):
    for elem in sorted(responseTimes, key=responseTimes.get, reverse=False):
        print "Fasted DNS is "+ elem +" with response time "+str(responseTimes[elem])+" secs"
        os.system("/usr/bin/su "+username+" -c '"+reattachToUserNamespace+" "+osaScript+" -message \"Active DNS changed to "+elem+"\" -title \"DNS Boost\" -appIcon "+appIcon+" -sound "+notificationSound+"'")
        break

    print "Setting up DNS Servers."
    nsString = " ".join(sorted(responseTimes, key=responseTimes.get, reverse=False))
    os.system(networkSetup+" -setdnsservers "+serviceName+" "+nsString)
else:
    print "System is already using the most robost DNS."
