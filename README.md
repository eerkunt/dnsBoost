# dnsBoost

```This documentation is not up-to-date. Will be updated soon```

This is a **Python** script that is used to be in **Mac OSX Environment** to test & change to the most robust DNS that are already defined in ```/etc/resolv.conf```

## Requirements

```dnsBoost``` requires ```dns.resolver``` Python module installed in your system ;

## Installation

1. Install ```dns.resolver``` first via [dnspython @GitHub](https://github.com/rthalley/dnspython)
2. Install ```terminal-notifier```
	You can either use ```gem``` or ```brew``` for easy installation.

	```gem install terminal-notifier```

	or

	```brew install terminal-notifier```
3. Install ```reattach-to-user-namespace```via ```gem``` or ```brew```.You can use the steps on 2nd section.
4. If you are going to use this script as scheduled - which is recommended - then you should configure your ```launchd``` to schedule this script.

	* Copy ```org.github.eerkunt.dnsBoost.plist``` to your ```/Library/LaunchAgents``` directory with ```root``` privileges.
	* Change the absolute pathname in your ```plist``` file.

		```xml
	<key>ProgramArguments</key>
	<array>
		<string>CHANGE HERE</string>
    </array>
    ```
	* Run ```sudo launchctl load -w /Library/LaunchAgents/org.github.eerkunt.dnsBoost.plist``` in order to start scheduling
	* Run ```sudo launchctl start /Library/LaunchAgents/org.github.eerkunt.dnsBoost.plist``` to start once. It will run in every 60 seconds as configured in your ```plist```file ;

		```xml
	<key>StartInterval</key>
    <integer>60</integer>
	```

## Configuration

You should ( *depends* ) change first few lines of the script, given example as below ;

```python
'''
    THIS IS WHERE YOU SHOULD CONFIGURE YOUR SCRIPT
'''
serviceName = "Wi-Fi"                                                                   # This is Interface that you are using ( OSX )
networkSetup = "/usr/sbin/networksetup"                                                 # Path to networksetup
osaScript = "/usr/local/bin/terminal-notifier"                                          # Path to terminal-notifier. Install it via brew or gem
appIcon = "/Users/teeerkunt/Documents/SVN_Repository/scripts/dnsBoost/dnsBoost.png"     # This is the icon that you want to show in notifier
notificationSound = "Pop"                                                               # This is the sound that you want to hear on notification. ( Sound Preferences )
reattachToUserNamespace="/usr/local/bin/reattach-to-user-namespace"                     # Path to reattach-to-user-namespace. Install it via brew or gem
username="teeerkunt"                                                                    # The user that will get the notification. Should be a GUI user.
queryList = [ "google.com", "microsoft.com", "apple.com" ]                              # Which domains do we need to check ?
recursor.lifetime = 5.0   
```

Most probably, most of the stuff will not change except ```username``` parameter.

## Issues & Requests

This script has been written in few minutes just for fun. You can either fork the code and do whatever you want or create an issue against it for me to fix or implement the change you want.

#### License
[GPL v3.0](http://www.gnu.org/licenses/gpl-3.0.en.html) licensed and also it is free to use it as in beer.
