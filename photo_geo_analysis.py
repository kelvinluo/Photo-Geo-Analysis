
#Installed by calling 'pip install requests requests_oauthlib'
import requests
from requests_oauthlib import OAuth1
#Installed by calling 'pip install -U googlemaps'
import googlemaps
from datetime import datetime
import pprint, json, csv

#Set up authorization for both 500px api and google maps api
auth = OAuth1('FyL5oMyb463i7ZfnViC6K1MJw6sIewRgPCuNVh3W',
              '6m7vlKENwnpxSjkA0tWFYGN3XQP43Ne5M9j8yjyT')
gmaps = googlemaps.Client(key='AIzaSyAi-kXDaiz717gCfjtdRvgmuF8bOzznfEg')

#Initialized lists for photos
photos_with_lat = []
photos_without_lat = []

#Number of pages user want to read, default 10 pages and 100 items per page
count = 10

#Loop over pages of the images for there is a 100 item limit for each page
for pageNum in range(1,count + 1):

    #Use RestFul api request to request for image data
    url = 'https://api.500px.com/v1/photos?feature=popular&sort=votes_count&page=' + str(pageNum) + '&rpp=100&image_size=3&include_store=store_download&include_states=voted'
    r = requests.get(url, auth=auth)

    #Process raw data
    content = r.json()
    content = content["photos"][:]

    #Process each image items
    for item in content:
        new_item = []
        #If latitude and longitude are not included in the photo
        if item['latitude'] is None or item['longitude'] is None:
            #Read infor from photo
            if item['location'] is not None:
                new_item.append(item['location'])
            else:
                new_item.append('Unidentified')
            item['name'] = item['name'].replace(',',' ')
            new_item.append(item['name'])
            new_item.append(item['votes_count'])
            new_item.append(item['image_url'])
            #Store in the list
            photos_without_lat.append(new_item)
        else:
            #use google map api to locate the country where the image is taking
            reverse_geocode_result = gmaps.reverse_geocode((item['latitude'], item['longitude']))
            #Initialized as unidentified in case the location is identified
            country = 'Unidentified'
            if len(reverse_geocode_result) > 0:
                reverse_geocode_result = reverse_geocode_result[0]['address_components']
                for address in reverse_geocode_result:
                    if 'country' in address['types']:
                        country = address['long_name']
            #Read information
            new_item.append(country)
            item['name'] = item['name'].replace(',',' ')
            new_item.append(item['name'])
            new_item.append(item['votes_count'])
            new_item.append(item['latitude'])
            new_item.append(item['longitude'])
            new_item.append(item['image_url'])
            photos_with_lat.append(new_item)

#write to the csv file which will contain the photos contains latitude and longitude
with open('photo_with_lat_lon.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar=',', quoting=csv.QUOTE_MINIMAL)
    fieldnames = ['Country', 'Country Popularity', 'Photo Name', 'Votes', 'Latitude', 'Longitude', 'URL']
    spamwriter.writerow(fieldnames)
    for item in photos_with_lat:
        try:
            #Calculate popularity of each country
            popularity = [a[0] for a in photos_with_lat].count(item[0])
            spamwriter.writerow([item[0], popularity, item[1], item[2], item[3], item[4],
                             item[5]])
        except:
            print("Some photos' Image URL contains invalid character.")

#Write to the csv file which will contain the photos contains latitude and longitude
with open('photo_without_lat_lon.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar=',', quoting=csv.QUOTE_MINIMAL)
    fieldnames = ['Location', 'Photo Name', 'Votes', 'URL']
    spamwriter.writerow(fieldnames)
    for item in photos_without_lat:
        try:
            spamwriter.writerow([item[0], item[1], item[2], item[3]])
        except:
            print("Some photos' Image URL contains invalid character.")
