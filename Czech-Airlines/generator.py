#!/usr/bin/env python

# Copyright (C) 2011 Adrian Musceac 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, sys, time
import io
import re, string, random
from urllib2 import *
import urllib
from HTMLParser import *


def generate():
	""" Filter the original schedule, get rid of dupes and indirect flights"""
	fw = open('./timetable.txt','ab')
	fr= open('./orar-csa.txt','r')
	content= fr.readlines()
	buf=''
	i=-1
	for line in content:
		if line.find('nonstop')!=-1 and line.find('*')==-1:
			line=line.lstrip(' ')
			line=line.replace('+1',' ')
			buf=buf+line
		
	fw.write(buf)
	fr.close()
	fw.close()
	

def flight_plan():
	"""Generate the actual flightplan from the intermediate file"""
	fw = open('./csa_flights.xml','ab')
	fr= open('./timetable.txt','r')
	content= fr.readlines()
	buf=''
	
	departure_apt=''
	departure_time=''
	arrival_apt=''
	arrival_time=''
	callsign=''
	repeat='WEEK'
	fltrules='IFR'
	req_aircraft=''
	cruise_alt=''
	
	altitudes_jet=(280,290,300,310,320,330,340,350)
	altitudes_prop=(150,160,170,180,190,200,210,220)
	airports=airport_list()
	i=-1
	deps=[]
	arrs=[]
	types=[]
	for line in content:
		line=line.rstrip('\n')
		arr=line.split('  ')
		for x in range (1, 20):
			for k in arr:
				if len(k)==0:
					arr.remove(k)
					
		for k in arr:
			j=k.strip()
			if k.find('OK')!=-1:
				j=k.replace(' ','')
			arr[arr.index(k)]=j
			
		if len(arr)>10:
			arr[1]=arr[1]+arr[2]
			arr.remove(arr[2])
			
		''' No longer used:		
		if arr[3] not in deps:
			deps.append(arr[3])
		
		if arr[6] not in arrs:
			arrs.append(arr[6])
		
		if arr[7] not in types:
			types.append(arr[7])
			'''
		
		callsign=arr[2]
		req_aircraft=arr[7]
		departure_apt=airports[arr[3]]
		departure_time=arr[4]+':00'
		arrival_time=arr[5]+':00'
		arrival_apt=airports[arr[6]]
		days=arr[1]
		## This line should really be checked, I don't know the usual flightlevels these planes fly at.
		if req_aircraft=='ATR':
			cruise_alt=str(random.choice(altitudes_prop))
		else:
			cruise_alt=str(random.choice(altitudes_jet))
		
		for i in days:
			if i.isdigit():	
				i=str(int(i))
				if i =='7':
					i='0'
				
				#print departure_apt + ' => '+arrival_apt, departure_time, arrival_time, cruise_alt, req_aircraft, i, callsign
				xml='''
	<flight>
            <callsign>'''+callsign+'''</callsign>
            <required-aircraft>'''+req_aircraft+'''</required-aircraft>
            <fltrules>IFR</fltrules>
            <departure>
                <port>'''+departure_apt+'''</port>
                <time>'''+i+'/'+departure_time+'''</time>
            </departure>
            <cruise-alt>'''+cruise_alt+'''</cruise-alt>
            <arrival>
                <port>'''+arrival_apt+'''</port>
                <time>'''+i+'/'+arrival_time+'''</time>
            </arrival>
            <repeat>WEEK</repeat>
        </flight>'''
					
				buf=buf+xml
	fw.write(buf)
	fr.close()
	fw.close()

				
		
def aircraft_list():
	aircraft_table=['32S', '737', 'ATR', '321']
	mapping={'32S':'A321',
		'321':'A321',
		'ATR':'ATR-72',
		'737':'737'
		}

def airport_list():
	"""Static mapping of city name to airport. In most cases CSA will land at the biggest airport available but exceptions may exist.
	In the future, use a web service to generate ICAO airports from cities"""
	airports={ 'Prague':'LKPR' ,
		'Abu Dhabi':'OMAA' ,
		'Almaty':'UAAA' ,
		'Amsterdam':'EHAM' ,
		'Athens':'LGAV' ,
		'Barcelona':'LEBL' ,
		'Beirut':'OLBA' ,
		'Belgrade':'LYBE' ,
		'Berlin':'EDDB' ,
		'Bologna':'LIPE' ,
		'Bordeaux':'LFBD' ,
		'Bratislava':'LZIB' ,
		'Brussels':'EBBR' ,
		'Budapest':'LHBP' ,
		'Bucharest':'LROP' ,
		'Cairo':'HECA' ,
		'Carlsbad':'KCRQ' ,
		'Copenhagen':'EKCH' ,
		'Damascus':'OSDI' ,
		'Donetsk':'UKCC' ,
		'Dusseldorf':'EDDL' ,
		'Ekateriburg': 'USSS',
		'Frankfurt':'EDDF' ,
		'Hamburg':'EDDH' ,
		'Hannover':'EDDV' ,
		'Helsinki':'EFHK' ,
		'Kiev':'UKBB' ,
		'Kosice':'LZKZ' ,
		'Krakow':'EPKK' ,
		'Larnaca':'LCLK' ,
		'Ljubljana':'LJLJ' ,
		'Lviv':'UKLL' ,
		'Madrid':'LEMD' ,
		'Marseille':'LFML' ,
		'Milan':'LIML' ,
		'Minsk':'UMMS' ,
		'Moscow':'UUDD' ,
		'Odessa':'KMAF' ,
		'Oslo':'ENGM' ,
		'Ostrava':'LKMT' ,
		'Paris':'LFPG' ,
		'Poprad':'LZTT' ,
		'Riga':'EVRA' ,
		'Rome':'LIRA' ,
		'Rostov on Don':'URRR',
		'Samara':'UWWW' ,
		'Skopje':'LWSK' ,
		'Sofia':'LBSF',
		'St. Petersburg':'ULLI',
		'Stockholm':'ESSA' ,
		'Strasbourg':'LFST' ,
		'Stuttgart':'EDDS' ,
		'Tallinn':'EETN' ,
		'Tashkent':'UTTT' ,
		'Tbilisi':'UGTB' ,
		'Tel Aviv':'LLBG' ,
		'Venice':'LIPH' ,
		'Vilnius':'EYVI' ,
		'Warsaw':'EPWA' ,
		'Yerevan':'UDYC' ,
		'Zagreb':'LDZA' ,
		'Zilina':'LZZI' ,
		'Zurich':'LSZH' 
		}
	
	arrivals=['Abu Dhabi',
	'Prague',
	'Almaty',
	'Amsterdam',
	'Athens',
	'Barcelona',
	'Beirut',
	'Belgrade',
	'Berlin',
	'Bologna',
	'Bordeaux',
	'Bratislava',
	'Brussels',
	'Budapest',
	'Bucharest',
	'Cairo',
	'Carlsbad',
	'Copenhagen',
	'Damascus',
	'Donetsk',
	'Dusseldorf',
	'Ekateriburg',
	'Frankfurt',
	'Hamburg',
	'Hannover',
	'Helsinki',
	'Kiev',
	'Kosice',
	'Krakow',
	'Larnaca',
	'Ljubljana',
	'Lviv',
	'Madrid',
	'Marseille',
	'Milan',
	'Minsk',
	'Moscow',
	'Odessa',
	'Oslo',
	'Ostrava',
	'Paris',
	'Poprad',
	'Riga',
	'Rome',
	'Rostov on Don',
	'Samara',
	'Skopje',
	'Sofia',
	'St. Petersburg',
	'Stockholm',
	'Strasbourg',
	'Stuttgart',
	'Tallinn',
	'Tashkent',
	'Tbilisi',
	'Tel Aviv',
	'Venice',
	'Vilnius',
	'Warsaw',
	'Yerevan',
	'Zagreb',
	'Zilina',
	'Zurich']
	
	departures=['Prague',
	'Abu Dhabi',
	'Almaty',
	'Amsterdam',
	'Athens',
	'Barcelona',
	'Beirut',
	'Belgrade',
	'Berlin',
	'Bologna',
	'Bordeaux',
	'Bratislava',
	'Brussels',
	'Budapest',
	'Bucharest',
	'Cairo',
	'Carlsbad',
	'Copenhagen',
	'Damascus',
	'Donetsk',
	'Dusseldorf',
	'Ekateriburg',
	'Frankfurt',
	'Hamburg',
	'Hannover',
	'Helsinki',
	'Kiev',
	'Kosice',
	'Krakow',
	'Larnaca',
	'Ljubljana',
	'Lviv',
	'Madrid',
	'Marseille',
	'Milan',
	'Minsk',
	'Moscow',
	'Odessa',
	'Oslo',
	'Ostrava',
	'Paris',
	'Poprad',
	'Riga',
	'Rome',
	'Rostov on Don',
	'Samara',
	'Skopje',
	'Sofia',
	'St. Petersburg',
	'Stockholm',
	'Strasbourg',
	'Stuttgart',
	'Tallinn',
	'Tashkent',
	'Tbilisi',
	'Tel Aviv',
	'Venice',
	'Vilnius',
	'Warsaw',
	'Yerevan',
	'Zagreb',
	'Zilina',
	'Zurich']
	
	
	return airports
	#####################################################
	## Code below fetches the ICAO code via name search##
	## Disabled now					   ##
	#####################################################
	
	
	i=0
	for apt in departures:
		#if i<49:
		#	i=i+1
		#	continue
		i=i+1
		time.sleep(3)
		query={'airport':apt,'but1':'Submit'}
		query=urllib.urlencode(query)
		aircodes= urlopen('http://www.airlinecodes.co.uk/aptcoderes.asp',query,20)
		res=aircodes.read()
		if res.find('Sorry-No Results Found')!=-1:
			print apt, 'Error'
		idx=res.find('ICAO-Code:')
		if idx!=-1:
			code=res[idx+19:idx+23]
			print '\''+apt+'\''+':'+'\''+code+'\' ,'
		
	

		

if __name__ == "__main__":
	if len(sys.argv) <2:
		print 'Usage: generator.py gen | fp'
		sys.exit()
	else:
		if sys.argv[1]=='gen':
			generate()
		if sys.argv[1]=='fp':
			flight_plan()
	
