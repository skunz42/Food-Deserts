import googlemaps
import json
import urllib
import csv
import sys

def findPlace(lat, lng, radius, kw, key):
  #making the url
  AUTH_KEY = key
  LOCATION = str(lat) + "," + str(lng)
  RADIUS = radius
  KEYWORD = kw
  MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&keyword=%s'
           '&sensor=false&key=%s') % (LOCATION, RADIUS, KEYWORD, AUTH_KEY)
  #grabbing the JSON result
  response = urllib.request.urlopen(MyUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw)
  #print(jsonData)
  return jsonData

#This is a helper to grab the Json data that I want in a list
def IterJson(place):
    x = [place['name'], place['reference'], place['geometry']['location']['lat'],
         place['geometry']['location']['lng'], place['vicinity'], place['rating'], place['user_ratings_total']]
    return x

#Calculates the coordinates needed for all locations in a city
def calcCoords(key, coords, city):
    gmaps = googlemaps.Client(key=key)
    geocode_result = gmaps.geocode(city)
    nelat = geocode_result[0]['geometry']['bounds']['northeast']['lat']
    nelng = geocode_result[0]['geometry']['bounds']['northeast']['lng']
    swlat = geocode_result[0]['geometry']['bounds']['southwest']['lat']
    swlng = geocode_result[0]['geometry']['bounds']['southwest']['lng']

    templat = swlat
    templng = swlng

    while (templat <= nelat):
        while (templng <= nelng):
            coords.append((templat, templng))
            templng += 0.015
        templng = swlng
        templat += 0.015

    #print(coords)

def write_csv(places, arg, city):
    with open(arg, mode = 'w') as csv_test:
        csv_writer = csv.writer(csv_test, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        for p in places:
            if city in p[4] and int(p[6]) > 5 and "Dollar" not in p[0]:
                csv_writer.writerow([p[0], p[2], p[3], p[4], p[5], p[6]])

def main():
    if (len(sys.argv) != 4):
        print("Please input in the following format: python fetchstores.py <file> <city> <state abbrev>")
        return 1

    arg1 = str(sys.argv[1]) + ".csv"
    city = str(sys.argv[2])
    state = str(sys.argv[3])
    citystate = city + ", " + state

    credsfile = open("../Geo-Credentials/creds.txt", "r")
    keyval = credsfile.read()
    coords = []
    calcCoords(keyval, coords, citystate)

    gplaces = set()
    cplaces = set()
    for c in coords:
        gsearch = findPlace(c[0], c[1], 1000, 'grocery', keyval)
        if gsearch['status'] == 'OK':
            for place in gsearch['results']:
                x = IterJson(place)
                gplaces.add(tuple(x))

        csearch = findPlace(c[0], c[1], 1000, 'convenience', keyval)
        if csearch['status'] == 'OK':
            for place in csearch['results']:
                x = IterJson(place)
                cplaces.add(tuple(x))

    groc_list = list(gplaces.difference(cplaces))

    write_csv(groc_list, arg1, city)

main()
