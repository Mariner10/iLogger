#Throw those credentials in here!
import os


# Type of OS you are using, [unix or windows] 
# (unix is macos and linux in terms of file system structure)
deviceType = "unix"

# Timezone you are operating from. i.e 'America/New_York' (You can run the program without selecting 
# a timezone and the program will print all timezones to choose from, then just paste 
# yours into the timeZone variable.
timeZone = 'America/New_York'

# Where the logs are stored on the separate server you'd want to download 
# them from. i.e "/home/pi/iLogger/logs/"
remote_logs_directory = ""

# Where the logs are stored on your machine. 
# i.e "/Users/me/Desktop/Programming/Python/Triangular-inator/logs/"
local_logs_directory = ""

# These variables are for accessing a separate server to download 
# your data if it is not ran locally, if you have no intention on using 
# this function you can leave these blank.
serverHostname,serverPort,serverUser,serverPass = '',0000,'',''

# Your appleID email associated with the tracked devices.
appleIDEmail = "johndoe@gmail.com"

# If you use nfty, you can specify a link here to get notifications about iLogger should something happen.
ntfy_subscription = ""


#Don't worry about these down here. It's only here for centralized access to the logs folders.
main_path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))
if deviceType == "windows":
    iHateWindows = "\logs\ "
    logPath = main_path + iHateWindows.strip()
else:
    logPath = main_path + "/logs/"