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

    print "length ", len(sys.argv)

    yearMin = int(sys.argv[1])
    yearMax = int(sys.argv[2])
    raceDistMin = float(sys.argv[3])-0.005
    raceDistMax = float(sys.argv[4])+0.005
    sexSelect = sys.argv[5]
    #print "raceDistMin ", raceDistMin, " raceDistMax ",raceDistMax

    #set up files
    fileName = sexSelect + "_paces_for_year_"+str(yearMin) + "_to_" + str(yearMax) + "_for_dist_" + str(raceDistMin) + "_to_" + str(raceDistMax) + ".dat"
    fle = open(fileName, 'wr')        
    fle.close()

    #for i in xrange(1,10000):
    for i in xrange(1, max_id+1): #go throught the racers to determine their ages
        cursor.execute("SELECT sex, distMiles, age, dateOfEvent, pacePerMile FROM nyrrRaceData WHERE id =" + str(int(i)) + ";")
        data=cursor.fetchall()
        currSex = data[0][0]
        currDist = data[0][1]
        currAge = data[0][2]
        try:
            year = data[0][3].year
        except:
            year = 1900 # if no obvious year just set it to something arbitrary
        pace = data[0][4]

        try:
            if currSex == sexSelect and currDist > raceDistMin and currDist < raceDistMax and year >= yearMin and year <= yearMax:
                fle = open(fileName, 'a')
                fle.write(str(pace) + "\n")
                fle.close()
        except:
            print "error parsing data"

    db.close()


main()
