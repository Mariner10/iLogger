import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap, HeatMapWithTime, TimestampedGeoJson, AntPath
from datetime import datetime, timedelta

zoom = 17



def markerClusters(inputCSV,outputHTML):
    df = pd.read_csv(inputCSV)
    sampled_df = df.iloc[::10, :]

    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=zoom)
    marker_cluster = MarkerCluster().add_to(mymap)

    for index, row in sampled_df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(marker_cluster)

    mymap.save(f"{outputHTML}overallHeatmap.html")

def dailyMarkers(inputCSV,outputHTML):

    day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
    }

    df = pd.read_csv(inputCSV)
    df['Date'] = pd.to_datetime(df['Date'])

    df['Weekday'] = df["Weekday"].map(day_mapping)

    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=zoom)
    marker_cluster = MarkerCluster().add_to(mymap)

    colors = ['red', 'orange', 'beige', 'green', 'blue', 'purple', 'pink']
    for index, row in df.iterrows():
        day = row['Weekday']
        folium.Marker([row['Latitude'], row['Longitude']], icon=folium.Icon(color=colors[day])).add_to(marker_cluster)


    mymap.save(f"{outputHTML}day_of_week_trends_map.html")

def heatmap(inputCSV,outputHTML):

    # Step 1: Data Preprocessing
    df = pd.read_csv(inputCSV)
    df['Timestamp'] = pd.to_datetime(df['Date'])

    # Step 2: Extract Day of the Week as Strings
    df['Weekday'] = df['Timestamp'].dt.day_name()  # Convert to day names

    # Step 3: Map Day of the Week to Integer Values
    day_mapping = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    df['Weekday'] = df['Weekday'].map(day_mapping)

    # Step 4: Spatial Visualization
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=zoom)

    # Prepare data for HeatMapWithTime
    data = [[] for _ in range(len(day_mapping))]  # Initialize empty lists for each day of the week
    for day, group in df.groupby('Weekday'):
        data[day] = group[['Latitude', 'Longitude']].values.tolist()

    # Create HeatMapWithTime layer with customized radius
    hmwt = HeatMapWithTime(data, index=list(day_mapping.keys()), auto_play=True, radius=30)  # Adjust radius as needed
    hmwt.add_to(mymap)

    # Save the map to an HTML file
    mymap.save(f"{outputHTML}day_of_week_heatmap.html")

def locationTypeMap(inputCSV,outputHTML):
    # Step 1: Data Preprocessing
    df = pd.read_csv(inputCSV)

    # Step 2: Spatial Visualization
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=zoom)

    # Prepare data for HeatMapWithTime
    data = {}
    for location_type, group in df.groupby('locationType'):
        data[location_type] = group[['Latitude', 'Longitude']].values.tolist()

    # Create HeatMapWithTime layer with customized radius
    for location_type, location_data in data.items():
        HeatMap(location_data, name=location_type, radius=15, max_zoom=10, overlay=True).add_to(mymap)

    # Add LayerControl to the map
    folium.LayerControl().add_to(mymap)

    # Save the map to an HTML file
    mymap.save(f"{outputHTML}location_Type_Map.html")

def timeSpentAtHeatmap(inputCSV,outputHTML,downsample_factor):
    df = pd.read_csv(inputCSV)

    # Combine 'Date' and 'Time' columns into a single datetime column
    df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    # Step 2: Downsample the data
    df_downsampled = df.iloc[::downsample_factor]

    # Prepare data for HeatMapWithTime
    data = []
    for _, row in df_downsampled.iterrows():
        data.append([row['Timestamp'], row['Latitude'], row['Longitude']])

    print("Number of downsampled data points:", len(data))

    # Spatial Visualization
    map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    mymap = folium.Map(location=map_center, zoom_start=zoom)

    # Create HeatMapWithTime layer
    hmwt = HeatMapWithTime(
        data,
        index=pd.to_datetime(df_downsampled['Time']),
        radius=15,
        auto_play=False,
        min_opacity=0.5,
        max_opacity=0.8,
        overlay=True
    )
    hmwt.add_to(mymap)

    # Add LayerControl to the map
    folium.LayerControl().add_to(mymap)

    # Save the map to an HTML file
    mymap.save(f"{outputHTML}time_Spent_At_Heatmap.html")
                
def frequentMarkers(inputCSV,outputHTML,countAmount):

    def getBounds(inputCSV,countAmount,Query = False):
        placeDict = {}
        df = pd.read_csv(inputCSV)
        df["Latitude"] = df["Latitude"]
        df["Longitude"] = df["Longitude"]
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values(by='Date', inplace=True)
        df['Date'] = df['Date'].apply(lambda x: datetime.strftime(x,"%Y-%m-%d"))

        for index, row in df.iterrows():
            dateTimeString = datetime.strptime(str(row["Date"]) + " " + str(row["Time"]),'%Y-%m-%d %I:%M:%S %p')
            time = dateTimeString.strftime("%p %I:%M")
            dateTimeString = int(dateTimeString.timestamp())
            weekdayAndTime = row["Weekday"] + " " + time[:7]

            if weekdayAndTime not in placeDict:
                placeDict[weekdayAndTime] = {"DateTime": dateTimeString,"Time": row["Time"],"Lat": round(row["Latitude"],3), "Lon": round(row["Longitude"],3),"Pair":(row["Latitude"],row["Longitude"]),"LongitudeList": [], "LatitudeList": [], "Count": 1}
            else:
                placeDict[weekdayAndTime]["Count"] += 1
                placeDict[weekdayAndTime]["LongitudeList"] += [float(row["Longitude"])]
                placeDict[weekdayAndTime]["LatitudeList"] += [float(row["Latitude"])]

        for weekTime in placeDict:
            count = 0
            adder = float(0)
            meanLon = None
            meanLat = None
            bound = placeDict[weekTime]["Lon"]
            for lon in placeDict[weekTime]["LongitudeList"]:
                bound = placeDict[weekTime]["Lon"]
                if str(bound) in str(lon):
                    adder += lon
                    count += 1
            if count != 0:
                meanLon = round(adder/count,6)

            count = 0
            adder = float(0)

            bound = placeDict[weekTime]["Lat"]
            for lat in placeDict[weekTime]["LatitudeList"]:
                if str(bound) in str(lat):
                    adder += lat
                    count += 1
            
            if count != 0:
                meanLat = round(adder/count,6)

            if meanLat != None and meanLon != None:
                placeDict[weekTime]["Pair"] = (meanLat,meanLon)

                

        
        placeListList = []
        for key in placeDict:
            if placeDict[key]['Count'] > countAmount:
                if str(placeDict[key]['Lat']) == "37.548" and str(placeDict[key]['Lon']) == "-77.457":
                    pass
                else:
                    placeListList.append({"Timestamp": placeDict[key]['DateTime'],"Day Time": key + "0","Latitude": placeDict[key]['Lat'],"Longitude": placeDict[key]['Lon'],"Pair": placeDict[key]['Pair'],"Count": placeDict[key]['Count']})
            
        if Query == True:
            frequences = pd.DataFrame(placeListList)
            frequences.sort_values(by='Timestamp', inplace=True)
            balls = frequences
            balls.sort_values(by='Count', inplace=True,ascending=False)
            print(frequences)
            print(balls)

            searchWeekday = input("SEARCH:\nEnter Weekday.\n    |- ")
            searchTime = input("Enter Time.\n    |- ")
            searchAMPM = input("Enter AM/PM.\n    |- ")
            print("Begining...")
            found = False
            for index, r0w in balls.iterrows():
                if searchWeekday in r0w["Day Time"] and searchAMPM in r0w["Day Time"] and searchTime in r0w["Day Time"]:
                    found = True
                    print(r0w)
                    print("Top Left corner:",r0w["Latitude"],r0w["Longitude"],"Bottom Right Corner",float(r0w["Latitude"])+0.001,float(r0w["Longitude"])+0.0001)
                    exit()

            if found == False:

                for index, r0w in balls.iterrows(): 
                    count = 0
                    while count < 100:
                        searchTime = datetime.strptime(searchTime,"%I:%M") + timedelta(seconds=600)
                        searchTime = searchTime.strftime("%I:%M")
                        if searchWeekday in r0w["Day Time"] and searchAMPM in r0w["Day Time"] and searchTime in r0w["Day Time"]:
                            found = True
                            print("Next Avaliable time:\n|- ",searchTime,searchAMPM)
                            print(r0w)
                            print("Top Left corner:",r0w["Latitude"],r0w["Longitude"],"Bottom Right Corner",float(r0w["Latitude"])-0.001,float(r0w["Longitude"])+0.001)
                            exit()

                        if searchTime == "11:50":
                            if searchAMPM == "PM":
                                searchAMPM = "AM"
                            else:
                                searchAMPM = "PM"

                        count += 1

                if found == False:   
                    print("Not Found")
                    exit()

        else:
            return placeListList

    placeList = getBounds(inputCSV,countAmount)

    # Create a Folium map centered at a location
    mymap = folium.Map(location=[37.549, -77.450], zoom_start=12)

    # Create a MarkerCluster layer
    marker_cluster = MarkerCluster().add_to(mymap)

    # Iterate over the list of dictionaries
    for data in placeList:
        # Extract information from the dictionary
        day_time = data["Day Time"]
        latitude = data["Pair"][0]
        longitude = data["Pair"][1]
        count = data["Count"]
        
        # Create a marker with popup text
        popup_text = f"Day Time: {day_time}<br>Latitude: {latitude}<br>Longitude: {longitude}<br>Count: {count}"
        folium.Marker(location=(latitude, longitude), popup=popup_text).add_to(marker_cluster)


    # Save the map to an HTML file
    mymap.save(f"{outputHTML}frequentMarkers.html")

def timestampGeoJson(inputCSV,outputHTML):

    # Step 1: Parse the CSV file into a pandas DataFrame
    df = pd.read_csv(inputCSV)

    # Step 2: Group the DataFrame by the 'Date' column
    grouped = df.groupby('Date')

    # Step 3: Iterate over groups and create lines between consecutive points
    lines = []
    for date, group in grouped:
        coordinates = []
        dates = []
        for index, row in group.iterrows():
            coordinates.append([row['Longitude'], row['Latitude']])
            dates.append(f"{row['Date']}T{row['Time']}")
        
        # Step 4: Format the data according to the TimestampedGeoJson structure
        line = {
            "coordinates": coordinates,
            "dates": dates,
            "color": "red",  # Change color as needed
            "weight": 5,     # Change weight as needed
        }
        lines.append(line)

    # Step 5: Create the map and add the TimestampedGeoJson layer to it
    mymap = folium.Map()

    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line["coordinates"],
            },
            "properties": {
                "times": line["dates"],
                "style": {
                    "color": line["color"],
                    "weight": line["weight"],
                },
            },
        }
        for line in lines
    ]

    TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        period="PT1M",
        add_last_point=True,
    ).add_to(mymap)

    # Add AntPath between every point
    for line in lines:
        AntPath(
            locations=line["coordinates"],
            dash_array=[20, 30]  # Customize dash array as needed
        ).add_to(mymap)

    # Fit the map bounds
    mymap.fit_bounds(mymap.get_bounds())

    mymap.save(f"{outputHTML}timestampGeoJson.html")



        

        



