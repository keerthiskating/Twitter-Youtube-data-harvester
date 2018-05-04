import geocoder
import time
import sys


class Geocoder:
    def __init__(self, place=None):
        self.__place = place
        self.__retry_constant = 3

    def get_location(self, place):
        self.__place = place
        i = 0
        if place:
            while True:
                try:
                    i = i + 1
                    if 3 <= i <= 150:
                        if i % 3 == 0:
                            print('Waiting to get geocode information...')
                            g = geocoder.google(self.__place)
                            location_string = str(g.latlng[0]) + "," + str(g.latlng[1])
                            return location_string
                    elif i < 2:
                        g = geocoder.google(self.__place)
                        location_string = str(g.latlng[0]) + "," + str(g.latlng[1])
                        return location_string
                except TypeError:
                    time.sleep(self.__retry_constant * i)
        else:
            print('Geocoder received empty string')
            sys.exit()
