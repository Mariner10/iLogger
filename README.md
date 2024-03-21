# iLogger
The successor to Triangular-Inator! iLogger uses iCloud API to query device data and stores it in a memorable CSV format for later usage!

iLogger was made due to Life360's API changes forcing me to pivot how I would want to track my data. Additionlly, I bundled in some interesting new ways to view your data thanks to leaflet!

First things first, iLogger is much more streamlined than Triangular-inator, this is because I was given the opportunity to build it from the ground up as opposed to continuing pushing changes on stuff I had written in the past.
As of posting this, it has ran headlessly on a raspberry pi for 2 months, only occasionally sending a 404 notificaiton to my phone due to iCloud not knowing where I am. It's stability is unmatched, I remember going to check on my Triangular-inator logs after a while and realizing that it had gone offline a week prior. With that in mind, I developed a separate program, just to send me a message if my programs went offline, and it wasnt used once thanks to iLogger's stability.

## What iLogger does:

iLogger will initially ask for your login, in which case you can either choose to give it your password along with your appleID in the initial connection module, or you could sign into it with Apple's own 2 Factor Authentication servers (I do not know how stable this is). Then it will use that authentication to continuously collect your data and save it to CSV files automatically, even if you get a new device! This actually happened during my testing phase as a family member powered on an old 2012 Mac Mini I had signed onto in the past. iLogger noticed tha change and made a new directoy, file, and logged its location, meanwhile I was non the wiser until a while later when I happened to check. 

Once you have a directory full of CSV's you can go into the stats folder and find LogsToCSV.py, which will compile all of your logs thus far, and create multiple informational maps for each device you have tracked thus far. An interesting feature of this which I reused from Triangular-inator was it's ability to download all logs from a remote server. This way you can download your logs on the go.

![Image1](/images/image1.png)

![Image4](/images/image4.png)

![Image2](/images/image2.png)

![Image3](/images/image3.png)


### Take a look at our constants.py file:

**Type of OS you are using, [unix or windows]** *(unix is macos and linux in terms of file system structure)*

`deviceType = "unix"`



**Timezone you are operating** from. i.e America/New_York
`timeZone = 'America/New_York'`



**Where the logs are stored on the separate server you'd want to download them from.** i.e "/home/pi/Triangular-inator/logs/"

`remote_logs_directory = "/home/pi/iLogger/logs/"`



**Where the logs are stored on your machine.** i.e "/Users/me/Desktop/Programming/Python/iLogger/logs/"

local_logs_directory = "/Users/me/Desktop/Programming/Python/dataAnalytics/iLogger/Stats/logs/"



*These variables are for accessing a separate server to download your data if it is not ran locally, if you have no intention on using this function you can leave these blank.*

`serverHostname,serverPort,serverUser,serverPass = 'serverIP.com',1738,'johndoe','bestPassword123'`



**Your appleID email associated with the tracked devices.**

`appleIDEmail = "carterbeaudoin@gmail.com"`



**If you use nfty, you can specify a link here to get notifications about iLogger should something happen.**

`ntfy_subscription = "goonCavePoggers"`


