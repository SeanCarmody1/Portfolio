import argparse
import collections
import csv
import json
import glob
import math
import os
import pandas
import re
import requests
import string
import sys
import time
import xml

class Bike():
    def __init__(self, baseURL, station_info, station_status):
        self.station_info_url = baseURL + station_info
        self.station_status_url = baseURL + station_status
        self.station_info = requests.get(self.station_info_url).json()['data']['stations']
        self.station_status = requests.get(self.station_status_url).json()['data']['stations']
        pass

    def total_bikes(self):
        return sum(station['num_bikes_available'] for station in self.station_status)

    def total_docks(self):
        return sum(station['num_docks_available'] for station in self.station_status)

    def percent_avail(self, station_id):
        for station in self.station_status:
            if station['station_id'] == str(station_id):
                total = station['num_bikes_available'] + station['num_docks_available']
                if total == 0:
                    return '0%'
                return str(math.floor((station['num_docks_available']/total) * 100)) + '%'
        return ""

    def closest_stations(self, latitude, longitude):
        distances = {}
        for station in self.station_info:
            dist = self.distance(latitude, longitude, station['lat'], station['lon'])
            distances[station['station_id']] = (dist, station['name'])
        closestStations = sorted(distances.items(), key=lambda x: x[1][0])[:3] 
        return {station_id: name for station_id, (_, name) in closestStations}

    def closest_bike(self, latitude, longitude):
        closest_station_id = None
        closest_station_name = None
        min_distance = float('inf')

        for station in self.station_info:
            station_id = station['station_id']
            station_status = next((status for status in self.station_status if status['station_id'] == station_id), None)

            if station_status and station_status['num_bikes_available'] > 0:
                dist = self.distance(latitude, longitude, station['lat'], station['lon'])
                if dist < min_distance:
                    min_distance = dist
                    closest_station_id = station_id
                    closest_station_name = station['name']

        if closest_station_id:
            return {closest_station_id: closest_station_name}
        else:
            return {}
     
        
    def station_bike_avail(self, latitude, longitude):
        for station in self.station_info:
            if station['lat'] == latitude and station['lon'] == longitude:
                for status in self.station_status:
                    if status['station_id'] == station['station_id']:
                        return {station['station_id']: status['num_bikes_available']}
        return {}
        

    def distance(self, lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p) * (1-math.cos((lon2-lon1)*p)) / 2
        return 12742 * math.asin(math.sqrt(a))



if __name__ == '__main__':
    instance = Bike('https://db.cs.pitt.edu/courses/cs1656/data', '/station_information.json', '/station_status.json')
    print('------------------total_bikes()-------------------')
    t_bikes = instance.total_bikes()
    print(type(t_bikes))
    print(t_bikes)
    print()

    print('------------------total_docks()-------------------')
    t_docks = instance.total_docks()
    print(type(t_docks))
    print(t_docks)
    print()

    print('-----------------percent_avail()------------------')
    p_avail = instance.percent_avail(342885) # replace with station ID
    print(type(p_avail))
    print(p_avail)
    print()

    print('----------------closest_stations()----------------')
    c_stations = instance.closest_stations(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_stations))
    print(c_stations)
    print()

    print('-----------------closest_bike()-------------------')
    c_bike = instance.closest_bike(40.444618, -79.954707) # replace with latitude and longitude
    print(type(c_bike))
    print(c_bike)
    print()

    print('---------------station_bike_avail()---------------')
    s_bike_avail = instance.station_bike_avail(40.445834, -79.954707) # replace with exact latitude and longitude of station
    print(type(s_bike_avail))
    print(s_bike_avail)
