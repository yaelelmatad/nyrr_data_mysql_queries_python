import MySQLdb
import os, popen2
import sys


db = MySQLdb.connect(host="localhost", port=3306, user="root", db="nyrrData")
cursor = db.cursor()

global listOfRaces
listOfRaces = []

def whichRace(currRaceName, currRaceDate):
    global listOfRaces
    for race in range(0,len(listOfRaces)):
        if currRaceName == listOfRaces[race][0] and currRaceDate == listOfRaces[race][1]:
            return race

    return -1 #race not found, you should append it

def yearIndex(year):
    mappedyear = year-1986
    return mappedyear

def main():
    global listOfRaces
    cursor.execute("SELECT lastName, COUNT(lastName) FROM nyrrRaceData")
    size_of_data = cursor.fetchall()
    max_id = size_of_data[0][1]

    if len(sys.argv)!=6:
        print "script to query mysql nyrr database for women or men for races between raceDistMin and raceDistMax"
        print "for years between yearMin and yearMax (inclusive).  Requires 5 arguments as follows:" 
        print "python script_name yearMin yearMax raceDistMin raceDistMax Gender(m or f)"
        return

    yearMin = int(sys.argv[1])
    yearMax = int(sys.argv[2])
    raceDistMin = float(sys.argv[3])-0.005
    raceDistMax = float(sys.argv[4])+0.005
    sexSelect = sys.argv[5]
    #print "raceDistMin ", raceDistMin, " raceDistMax ",raceDistMax

    #set up files
    fileName = sexSelect + "_paces_for_year_"+str(yearMin) + "_to_" + str(yearMax) + "_for_dist_" + str(raceDistMin) + "_to_" + str(raceDistMax) + ".dat2"
    fle = open(fileName, 'wr')        
    fle.close()

    #for i in xrange(1,10000):
    #for i in xrange(1, max_id+1): #go throught the racers to determine their ages
    cursor.execute("SELECT pacePerMile FROM nyrrRaceData WHERE dateOfEvent >= '" + str(yearMin) + "0101000000' and dateOfEvent <= '" + str(yearMax) + "1231000000' and distMiles > " + str(raceDistMin) + " and distMiles < " + str(raceDistMax) + " and sex = '"+str(sexSelect)+"' and raceName not like '%walk%'")
        
    data=cursor.fetchone()

    while (data != None):
        fle = open(fileName, 'a')
        fle.write(str(data[0]) + "\n")
        fle.close()
        data = cursor.fetchone()
    db.close()


main()
