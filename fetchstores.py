import googlemaps
import json
import urllib
import csv
import sys

'''***********************************************
                    findPlace
    purpose:
        gets json data from google search
    params:
        lat - represents latitude
        lng - represents longitude
        radius - represents search radius
        kw - represents search word (ie grocery)
        key - API authentication key
    return:
        jSonData - returns search in json format
***********************************************'''
def findPlace(lat, lng, radius, kw, key):
  #making the url
  AUTH_KEY = key #authentication key
  LOCATION = str(lat) + "," + str(lng) #location for url
  RADIUS = radius
  KEYWORD = kw #search word
  MyUrl = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json'
           '?location=%s'
           '&radius=%s'
           '&keyword=%s'
           '&sensor=false&key=%s') % (LOCATION, RADIUS, KEYWORD, AUTH_KEY) #url for search term
  #grabbing the JSON result
  response = urllib.request.urlopen(MyUrl)
  jsonRaw = response.read()
  jsonData = json.loads(jsonRaw)
  return jsonData

'''***********************************************
                    IterJson
    purpose:
        returns array of data parsed from search
        request
    params:
        place - jSonData retreived from search
    return:
        array of parsed data
***********************************************'''
def IterJson(place):
    x = [place['name'], place['reference'], place['geometry']['location']['lat'],
         place['geometry']['location']['lng'], place['vicinity'], place['rating'], place['user_ratings_total']]
    return x

'''***********************************************
                    calcCoords
    purpose:
        calculates the coordinates to use when
        searching. Updates an array of tuples
        storing coordinates
    params:
        key - API authentication key
        coords - array of coordinates
        city - city being searched
    return:
        None
***********************************************'''
def calcCoords(key, coords, city):
    gmaps = googlemaps.Client(key=key) #authentication
    geocode_result = gmaps.geocode(city) #gets results for city
    nelat = geocode_result[0]['geometry']['bounds']['northeast']['lat'] #northeast latitude
    nelng = geocode_result[0]['geometry']['bounds']['northeast']['lng'] #northeast longitude
    swlat = geocode_result[0]['geometry']['bounds']['southwest']['lat'] #southwest latitude
    swlng = geocode_result[0]['geometry']['bounds']['southwest']['lng'] #southwest longitude

    templat = swlat #latitude and longitude used for calculation purposes
    templng = swlng

    while (templat <= nelat): #north/south calc
        while (templng <= nelng): #east/west calc
            coords.append((templat, templng))
            templng += 0.015 # ~ 1 km
        templng = swlng
        templat += 0.015 # ~ 1 km

'''***********************************************
                    write_csv
    purpose:
        write data to csv
    params:
        places - list of grocery store tuples
        fn - filename
        city - city name
    return:
        None
***********************************************'''
def write_csv(places, fn, city):
    with open(fn, mode = 'w') as csv_test:
        csv_writer = csv.writer(csv_test, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        for p in places:
            if city in p[4] and int(p[6]) > 5 and "Dollar" not in p[0]: # filter out dollar stores and stores outside the city
                csv_writer.writerow([p[0], p[2], p[3], p[4], p[5], p[6]])


'''***********************************************
                    scrapeData
    purpose:
        creates set of data
    parameters:
        fn - filename
        citystate - city + state for scraping
        city - city name for csv writing
    return:
        None
***********************************************'''
def scrapeData(fn, citystate, city):
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

    write_csv(groc_list, fn, city)

def main():
    if (len(sys.argv) != 4):
        print("Please input in the following format: python fetchstores.py <file> <city> <state abbrev>")
        return 1

    fn = str(sys.argv[1]) + ".csv"
    city = str(sys.argv[2])
    state = str(sys.argv[3])
    citystate = city + ", " + state

    scrapeData(fn, citystate, city)
main()
