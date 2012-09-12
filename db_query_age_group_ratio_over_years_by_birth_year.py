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
    if len(sys.argv) < 5:
        print "Code requires following arguments"
        print "yearInc, birthYearInc, raceDistMin, raceDistMax"
        return
    
    global listOfRaces
    cursor.execute("SELECT lastName, COUNT(lastName) FROM nyrrRaceData")
    size_of_data = cursor.fetchall()
    max_id = size_of_data[0][1]


    minBirthYear = 1890
    maxBirthYear = 2012
    birthRange = maxBirthYear - minBirthYear
    
    yearIncrement = int(sys.argv[1])
    birthYearIncrement = int(sys.argv[2])
    raceDistMin = float(sys.argv[3])-0.005
    raceDistMax = float(sys.argv[4])+0.005

    print "input"
    print "yearInc", yearIncrement
    print "birthYearInc", birthYearIncrement
    print "raceDistMin", raceDistMin
    print "raceDistMax", raceDistMax
    
    sys.stdout.flush()

    raceMen = []
    raceWomen = []

    #for i in xrange(1,10000):
    for i in xrange(1, max_id+1): #go throught the racers to determine their ages
        cursor.execute("SELECT raceName, dateOfEvent, sex, distMiles, age FROM nyrrRaceData WHERE id =" + str(int(i)) + ";")
        data=cursor.fetchall()
        currRaceName = data[0][0]
        currRaceDate = data[0][1]
        currSex = data[0][2]
        currDist = data[0][3]
        currAge = data[0][4]
        try:
            currBirthYear = currRaceDate.year - int(currAge)
        except:
            #ok because not going to get computed anyway
            currBirthYear = maxBirthYear-1 

        if currDist > 0.99:
            raceIndex = whichRace(currRaceName, currRaceDate)
            if (raceIndex==-1):
                raceMen.append([0]*birthRange)
                raceWomen.append([0]*birthRange)
                if currSex == 'm':
                    listOfRaces.append([currRaceName,currRaceDate,currDist,1,0]) #add 1 to men
                    try:
                        raceMen[len(raceMen)-1][currBirthYear - minBirthYear]=1
                    except:
                        print currBirthyear
                        print minBirthYear
                    #raceMen[len(raceMen)-1][int(currAge)]=1
                else:
                    listOfRaces.append([currRaceName,currRaceDate,currDist,0,1]) #add 1 to women
                    raceWomen[len(raceWomen)-1][currBirthYear - minBirthYear]=1
                    #raceWomen[len(raceWomen)-1][int(currAge)]=1
            else:
                if currSex == 'm':
                    #raceMen[raceIndex][int(currAge)]=raceMen[raceIndex][int(currAge)] + 1
                    raceMen[raceIndex][currBirthYear - minBirthYear] = raceMen[raceIndex][currBirthYear - minBirthYear] + 1
                    listOfRaces[raceIndex][3] = listOfRaces[raceIndex][3]+1
                else:
                    #raceWomen[raceIndex][int(currAge)]=raceWomen[raceIndex][int(currAge)] + 1
                    raceWomen[raceIndex][currBirthYear - minBirthYear]=raceWomen[raceIndex][currBirthYear - minBirthYear] + 1
                    listOfRaces[raceIndex][4]=listOfRaces[raceIndex][4]+1
    
    #for race in range (0,len(listOfRaces)):
    #    print listOfRaces[race][2], listOfRaces[race][3], listOfRaces[race][4]

#EDITING STARTS HERE  9/7/2012

    menInAgeGroup = []
    womenInAgeGroup = []
    for year in range (1986,2013):
        menInAgeGroup.append(year)
        womenInAgeGroup.append(year)
        menInAgeGroup[len(menInAgeGroup)-1]=[]
        womenInAgeGroup[len(womenInAgeGroup)-1]=[]
        for birthYear in range(0,birthRange):
            menInAgeGroup[len(menInAgeGroup)-1].append(0)
            #print year, age, menInAgeGroup[len(menInAgeGroup)-1][age]
            womenInAgeGroup[len(womenInAgeGroup)-1].append(0)

    #print "raceDistMin ", raceDistMin, " raceDistMax ",raceDistMax

    for race in range(0,len(listOfRaces)):
        if listOfRaces[race][3] > 0 and listOfRaces[race][4] > 0 and listOfRaces[race][2] > raceDistMin and listOfRaces[race][2] < raceDistMax:
            print "Race Included: ", listOfRaces[race][0], " date ", listOfRaces[race][1]
            #both men and women participated
            #year = listOfRaces[race][1].year
            #print year
            try:
                year=listOfRaces[race][1].year
                for yearShifted in range(0,birthRange):
                    menInAgeGroup[yearIndex(year)][yearShifted] = menInAgeGroup[yearIndex(year)][yearShifted] + raceMen[race][yearShifted]
                    womenInAgeGroup[yearIndex(year)][yearShifted] = womenInAgeGroup[yearIndex(year)][yearShifted]+raceWomen[race][yearShifted]
            except:
                print "Race Excluded due to year missing ", listOfRaces[race][0], " date ", listOfRaces[race][1]
        else:
            print "Race Excluded: ",listOfRaces[race][0], " date ", listOfRaces[race][1]
            print "Number of male,female participants", listOfRaces[race][3], listOfRaces[race][4]
            print "Race Distance: ",listOfRaces[race][2]


   # for year in range (1986,2013):
       # for age in range(0,101):
       #     print year,age, menInAgeGroup[yearIndex(year)][age], womenInAgeGroup[yearIndex(year)][age]


    groupedByYearBirthYear=[]
    for minyear in range (1986, 2013-yearIncrement, yearIncrement):
        for minBirthYearIndex in range (0,101-birthYearIncrement,birthYearIncrement):
            accumWomen = 0
            accumMen = 0
            for year in range (minyear, minyear+yearIncrement):
                for birthYear in range (minBirthYearIndex, minBirthYearIndex+birthYearIncrement):
                    accumWomen = accumWomen +  womenInAgeGroup[yearIndex(year)][birthYear]
                    accumMen = accumMen + menInAgeGroup[yearIndex(year)][birthYear]
            #print float(minyear)+float(yearIncrement)/2.0, float(minage)+float(birthYearIncrement)/2, accumMen, accumWomen
            groupedByYearBirthYear.append([float(minyear)+float(yearIncrement)/2.0, float(minBirthYearIndex)+float(birthYearIncrement)/2, accumMen, accumWomen])
            #print groupedByYearBirthYear[len(groupedByYearBirthYear)-1][0], groupedByYearBirthYear[len(groupedByYearBirthYear)-1][1], groupedByYearBirthYear[len(groupedByYearBirthYear)-1][2], groupedByYearBirthYear[len(groupedByYearBirthYear)-1][3]

    #first we need to make hte files and clean the mout
    fileNames = []
    for i in range (0,len(groupedByYearBirthYear)):
        yearFileName = "MW_from_year_"+str(float(groupedByYearBirthYear[i][0])-float(yearIncrement)/2.0) + "_to_" + str(float(groupedByYearBirthYear[i][0])+float(yearIncrement)/2.0)+".dat"

        #have we seen this file before?
        test = 0
        for filesAlready in range (0,len(fileNames)):
            if (fileNames[filesAlready] == yearFileName):
                test = 1
                break
        if test == 0: #erase the file if new and write to it the header
            fileNames.append(yearFileName)
            yearFile = open(yearFileName, 'wr')
            yearFile.write("#men women for years "+str(float(groupedByYearBirthYear[i][0])-float(yearIncrement)/2.0) + " to " + str(float(groupedByYearBirthYear[i][0])+float(yearIncrement)/2.0)+" for races longer than " +str(raceDistMin) + " but shorter than " + str(raceDistMax) +"\n" )
            yearFile.close()
        
        ageGroupFileName = "MW_from_birthYear_"+str(minBirthYear + float(groupedByYearBirthYear[i][1]) - float(birthYearIncrement)/2.0) + "_to_" + str(minBirthYear + float(groupedByYearBirthYear[i][1])+float(birthYearIncrement)/2.0)+".dat"
        test = 0
        for filesAlready in range (0, len(fileNames)):
            if fileNames[filesAlready] == ageGroupFileName:
                test = 1
                break
        if test == 0:
            fileNames.append(ageGroupFileName)
            ageFile = open(ageGroupFileName, 'wr')
            ageFile.write("#men women for birth year from " + str(minBirthYear + float(groupedByYearBirthYear[i][1]) - float(birthYearIncrement)/2.0) + " to " + str(minBirthYear + float(groupedByYearBirthYear[i][1])+float(birthYearIncrement)/2.0)+" for races longer than " +str(raceDistMin) + " but shorter than " + str(raceDistMax)+"\n")
            ageFile.close()

    
    for i in range (0,len(groupedByYearBirthYear)):
        yearFileName = "MW_from_year_"+str(float(groupedByYearBirthYear[i][0])-float(yearIncrement)/2.0) + "_to_" + str(float(groupedByYearBirthYear[i][0])+float(yearIncrement)/2.0)+".dat"
        ageGroupFileName = "MW_from_birthYear_"+str(minBirthYear + float(groupedByYearBirthYear[i][1]) - float(birthYearIncrement)/2.0) + "_to_" + str(minBirthYear + float(groupedByYearBirthYear[i][1])+float(birthYearIncrement)/2.0)+".dat"
        yearFile = open(yearFileName, 'a')
        ageFile = open(ageGroupFileName, 'a')
        yearFile.write(str(groupedByYearBirthYear[i][1] + minBirthYear) + " " + str(groupedByYearBirthYear[i][2]) + " " + str(groupedByYearBirthYear[i][3]) + "\n")
        ageFile.write(str(groupedByYearBirthYear[i][0]) + " " + str(groupedByYearBirthYear[i][2]) + " " + str(groupedByYearBirthYear[i][3]) + "\n")
        yearFile.close()
        ageFile.close()

    #f.write(str(groupedByYearBirthYear[0][0]) + " " + str(groupedByYearBirthYear[0][1]) + " " + str(groupedByYearBirthYear[0][2]) + " " + str(groupedByYearBirthYear[0][3]))

    db.close()

    



#main routine
main()
