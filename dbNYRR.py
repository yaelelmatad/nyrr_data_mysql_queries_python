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

    yearIncrement = int(sys.argv[1])
    ageIncrement = int(sys.argv[2])
    raceDistMin = float(sys.argv[3])-0.005
    raceDistMax = float(sys.argv[4])+0.005

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

        if currDist > 0.99:
            raceIndex = whichRace(currRaceName, currRaceDate)
            if (raceIndex==-1):
                raceMen.append([0]*101)
                raceWomen.append([0]*101)
                if currSex == 'm':
                    listOfRaces.append([currRaceName,currRaceDate,currDist,1,0]) #add 1 to men
                    raceMen[len(raceMen)-1][int(currAge)]=1
                else:
                    listOfRaces.append([currRaceName,currRaceDate,currDist,0,1]) #add 1 to women
                    raceWomen[len(raceWomen)-1][int(currAge)]=1
            else:
                if currSex == 'm':
                    raceMen[raceIndex][int(currAge)]=raceMen[raceIndex][int(currAge)] + 1
                    listOfRaces[raceIndex][3] = listOfRaces[raceIndex][3]+1
                else:
                    raceWomen[raceIndex][int(currAge)]=raceWomen[raceIndex][int(currAge)] + 1
                    listOfRaces[raceIndex][4]=listOfRaces[raceIndex][4]+1
    
    for race in range (0,len(listOfRaces)):
        print listOfRaces[race][2], listOfRaces[race][3], listOfRaces[race][4]

    menInAgeGroup = []
    womenInAgeGroup = []
    for year in range (1986,2013):
        menInAgeGroup.append(year)
        womenInAgeGroup.append(year)
        menInAgeGroup[len(menInAgeGroup)-1]=[]
        womenInAgeGroup[len(womenInAgeGroup)-1]=[]
        for age in range(0,101):
            menInAgeGroup[len(menInAgeGroup)-1].append(0)
            #print year, age, menInAgeGroup[len(menInAgeGroup)-1][age]
            womenInAgeGroup[len(womenInAgeGroup)-1].append(0)

    print "raceDistMin ", raceDistMin, " raceDistMax ",raceDistMax

    for race in range(0,len(listOfRaces)):
        if listOfRaces[race][3] > 0 and listOfRaces[race][4] > 0 and listOfRaces[race][2] > raceDistMin and listOfRaces[race][2] < raceDistMax:
            print "Race Included: ", listOfRaces[race][0], " date ", listOfRaces[race][1]
            #both men and women participated
            #year = listOfRaces[race][1].year
            #print year
            try:
                year=listOfRaces[race][1].year
                for age in range(0,101):
                    menInAgeGroup[yearIndex(year)][age] = menInAgeGroup[yearIndex(year)][age] + raceMen[race][age]
                    womenInAgeGroup[yearIndex(year)][age] = womenInAgeGroup[yearIndex(year)][age]+raceWomen[race][age]
                #print menInAgeGroup[yearIndex(year)]
                #print womenInAgeGroup[yearIndex(year)]
            except:
                print "Race Excluded due to year missing ", listOfRaces[race][0], " date ", listOfRaces[race][1]
        else:
            print "Race Excluded: ",listOfRaces[race][0], " date ", listOfRaces[race][1]


   # for year in range (1986,2013):
       # for age in range(0,101):
       #     print year,age, menInAgeGroup[yearIndex(year)][age], womenInAgeGroup[yearIndex(year)][age]


    groupedByYearAgeGroup=[]
    for minyear in range (1986, 2013-yearIncrement, yearIncrement):
        for minage in range (0,101-ageIncrement,ageIncrement):
            accumWomen = 0
            accumMen = 0
            for year in range (minyear, minyear+yearIncrement):
                for age in range (minage, minage+ageIncrement):
                    accumWomen = accumWomen +  womenInAgeGroup[yearIndex(year)][age]
                    accumMen = accumMen + menInAgeGroup[yearIndex(year)][age]
            #print float(minyear)+float(yearIncrement)/2.0, float(minage)+float(ageIncrement)/2, accumMen, accumWomen
            groupedByYearAgeGroup.append([float(minyear)+float(yearIncrement)/2.0, float(minage)+float(ageIncrement)/2, accumMen, accumWomen])
            #print groupedByYearAgeGroup[len(groupedByYearAgeGroup)-1][0], groupedByYearAgeGroup[len(groupedByYearAgeGroup)-1][1], groupedByYearAgeGroup[len(groupedByYearAgeGroup)-1][2], groupedByYearAgeGroup[len(groupedByYearAgeGroup)-1][3]

    #first we need to make hte files and clean the mout
    fileNames = []
    for i in range (0,len(groupedByYearAgeGroup)):
        yearFileName = "MW_from_year_"+str(float(groupedByYearAgeGroup[i][0])-float(yearIncrement)/2.0) + "_to_" + str(float(groupedByYearAgeGroup[i][0])+float(yearIncrement)/2.0)+".dat"

        #have we seen this file before?
        test = 0
        for filesAlready in range (0,len(fileNames)):
            if (fileNames[filesAlready] == yearFileName):
                test = 1
                break
        if test == 0: #erase the file if new and write to it the header
            fileNames.append(yearFileName)
            yearFile = open(yearFileName, 'wr')
            yearFile.write("#men women for years "+str(float(groupedByYearAgeGroup[i][0])-float(yearIncrement)/2.0) + " to " + str(float(groupedByYearAgeGroup[i][0])+float(yearIncrement)/2.0)+" for races longer than " +str(raceDistMin) + " but shorter than " + str(raceDistMax) +"\n" )
            yearFile.close()
        
        ageGroupFileName = "MW_from_ageGroup_"+str(float(groupedByYearAgeGroup[i][1]) - float(ageIncrement)/2.0) + "_to_" + str(float(groupedByYearAgeGroup[i][1])+float(ageIncrement)/2.0)+".dat"
        test = 0
        for filesAlready in range (0, len(fileNames)):
            if fileNames[filesAlready] == ageGroupFileName:
                test = 1
                break
        if test == 0:
            fileNames.append(ageGroupFileName)
            ageFile = open(ageGroupFileName, 'wr')
            ageFile.write("#men women for age group " + str(float(groupedByYearAgeGroup[i][1]) - float(ageIncrement)/2.0) + " to " + str(float(groupedByYearAgeGroup[i][1])+float(ageIncrement)/2.0)+" for races longer than " +str(raceDistMin) + " but shorter than " + str(raceDistMax)+"\n")
            ageFile.close()

    
    for i in range (0,len(groupedByYearAgeGroup)):
        yearFileName = "MW_from_year_"+str(float(groupedByYearAgeGroup[i][0])-float(yearIncrement)/2.0) + "_to_" + str(float(groupedByYearAgeGroup[i][0])+float(yearIncrement)/2.0)+".dat"
        ageGroupFileName = "MW_from_ageGroup_"+str(float(groupedByYearAgeGroup[i][1]) - float(ageIncrement)/2.0) + "_to_" + str(float(groupedByYearAgeGroup[i][1])+float(ageIncrement)/2.0)+".dat"
        yearFile = open(yearFileName, 'a')
        ageFile = open(ageGroupFileName, 'a')
        yearFile.write(str(groupedByYearAgeGroup[i][1]) + " " + str(groupedByYearAgeGroup[i][2]) + " " + str(groupedByYearAgeGroup[i][3]) + "\n")
        ageFile.write(str(groupedByYearAgeGroup[i][0]) + " " + str(groupedByYearAgeGroup[i][2]) + " " + str(groupedByYearAgeGroup[i][3]) + "\n")
        yearFile.close()
        ageFile.close()

    #f.write(str(groupedByYearAgeGroup[0][0]) + " " + str(groupedByYearAgeGroup[0][1]) + " " + str(groupedByYearAgeGroup[0][2]) + " " + str(groupedByYearAgeGroup[0][3]))

    db.close()

    



#main routine
main()
