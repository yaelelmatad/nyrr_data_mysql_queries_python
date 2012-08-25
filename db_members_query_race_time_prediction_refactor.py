import MySQLdb
import os, popen2
import sys
from operator import itemgetter, attrgetter
from datetime import datetime

db = MySQLdb.connect(host="localhost", port=3306, user="root", db="nyrrData")
cursor = db.cursor()




class NyrrMember:
    def _init_(self, raceData = [], sortBy1 = 0, lengthCheck = 4):
        self.myRaceData = raceData
        i = 0
        while i < len(self.myRaceData):
            if len(self.myRaceData[i]) == lengthCheck:
                i= i+1
            else:
                print "deleted ", self.myRaceData[i]
                del self.myRaceData[i]


        self.mySortBy1 = sortBy1
        self.mySortBy2 = sortBy1
        #figure out which element you want to sort by
        self.myRaceData = sorted(self.myRaceData, key=itemgetter(sortBy1))
    def sortData(self,sortBy):
        self.mySortBy1 = sortBy1
        self.myRaceData = sorted(self.myRaceData, key=itemgetter(sortBy1))
    def multSortData(self,sortBy1,sortBy2):
        self.mySortBy1 = sortBy1
        self.mySortBy2 = sortBy2
        self.myRaceData = sorted(self.myRaceData,key=itemgetter(sortBy1,sortBy2))
    def printRaceData(self):
        print self.myRaceData
    def getRaceData(self, lowDist, highDist, distIndex, speedIndex):
        #make sure data is sorted by race distance
        if self.mySortBy1 != distIndex or self.mySortBy2 != speedIndex:
            self.multSortData(distIndex, speedIndex)
            #self.myRaceData = sorted(self.myRaceDat, key=itemgetter(sortBy1))
        thisDist = []
        i = 0 
        while i < len(self.myRaceData) and self.myRaceData[i][distIndex] < lowDist:
            i = i + 1
        while i < len (self.myRaceData) and self.myRaceData[i][distIndex] < highDist:
            thisDist.append(self.myRaceData[i])
            i = i + 1
        #if thisDist:
        #    print thisDist
        return thisDist
    def findFastestPaceInDateRange(self, lowD, highD, currDatetime, raceThreshold_months, distIndex, paceIndex, dateIndex):
        races = self.getRaceData(lowD,highD,distIndex,paceIndex)
        for i in range(0,len(races)):
            if dateInRange(races[i][dateIndex],currDatetime,raceThreshold_months) == 1:
                return races[i][paceIndex]
        #none fond so return 0
        return ""
                


    def findFastestAtPace(self, lowPace, highPace, lowD,highD,raceThreshold_months,distIndex,paceIndex,dateIndex):
        races = self.getRaceData(lowD,highD,distIndex,paceIndex)
        faster = []
        atpace = []
        i = 0
        #print races
        while i < len(races) and races[i][paceIndex] < lowPace:
            faster.append(races[i][dateIndex])
            #faster.append(races[i])
            i = i + 1
        while i< len(races) and races[i][paceIndex] < highPace:
            atpace.append(races[i][dateIndex])
            #atpace.append(races[i])
            i = i + 1

        #if atpace:
            #if faster:
                #print "faster"
                #print faster
            #print "at pace"
            #print atpace
        

        # chec kfor faster races
        i = 0
        while i < len(atpace):
            fasterFlag = 0 #no faster time found yet
            for j in range (0, len(faster)): #check the faster races
                #print "check"
                #print atpace[i][dateIndex]
                #print faster[j][dateIndex]
                if dateInRange(atpace[i],faster[j],raceThreshold_months) == 1:
                #if dateInRange(atpace[i][dateIndex],faster[j][dateIndex],raceThreshold_months) == 1:
                    fasterFlag = 1
                    break
            
            if fasterFlag != 1: #if no faster race found yet in the time span
                for j in range (0,i): #check the at pace races
                    if dateInRange(atpace[i],atpace[j],raceThreshold_months) == 1:
                    #if dateInRange(atpace[i][dateIndex],atpace[j][dateIndex],raceThreshold_months) == 1:
                        fasterFlag = 1
                        break

            if fasterFlag == 1:
                del atpace[i]
            else:
                i = i + 1

        #if atpace:
            #print "at pace after"
            #print atpace

        return atpace
                        

  

def dateInRange(firstDatetime, secondDatetime, raceThreshold_months):
    upperDatetime=getUpperDate(firstDatetime.year, firstDatetime.month, firstDatetime.day, raceThreshold_months)
    lowerDatetime=getLowerDate(firstDatetime.year, firstDatetime.month, firstDatetime.day, raceThreshold_months)
    
    if (secondDatetime < upperDatetime and secondDatetime > lowerDatetime):
        #print secondDatetime
        #print upperDatetime
        #print lowerDatetime
        return 1
    else:
        return 0
         

def getUpperDate(year, month, date, threshold_months):
    upperMonth = month + threshold_months
    upperYear = year
    while (upperMonth > 12):
        upperYear = upperYear + 1
        upperMonth = upperMonth - 12

    if upperMonth == 2 and date > 28:
        date = 28
    elif date > 30:
        date = 30

    upperDatetime = datetime(upperYear, upperMonth, date, 06, 00, 00)
    return upperDatetime

def getLowerDate(year, month, date, threshold_months):
    lowerMonth = month - threshold_months
    lowerYear = year
    while (lowerMonth <= 0):
        lowerYear = lowerYear - 1
        lowerMonth = lowerMonth + 12

    if lowerMonth == 2 and date > 28:
        date = 28
    elif date > 30:
        date = 30

    lowerDatetime = datetime(lowerYear, lowerMonth, date, 06, 00, 00)
    return lowerDatetime
    #lowerDateStr = str(lowerYear) + lowerMonthStr + dateStr + "060000"
    #print year, month, date, threshold_months
    #print lowerDateStr

    #return [lowerYear, lowerMonth, date]
    #return lowerDateStr

def main():
    #if len(sys.argv)!=6:
    #    print "script to query mysql nyrr member database for racetime prediction"
    #    print "for years between yearMin and yearMax (inclusive).  Requires 5 arguments as follows:" 
    #    print "python script_name yearMin yearMax raceDistMin raceDistMax Gender(m or f)"
    #    return

    raceDistCurr_miles = 3.1
    tiny = 0.0001
    highRaceDistCurr_miles = raceDistCurr_miles + tiny
    lowRaceDistCurr_miles = raceDistCurr_miles - tiny
    raceDistPredict_miles = 6.2
    lowRaceDistPredict_miles = 6.2 - tiny
    highRaceDistPredict_miles = 6.2 + tiny
    raceTimeCurr_seconds = 24*60+15
    racePaceCurr_seconds = raceTimeCurr_seconds/raceDistCurr_miles
    #racePaceCurr_seconds = 470 
    raceThreshold_months = 6
    timeThreshold_seconds = 5
    lowRacePaceCurr_seconds = racePaceCurr_seconds - timeThreshold_seconds
    highRacePaceCurr_seconds = racePaceCurr_seconds + timeThreshold_seconds
    #yearMin = int(sys.argv[1])
    #yearMax = int(sys.argv[2])
    #raceDistMin = float(sys.argv[3])-0.005
    #raceDistMax = float(sys.argv[4])+0.005
    #sexSelect = sys.argv[5]

    #set up files
    #fileName = sexSelect + "_paces_for_year_"+str(yearMin) + "_to_" + str(yearMax) + "_for_dist_" + str(raceDistMin) + "_to_" + str(raceDistMax) + ".dat2"
    #fle = open(fileName, 'wr')        
    #fle.close()

    

    paceIndex = 0
    distIndex = 1
    memberIndex = 2
    dateIndex = 3
    numData = 4 #lenght of excpected data

    memberList = []
    for memNum in range(0,125000):
        cursor.execute("SELECT pacePerMile, distMiles, memberNumber, date FROM nyrrMemberData WHERE memberNumber = " + str(memNum) 
                #+ " and distMiles >= "  + str(lowRaceDistCurr_miles) + " and distMiles <= " + str(highRaceDistCurr_miles) 
                #+ " and pacePerMile >= " + str(lowRacePaceCurr_seconds)+ " and pacePerMile <= " + str(highRacePaceCurr_seconds) 
                )
        

        data=cursor.fetchall()
        
        if len(data) >= 2:
            tempMember = NyrrMember()
            tempMember._init_(data, distIndex, numData)
            tempMember.multSortData(distIndex, paceIndex)
            memberList.append(tempMember)
            index = len(memberList)-1
            #raceData = memberList[index].getRaceData(lowRaceDistCurr_miles,highRaceDistCurr_miles,distIndex,paceIndex)
            fastestDatetimes = memberList[index].findFastestAtPace(lowRacePaceCurr_seconds, highRacePaceCurr_seconds, lowRaceDistCurr_miles,highRaceDistCurr_miles,raceThreshold_months,distIndex,paceIndex,dateIndex)
            for i in range(0,len(fastestDatetimes)):
                corrData = memberList[index].findFastestPaceInDateRange(lowRaceDistPredict_miles, highRaceDistPredict_miles, fastestDatetimes[i], raceThreshold_months, distIndex, paceIndex, dateIndex)
                if corrData != "":
                    print corrData

#for i in range(0,len(memberList)):
        #raceData = memberList[i].getRaceData(lowRaceDistCurr_miles,highRaceDistCurr_miles,distIndex,paceIndex)
        #if raceData:
        #    print len(raceData)

    #now make sure those times are the lowest times in the area
    #for i in range(0,len(memberList)):
    #    fastestData = memberList[i].findFastestAtPace(lowRacePaceCurr_seconds, highRacePaceCurr_seconds, lowRaceDistCurr_miles,highRaceDistCurr_miles,raceThreshold_months,distIndex,paceIndex,dateIndex)


    
        #sort the data
        

            #fle = open(fileName, 'a')
            #fle.write(str(data[0]) + "\n")
            #fle.close()


    #print data
    
    db.close()


main()
