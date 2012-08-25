import MySQLdb
import os, popen2
import sys
import math
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

        # chec kfor faster races
        i = 0
        while i < len(atpace):
            fasterFlag = 0 #no faster time found yet
            for j in range (0, len(faster)): #check the faster races
                if dateInRange(atpace[i],faster[j],raceThreshold_months) == 1:
                    fasterFlag = 1
                    break
            
            if fasterFlag != 1: #if no faster race found yet in the time span
                for j in range (0,i): #check the at pace races
                    if dateInRange(atpace[i],atpace[j],raceThreshold_months) == 1:
                        fasterFlag = 1
                        break

            if fasterFlag == 1:
                del atpace[i]
            else:
                i = i + 1
        return atpace
                        

#some useful functions for dealing with date ranges  

def dateInRange(firstDatetime, secondDatetime, raceThreshold_months):
    upperDatetime=getUpperDate(firstDatetime.year, firstDatetime.month, firstDatetime.day, raceThreshold_months)
    lowerDatetime=getLowerDate(firstDatetime.year, firstDatetime.month, firstDatetime.day, raceThreshold_months)
    
    if (secondDatetime < upperDatetime and secondDatetime > lowerDatetime):
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

def main():
    #if len(sys.argv)!=6:
    #    print "script to query mysql nyrr member database for racetime prediction"
    #    print "for years between yearMin and yearMax (inclusive).  Requires 5 arguments as follows:" 
    #    print "python script_name yearMin yearMax raceDistMin raceDistMax Gender(m or f)"
    #    return

    
    
    raceDistList = [3.1,4.0,5.0,6.2,9.3,13.1,26.2]
    #raceDistList = [3.1,6.2,13.1]
    racePaceStart_sec = 4*60 
    racePaceEnd_sec = 14*60
    racePaceInc = 5
    totalPaces = (racePaceEnd_sec - racePaceStart_sec) / racePaceInc + 1
    raceThreshold_months = 6
    timeThreshold_seconds = 2.5
    tiny = 0.10001 #this will get 3.0 and 3.1 in same shot
 
    #yearMax = int(sys.argv[2])
    #raceDistMin = float(sys.argv[3])-0.005
    #sexSelect = sys.argv[5]

    accum= [] #running accumlator
    accum2 =[] #running accumulator (squared)
    totalPts = []
    for fromIndex in range (0, len(raceDistList)):
        raceDistCurr_miles = raceDistList[fromIndex]
        toIndex = 0 
        toRacesTemp = [] 
        toRacesTemp2 = []
        toRacesTemp3 = []
        while toIndex < len(raceDistList):
            pacesTemp = []
            pacesTemp2 = []
            pacesTemp3 = []
            if toIndex != fromIndex: 
                for racePaceCurr_seconds in range (racePaceStart_sec, racePaceEnd_sec, racePaceInc):
                    raceDistPredict_miles = raceDistList[toIndex]
                    fileName = "colDat_from_" + str(raceDistCurr_miles) + "_to_"+ str(raceDistPredict_miles) + "_miles_for_pace_" + str(racePaceCurr_seconds) + ".dat"
                    fle = open(fileName, 'wr')        
                    fle.close()
                    pacesTemp.append(0)
                    pacesTemp2.append(0)
                    pacesTemp3.append(0)
            toRacesTemp.append(pacesTemp)
            toRacesTemp2.append(pacesTemp2)
            toRacesTemp3.append(pacesTemp3)
            toIndex = toIndex + 1
        #set up accum to be zero
        accum.append(toRacesTemp)
        accum2.append(toRacesTemp2)
        totalPts.append(toRacesTemp3)
        accumNorm = 9*60
        accum2Norm = 9*60*9*60 #so numbers in ararys dont' go insane

    #print totalPts

    paceIndex = 0
    distIndex = 1
    memberIndex = 2
    dateIndex = 3
    numData = 4 #lenght of excpected data

    memberList = []
    for memNum in range(0,10):
    #for memNum in range(0,10):
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
            
            # HERE BE THE LOOPS!
            
            for fromIndex in range (0, len(raceDistList)):
                raceDistCurr_miles = raceDistList[fromIndex]
                toIndex = 0 
                while toIndex < len(raceDistList):
                    if toIndex != fromIndex: 
                        speedIndex = 0
                        for racePaceCurr_seconds in range (racePaceStart_sec, racePaceEnd_sec, racePaceInc):
                            raceDistPredict_miles = raceDistList[toIndex]
                            fileName = "colDat_from_" + str(raceDistCurr_miles) + "_to_"+ str(raceDistPredict_miles) + "_miles_for_pace_" + str(racePaceCurr_seconds) + ".dat"
                            highRaceDistCurr_miles = raceDistCurr_miles + tiny
                            lowRaceDistCurr_miles = raceDistCurr_miles - tiny
                            lowRaceDistPredict_miles = raceDistPredict_miles- tiny
                            highRaceDistPredict_miles = raceDistPredict_miles + tiny
                            lowRacePaceCurr_seconds = racePaceCurr_seconds - timeThreshold_seconds
                            highRacePaceCurr_seconds = racePaceCurr_seconds + timeThreshold_seconds

                            #print lowRaceDistCurr_miles
                            #print highRaceDistCurr_miles
                            #print lowRaceDistPredict_miles
                            #print highRaceDistPredict_miles
                            #print lowRacePaceCurr_seconds
                            #print highRacePaceCurr_seconds

                            fastestDatetimes = memberList[index].findFastestAtPace(lowRacePaceCurr_seconds, highRacePaceCurr_seconds, 
                                    lowRaceDistCurr_miles,highRaceDistCurr_miles,raceThreshold_months,distIndex,paceIndex,dateIndex)
                            #print "fastest_dates"
                            #print fastestDatetimes

                            for i in range(0,len(fastestDatetimes)):
                                corrData = memberList[index].findFastestPaceInDateRange(lowRaceDistPredict_miles, highRaceDistPredict_miles, 
                                        fastestDatetimes[i], raceThreshold_months, distIndex, paceIndex, dateIndex)
                                if corrData != "":
                                    #print "corrData"
                                    #print corrData
                                    fle = open(fileName, 'a') 
                                    fle.write(str(corrData) + "\n")
                                    fle.close()
                                    accum[fromIndex][toIndex][speedIndex] = accum[fromIndex][toIndex][speedIndex] + float(corrData)/accumNorm
                                    accum2[fromIndex][toIndex][speedIndex] = accum2[fromIndex][toIndex][speedIndex] + float(corrData)*float(corrData)/accum2Norm
                                    totalPts[fromIndex][toIndex][speedIndex]=totalPts[fromIndex][toIndex][speedIndex]+1
                                    #print totalPts
                            speedIndex = speedIndex + 1
                    toIndex = toIndex + 1
                #set up accum to be zero

            #print accum
            #print totalPts

            
            
            #set up files
            #fileName = sexSelect + "_paces_for_year_"+str(yearMin) + "_to_" + str(yearMax) + "_for_dist_" + str(raceDistMin) + "_to_" + str(raceDistMax) + ".dat2"
            #fle = open(fileName, 'wr')        
            #fle.close()

            #fle = open(fileName, 'a')
            #fle.write(str(data[0]) + "\n")
            #fle.close()

    fileName = "avgs.dat"
    fle = open(fileName, 'wr')
    fle.close()

    fle = open(fileName, 'a') 
    for fromIndex in range (0, len(raceDistList)):
        raceDistCurr_miles = raceDistList[fromIndex]
        toIndex = 0 
        while toIndex < len(raceDistList):
            if toIndex != fromIndex: 
                speedIndex = 0
                for racePaceCurr_seconds in range (racePaceStart_sec, racePaceEnd_sec, racePaceInc):
                    raceDistPredict_miles = raceDistList[toIndex]
                    fileName = "avgs.dat"
                    if (totalPts[fromIndex][toIndex][speedIndex] > 0):
                        avg = (accum[fromIndex][toIndex][speedIndex]/float(totalPts[fromIndex][toIndex][speedIndex]))*accumNorm
                        avg2 = (accum2[fromIndex][toIndex][speedIndex]/float(totalPts[fromIndex][toIndex][speedIndex]))*accum2Norm
                        var = avg2 - avg*avg
                        if var < 0:
                            if var > -0.001: #deal with floating point errors when avg2 = avg*avg
                                var = 0
                            else:
                                print "var less than zero " , var
                                print avg2, avg*avg
                        stdev = math.sqrt(var)
                        fle.write(str(raceDistCurr_miles) + " " + str(raceDistPredict_miles) + " " + str(racePaceCurr_seconds) + " " + str(avg) + " " + str(stdev))
                        fle.write("\n")
                    speedIndex = speedIndex + 1
            toIndex = toIndex + 1
        #set up accum to be zero

    fle.close()
    db.close()


main()
