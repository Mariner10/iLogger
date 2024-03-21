import csv
import calendar
import os
from datetime import datetime
from sftp_handler import getLogs
from constants import main_path


if input("Redownload Logs? - (Y/N)\n") == "Y":
    getLogs(False)
else: pass



def findDay(date):
    year,month,day = (int(i) for i in date.split(' '))    
    dayNumber = calendar.weekday(year, month, day)
     
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday","Sunday"]
     
    return days[dayNumber]


def collect_data(devicepath,devicename):
    csv_Files = []
    new_File = f"{main_path}/map/compiled/{devicename}.csv"
    logPath = f"{devicepath}"
    
    try:
        print("Deleting " + new_File + "...")
        os.remove(new_File)
        print("Done!")
    except FileNotFoundError:
        print("we good")

    isExist = os.path.exists(new_File)

    if isExist == False:
        filename = new_File

        try:
            file = open(filename, 'w')
        except FileNotFoundError:
            print("NEW File : ", filename)
            file = open(filename, 'w')

        file.close()

        fields = ["Date", "Time", "Latitude", "Longitude", "Weekday", "Battery", "inTransit", "Speed", "timeAtLocation","locationType" ,"accuracy"]
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            csvfile.close()
        csvfile.close()


        for path, subdirs, files in os.walk(logPath):
            for name in files:
                
                if ".csv" in name:
                    csv_Files.append(str(os.path.join(logPath,name)))
                    

                else:
                    pass

        print("READING")
        for user_File in csv_Files:
            with open(user_File, 'r') as csvfile:
                filename = str(user_File).split("/20")
                filename = "20" + filename[1]
                filename = filename.split("_")
                dateFromFilename = filename[0]

                heading = next(csvfile)
                csvreader = csv.reader(csvfile)

                for row in csvreader:

                    

                    latitude = row[1]
                    longitude = row[2]

                    timeElement = row[0]
                    
                    time = str(datetime.fromtimestamp(float(timeElement)).strftime('%I:%M:%S %p'))
                    battery = row[6]
    
                    inTransit = row[5]
                    if "class" in inTransit:
                        inTransit == "False"

                    speed = row[3]
                    timeAtLocation = row[4]
                    locationType = row[7]
                    accuracy = row[9]
                    weekday = findDay(dateFromFilename.replace("-"," "))
                    
                    data = [dateFromFilename, time, latitude, longitude, weekday, battery, inTransit, speed, timeAtLocation,locationType ,accuracy]

                    with open(new_File, 'a') as file:
                                writer = csv.writer(file)
                                row = data
                                
                                writer.writerow(row)

                    file.close
                csvfile.close
    print("Wrote all Lines to " + new_File + "...")


from mapStats import *
for path, subdirs, files in os.walk(main_path + "/logs"):
    try:
        devicename = path.split("/logs/")[1]
        collect_data(path,devicename)


        compiledFilename = f"{main_path}/map/compiled/{devicename}.csv"
        outputHTML = f"{main_path}/map/{devicename}/"
        timeSpentAtHeatmap(compiledFilename,outputHTML,10)
        locationTypeMap(compiledFilename,outputHTML)
        dailyMarkers(compiledFilename,outputHTML)
        heatmap(compiledFilename,outputHTML)
        frequentMarkers(compiledFilename,outputHTML,3)
        timestampGeoJson(compiledFilename,outputHTML)

    except IndexError as e:
        print(e)
        pass

    
    
