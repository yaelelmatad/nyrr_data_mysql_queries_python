import MySQLdb
import os, popen2
import sys

db = MySQLdb.connect(host="localhost", port=3306, user="root", db="nyrrData")
cursor = db.cursor()

def main():
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

    #set up files
    fileName = sexSelect + "_paces_for_year_"+str(yearMin) + "_to_" + str(yearMax) + "_for_dist_" + str(raceDistMin) + "_to_" + str(raceDistMax) + ".dat2"
    fle = open(fileName, 'wr')        
    fle.close()

    cursor.execute("SELECT pacePerMile FROM nyrrRaceData WHERE dateOfEvent >= '" + str(yearMin) + "0101000000' and dateOfEvent <= '" + str(yearMax) + "1231000000' and distMiles > " + str(raceDistMin) + " and distMiles < " + str(raceDistMax) + " and sex = '"+str(sexSelect)+"' and raceName not like '%walk%'")
        
    data=cursor.fetchone()

    while (data != None):
        fle = open(fileName, 'a')
        fle.write(str(data[0]) + "\n")
        fle.close()
        data = cursor.fetchone()
    db.close()


main()
