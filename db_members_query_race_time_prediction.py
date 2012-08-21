import MySQLdb
import os, popen2
import sys

db = MySQLdb.connect(host="localhost", port=3306, user="root", db="nyrrData")
cursor = db.cursor()


def getUpperDate(year, month, date, threshold_months):
    upperMonth = month + threshold_months
    upperYear = year
    while (upperMonth > 12):
        upperYear = upperYear + 1
        upperMonth = upperMonth - 12

    if upperMonth < 10:
        upperMonthStr = "0" + str(upperMonth)
    else:
        upperMonthStr = str(upperMonth)

    if date < 10:
        dateStr = "0" + str(date)
    else:
        dateStr = str(date)

    upperDateStr = str(upperYear) + upperMonthStr + dateStr + "060000"
    #print year, month, date, threshold_months
    #print upperDateStr

    return upperDateStr

def getLowerDate(year, month, date, threshold_months):
    lowerMonth = month - threshold_months
    lowerYear = year
    while (lowerMonth <= 0):
        lowerYear = lowerYear - 1
        lowerMonth = lowerMonth + 12

    if lowerMonth < 10:
        lowerMonthStr = "0" + str(lowerMonth)
    else:
        lowerMonthStr = str(lowerMonth)

    if date < 10:
        dateStr = "0" + str(date)
    else:
        dateStr = str(date)

    lowerDateStr = str(lowerYear) + lowerMonthStr + dateStr + "060000"
    #print year, month, date, threshold_months
    #print lowerDateStr

    return lowerDateStr

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

    for memNum in range(1000,4000):
        cursor.execute("SELECT pacePerMile, memberNumber, date, id FROM nyrrMemberData WHERE memberNumber = " + str(memNum) 
                + " and distMiles >= "  + str(lowRaceDistCurr_miles) + " and distMiles <= " + str(highRaceDistCurr_miles) 
                + " and pacePerMile >= " + str(lowRacePaceCurr_seconds)+ " and pacePerMile <= " + str(highRacePaceCurr_seconds) 
                )
        #        cursor.execute("SELECT pacePerMile FROM nyrrMemberData WHERE dateOfEvent >= '" + str(yearMin) + "0101000000' and dateOfEvent <= '" + str(yearMax) + "1231000000' and distMiles > " + str(raceDistMin) + " and distMiles < " + str(raceDistMax) + " and sex = '"+str(sexSelect)+"' and raceName not like '%walk%'")
        
        #now make sure those times are the lowest times in the area
        
        #data=cursor.fetchone()
        data=cursor.fetchall()
        
        #sort the data
        data = sorted(data, key=lambda dat:dat[0])
        
        i = 0
        while i <  len(data):
            #print data[i]
            cursor.execute("SELECT pacePerMile, memberNumber, date, id FROM nyrrMemberData WHERE memberNumber = " + str(memNum) 
                + " and distMiles >= "  + str(lowRaceDistCurr_miles) + " and distMiles <= " + str(highRaceDistCurr_miles) 
                + " and pacePerMile < " + str(data[i][0]) 
                + " and date > " + getLowerDate(data[i][2].year, data[i][2].month, data[i][2].day, raceThreshold_months)
                + " and date < " + getUpperDate(data[i][2].year, data[i][2].month, data[i][2].day, raceThreshold_months)
                )
            dataFaster = cursor.fetchall()
            #if there exists a faster time within the threshold amount of months, delete that entry.  recall that this changes the len(data)
            if len(dataFaster) > 0:
                del data[i]
            else: 
                # only want to add 1 to i if not deleting, otherwise use same index to get next element (since we'll have deleted the current i, the "next" element is what used to be at i+1 but now is at i
                #we know we want to use this data, so use it here.

                cursor.execute("SELECT pacePerMile, memberNumber FROM nyrrMemberData WHERE memberNumber = " + str(memNum) 
                    + " and distMiles >= "  + str(lowRaceDistPredict_miles) + " and distMiles <= " + str(highRaceDistPredict_miles) 
                    + " and date > " + getLowerDate(data[i][2].year, data[i][2].month, data[i][2].day, raceThreshold_months)
                    + " and date < " + getUpperDate(data[i][2].year, data[i][2].month, data[i][2].day, raceThreshold_months)
                    )

                dataPredict = cursor.fetchall()
                dataPredict = sorted(dataPredict, key=lambda pace:pace[0])
                if dataPredict:
                    print int(dataPredict[0][0])
                
                i = i + 1


            #fle = open(fileName, 'a')
            #fle.write(str(data[0]) + "\n")
            #fle.close()


    #print data
    
    db.close()


main()
