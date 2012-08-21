import MySQLdb
import os, popen2
import sys

db = MySQLdb.connect(host="localhost", port=3306, user="root", db="nyrrData")
cursor = db.cursor()

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
    raceTimeCurr_seconds = 24*60+15
    racePaceCurr_seconds = raceTimeCurr_seconds/raceDistCurr_miles
    raceThreshold_years = 1
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

    for memNum in range(1,200):
        cursor.execute("SELECT pacePerMile, memberNumber, date FROM nyrrMemberData WHERE memberNumber = " + str(memNum) 
                + " and distMiles >= "  + str(lowRaceDistCurr_miles) + " and distMiles <= " + str(highRaceDistCurr_miles) 
                + " and pacePerMile >= " + str(lowRacePaceCurr_seconds)+ " and pacePerMile <= " + str(highRacePaceCurr_seconds) 
                )
        #        cursor.execute("SELECT pacePerMile FROM nyrrMemberData WHERE dateOfEvent >= '" + str(yearMin) + "0101000000' and dateOfEvent <= '" + str(yearMax) + "1231000000' and distMiles > " + str(raceDistMin) + " and distMiles < " + str(raceDistMax) + " and sex = '"+str(sexSelect)+"' and raceName not like '%walk%'")
        
        #now make sure those times are the lowest times in the area
        
        data=cursor.fetchone()
        #data=cursor.fetchall()
        
        if data:
            print data[0], data[1], data[2].month
        #while (data != None):
            #fle = open(fileName, 'a')
            #fle.write(str(data[0]) + "\n")
            #fle.close()
            #print data
            data = cursor.fetchone()
    
    db.close()


main()
