from pyicloud import PyiCloudService
from datetime import datetime, timedelta
import requests
from math import radians, cos, sin, asin, sqrt
import sys
import os
import csv
from time import sleep
from Stats.constants import ntfy_subscription, appleIDEmail,timeZone
from pytz import timezone
tz = tz = timezone(timeZone)

# Seconds between each poll
POLLING_RATE = 30


# Set up iCloud service with your Apple ID, if you only provide appleID it will prompt you to enter 2FA, otherwise paste your password into it
#  as such > PyiCloudService(appleIDEmail, "password") doing it this way will lead to greater stability from my testing.
api = PyiCloudService(appleIDEmail)

# These are pretty self explanatory, if you want to see your device info, set output to true, if you want to save to CSVs, set that one to true
OUTPUT_DETAILS_IN_CMD = False
SAVE_TO_CSV_FILES = True


# 2 Step Verification
if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
elif api.requires_2sa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber')))
        )

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)



def speedCalculation(lon1, lat1, lon2, lat2):

    def calcDistance(lon1, lat1, lon2, lat2):
        """
        Calculate the distance in kilometers between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r

    distance = calcDistance(lon1,lat1,lon2,lat2)

    speed = distance / (POLLING_RATE/3600)

    return speed
    # ^ this is in KPH

class Device:
    def __init__(self,device):
        status = device.status()
        locationInfo = device.location()

        self.name = status['name']
        self.deviceType = status['deviceDisplayName']
        self.latitude = round(float(locationInfo['latitude']),7)
        self.longitude = round(float(locationInfo['longitude']),7)
        self.batteryLevel = round(float(status['batteryLevel']) *100,2)
        self.positionType = locationInfo['positionType']
        self.altitude = locationInfo['altitude']
        self.accuracy = locationInfo['horizontalAccuracy'],locationInfo['verticalAccuracy']
        self.locationFinished = locationInfo['locationFinished']
        self.timestamp = float(locationInfo['timeStamp']) / 1000 # Convert ms EPOCH time to second EPOCH time. (Not having this makes it think you're in the year 50,000 or something)

    def convertToDict(self):
        deviceDict = {"name":self.name,"deviceType":self.deviceType,"latitude":self.latitude,"longitude":self.longitude,"batteryLevel":self.batteryLevel,"positionType":self.positionType,"timestamp":self.timestamp}
        return deviceDict

    def saveFile(self):
        deviceType = 'macOS'

        main_path = str(os.path.join(os.path.dirname(os.path.abspath(__file__))))

        if deviceType == "windows":
            iHateWindows = "\logs\ "
            logPath = main_path + iHateWindows.strip()
        else:
            logPath = main_path + "/logs/"
        
        current_datetime = datetime.now(tz)
        string = str(current_datetime)
        dateAndTime = string.split()
        date = dateAndTime[0]

        fileNameString = str(self.name).replace(" ", "_")

        isExist = os.path.exists(logPath + fileNameString + "/" + date + "_" + fileNameString + ".csv")

        if isExist == False:
            # create a file object along with extension
            filename = logPath + fileNameString + "/" + date + "_" + fileNameString + ".csv"
            try:
                file = open(filename, 'w')
            except FileNotFoundError:
                os.mkdir(logPath + fileNameString + "/")
                print("NEW DEVICE : ", fileNameString)
                file = open(filename, 'w')
    

            file.close()

            filename = logPath + fileNameString + "/" + date + "_" + fileNameString + ".csv"
            fields = ['Time Object (EPOCH)', 'Latitude','Longitude','Speed (MPH)','Time Since Last Moved (Min)',"Stationary (T/F)", 'Battery Level (%)', "Position Type", "Altitude", "Accuracy",'locationFinished']
            with open(filename, 'w') as csvfile:
                # creating a csv writer object
                csvwriter = csv.writer(csvfile)
                # writing the fields
                csvwriter.writerow(fields)

        else:    
            pass
        
        data = [self.timestamp,self.latitude,self.longitude,self.batteryLevel,self.positionType,self.altitude,self.accuracy,self.locationFinished]


        def lastRow(user_File):
            rowData = []
            with open(user_File, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    rowData.append(row)
            
            return rowData[-1]

        filename = logPath + fileNameString + "/" + date + "_" + fileNameString + ".csv"

        
        try:
            lastLog = lastRow(filename)
            if round(float(data[1]),4) == round(float(lastLog[1]),4) or round(float(data[2]),4) == round(float(lastLog[2]),4):
                print(self.name + " has not moved since last check, continuing...\n")
        
        
            else:
                stationary = bool
                speed = 0

                time1 = datetime.fromtimestamp(float(lastLog[0]))
                time2 = datetime.fromtimestamp(float(self.timestamp))
                timeDifference = time2 - time1
                minutesSinceLastMovement = int(timeDifference.seconds) / 60
                
                if minutesSinceLastMovement > 5:
                    stationary = True

                else:

                    if stationary == True:
                        if data[4] != "GPS": # What sometimes happens is that your phone will switch from a GPS provided location to a Wifi or Cellular tower provided
                                            # location to save battery, when this happens, your location can rapidly shift to where the wifi or cellular tower "thinks" you are
                                            #  if the device was previously stationary, we do not treat this as a movement type. This prevents a bunch of jumping around (paticularly at night).n 
                            print("Location Type not GPS, cannot determine if this was actual movement or a switch of location type.")

                        else:

                            stationary = False
                            print(self.name + " moved! Logging this change...\n")

                            lat1 = float(self.latitude)
                            long1 = float(self.longitude)
                            lat2 = float(lastLog[1])
                            long2 = float(lastLog[2])

                            speed = float(speedCalculation(long1,lat1,long2,lat2))

                            speed = round(speed * 1.609,2)

                            print(str(speed) + " mph")


                with open(filename, 'a') as file:
                    writer = csv.writer(file)
                    print("Writing row:")
                    row = [data[0], data[1], data[2], speed, minutesSinceLastMovement, stationary, data[3], data[4], data[5], data[6], data[7]]
                    print(row)
                    writer.writerow(row)
                    print("\n")
                    
        except ValueError:
            print("New Row, ignoring...\n")
            with open(filename, 'a') as file:
                    writer = csv.writer(file)
                    row = [data[0], data[1], data[2], "0","0","True", data[3], data[4], data[5], data[6], data[7]]
                    writer.writerow(row)


    def postDeviceInfo(self):
        print("Device name -\n  | " + self.name + " - [" + self.deviceType + "]")
        print("Location -\n  | " + str(self.latitude) + " , " + str(self.longitude) + " [ Altitude: " + str(self.altitude) + " ]")
        print("Accuracy -\n  | " + str(self.accuracy))
        print("Location Finished? -\n  | " + str(self.locationFinished))
        print("Timestamp -\n  | " + datetime.fromtimestamp(float(self.timestamp)).strftime('%Y-%m-%d %I:%M:%S %p'))
        print("Battery Level -\n  | " + str(self.batteryLevel) + " %")
        print("Position Type -\n  | " + str(self.positionType) + '\n \n')

try:
    while True:
        try:
            devices = api.devices
        except Exception as f:
            print('Failed to get device list from API: ' + str(f) + "\n")
            sleep(POLLING_RATE) # Wait before trying again

        deviceName = ""
        for device in devices:
            try:
                if device.status()['deviceStatus'] == "200":

                    if OUTPUT_DETAILS_IN_CMD == True:
                        Device(device).postDeviceInfo()

                    if SAVE_TO_CSV_FILES == True:
                        Device(device).saveFile()

            except Exception as e:
                print("Uh Oh! Something went wrong!... \n   |   " + str(e))
                if ntfy_subscription is not "":
                    requests.post(f"https://ntfy.sh/{ntfy_subscription}", data=str(e),headers={
                        "Title": "iLogger Experienced a exception!",
                        "Priority": "urgent",
                        "Tags": "boom"
                    })

        sleep(POLLING_RATE)

except KeyboardInterrupt:
    print("Exiting...")
    