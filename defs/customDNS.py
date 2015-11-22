import os
import time
import dns.resolver
import re
from unqlite import UnQLite

class DNS:
        def __init__( self, configFileName, dbPath, timeout ):

            self.dnsArray = list()
            self.responseTimes = dict()

            if os.access( configFileName, os.R_OK ) is False:
                print "Can not read "+configFileName+" !"
                exit(-1)

            if os.access( dbPath, os.F_OK ) is False:
                print "Created DB Directory at "+dbPath
                os.mkdir( dbPath )

            db = UnQLite( dbPath+"/history.db" )
            self.dnsDB = db.collection('dnsResponses')

            if ( self.dnsDB.exists() is False ):
                print "Initial DB Created."
                self.dnsDB.create()

            self.recursor = dns.resolver.Resolver()
            self.recursor.lifetime = timeout
            self.recursor.timeout = self.recursor.lifetime
            dns.resolver.override_system_resolver(self.recursor)

            with open(configFileName) as configFile:
                contents = configFile.readlines()
            validNSRegex = re.compile(r'nameserver (1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])\.(1[0-9][0-9]|2[0-4][0-9]|25[0-5]|[0-9][0-9]|[0-9])')

            for line in contents:
                match = validNSRegex.search(line)
                if ( match is not None ):
                    self.dnsArray.append(match.group(1)+"."+match.group(2)+"."+match.group(3)+"."+match.group(4))
                    print "=> Added "+match.group(1)+"."+match.group(2)+"."+match.group(3)+"."+match.group(4)+" into the list."

            self.currentPreferredDNS = self.dnsArray[0]
            return

        def sweepDnsServers( self, queryList ):
            for ns in self.dnsArray:
                print "-> "+ns
                average = list()
                self.recursor.nameservers = [ ns ]
                for fqdn in queryList:
                    timeStarted = time.time()
                    try:
                        answer = self.recursor.query(fqdn,'A')
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
                    self.responseTimes[ns] = sum(average)/len(average)
                else:
                    self.responseTimes[ns] = 999
                print "   = Average is "+str(self.responseTimes[ns])
            return

        def updateScores( self  ):
            # print "updateScores()"
            # print self.dnsDB.all()
            # print "ResponseTimes: "+str(self.responseTimes)
            for (dnsIP, responseTime) in self.responseTimes.iteritems():
                currentInfo = self.dnsDB.filter(lambda obj: obj['dnsServer'] == dnsIP )
                # print "DNS : "+dnsIP + "("+str(len(currentInfo))+" records)"
                # print "\tCurrentInfo : "+str(currentInfo)
                averageArray = list()
                __id = -1
                if ( len(currentInfo) > 0 ):
                    for (key, value) in currentInfo[0].iteritems():
                        if ( key == "averageResponseTime" ):
                            for avgRT in value:
                                averageArray.append(avgRT)
                                # print "\t\t+ Appended "+str(avgRT)+" into array"
                        elif ( key == "__id"):
                            __id = value

                ''' In order to change a decision in 2 hours max, length of average array should be 24
                    Assuming that this script checks everything in every 5 minutes '''
                maxLength = 5
                if ( len(averageArray) > maxLength ):
                    averageArray = averageArray[(len(averageArray)-maxLength):len(averageArray)]

                averageArray.append(responseTime)
                # print "\tAverage Array : "+str(averageArray)

                if (len(currentInfo) > 0 ):
                    ''' Update the values since we already have some in the DB '''
                    # print "\tUpdating data.."
                    if ( self.dnsDB.update( __id, { 'dnsServer' : dnsIP, 'averageResponseTime': averageArray }) == True ):
                        pass
                        # print "\t\tUpdated "+dnsIP,"->",str(averageArray)," id:"+str(__id)
                        # else:
                        # print "\t\tUnable to update data for "+dnsIP
                else:
                    ''' Insert the new value into the DB '''
                    # print "\tInserting data.."
                    self.dnsDB.store([{ 'dnsServer':dnsIP, 'averageResponseTime': [ responseTime ] }])
                    # print "\t\tInserted new responseTime ("+str(responseTime)+") in "+dnsIP

        def findTheBestScore( self ):
            dbDump = self.dnsDB.all()
            result = dict()
            for row in dbDump:
                self.responseTimes[row['dnsServer']] = sum(row['averageResponseTime'])/len(row['averageResponseTime'])

            return sorted(self.responseTimes, key=self.responseTimes.get, reverse=False)[0]

        def notifyLoggedInUser( self, username, reattachToUserNamespace, osaScript, appIcon, notificationSound ):
            selectedDNS = sorted(self.responseTimes, key=self.responseTimes.get, reverse=False)[0]
            if ( selectedDNS is not self.currentPreferredDNS ):
                print "Fasted DNS is "+ selectedDNS +" with response time "+str(self.responseTimes[selectedDNS])+" secs"
                os.system("/usr/bin/su "+username+" -c '"+reattachToUserNamespace+" "+osaScript+" -message \"Active DNS changed to "+selectedDNS+"\" -title \"DNS Boost\" -appIcon "+appIcon+" -sound "+notificationSound+"'")
                return True
            else:
                print "System is already using the most robost DNS."
                return False

        def makeSystemWideChanges( self, networkSetup, serviceName ):
            print "Setting up DNS Servers."
            nsString = " ".join(sorted(self.responseTimes, key=self.responseTimes.get, reverse=False))
            os.system(networkSetup+" -setdnsservers "+serviceName+" "+nsString)
            return
