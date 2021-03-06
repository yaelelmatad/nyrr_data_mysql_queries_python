import sys, os, re
import collections 

class Data(object):
    '''Data class, members include a dictionary (of dicts), a first label (birthyear or raceyear) a second label (same) as well as max and min for each of those years'''
    def __init__(self,allData, firstLabel,secondLabel):
        self.allData = allData
        self.firstKeyLabel = firstLabel
        self.secondKeyLabel = secondLabel
        self.minFirstKey = min(allData.keys())
        self.maxFirstKey = max(allData.keys())
        self.maxSecondKey = max([max(allData[year].keys()) for year in allData.keys()])
        self.minSecondKey = min([min(allData[year].keys()) for year in allData.keys()])



def loadFile(filename):
    '''for a give data file returns a dictionary with a nested dictionary for gender
    {1987: {'w': 34, 'm': 17}, 1988: {...},...},'''
    f = open(filename,'r')
    f.next() #the first line is dead to me
    dataSlice = {}
    for line in f:
        (year, men, women) = [int(float(x)) for x in line.split()]
        dataSlice[year] = {'M': men, 'W': women} 
    #print dataSlice
    return dataSlice


def loadAllFiles(files):
    '''loads all the files in the file list, extracts the year from the file name, and calls loadFile on single files'''
    allData = {}
    for f in files:
        year = int([year for year in re.findall(r'\d+', '%s' %(f)) if year != '0'][0])
        allData[year] = loadFile(f)

    #print allData
    return allData
    #print allData


def smoothed(allTheData, firstYearIncrement, secondYearIncrement):
    '''Given a data type, an incrememtn for the first type of year, and one of the second re "bins" the data so can be printed out as desired'''
    firstMin = allTheData.minFirstKey    
    firstMax = allTheData.maxFirstKey
    
    secondMin = allTheData.minSecondKey
    secondMax = allTheData.maxSecondKey

    smoothedData = {}

    nFirstBins = (firstMax - firstMin)/firstYearIncrement + 1
    nSecondBins = (secondMax - secondMin)/secondYearIncrement + 1 
    
    leftFirstBin = [firstMin + x*firstYearIncrement for x in range(nFirstBins)]
    leftSecondBin = [secondMin + x*secondYearIncrement for x in range(nSecondBins)]
    
    for left1Bin in leftFirstBin:
        smoothedData[left1Bin, left1Bin+firstYearIncrement] = {}
        for left2Bin in leftSecondBin:
            smoothedData[left1Bin, left1Bin+firstYearIncrement][left2Bin, left2Bin + secondYearIncrement] = {'M': 0, 'W': 0}
    
    for left1Key, right1Key in smoothedData:
        for left2Key, right2Key in smoothedData[left1Key, right1Key]:
            for year1 in range(left1Key, min(right1Key,firstMax+1)):
                for year2 in range(left2Key,min(right2Key,secondMax+1)):
                    for gender in ('M','W'):
                        smoothedData[left1Key,right1Key][left2Key, right2Key][gender] += allTheData.allData[year1][year2][gender]



    return smoothedData
    

def printData(allTheData,smoothedData):
    '''after rebinning, prints data, must pass it original data class as well as smoothed data'''
    if allTheData.firstKeyLabel == 'birthyear':
        dirName = 'reBinnedByBirthYear'
        fileNamePrefix = "for_birthyears_"
    if allTheData.firstKeyLabel == 'raceyear':
        dirName = 'reBinnedByRaceYear' 
        fileNamePrefix = "for_raceyears_"
    
    #makes a directory if it doesn't fine that directory already
    if not os.path.isdir('./'+dirName):
        os.makedirs('./'+dirName)

    #here is where you write out all the smoothedData stuff.
    for left1Key, right1Key in smoothedData:
        filename = dirName + '/' + fileNamePrefix + str(left1Key) +'_to_' +str(right1Key)+'.dat'
        print filename
        f = open(filename,'w')
        f.write("#Data for birth years in range" + str(left1Key) + " to " + str(right1Key) + "\n")
        f.write("#Data for race years in range [Year1, Year2) for M and then W \n")
        f.write("#Year1  Year2  MenRacers  WomenRacers \n")
        f.close

        sortedKeys = sorted(smoothedData[left1Key, right1Key].keys())
        for left2Key, right2Key in sortedKeys:
            f.write(str(left2Key) + " " + str(right2Key) + " " + str(smoothedData[left1Key, right1Key][left2Key, right2Key]['M']) + " " + str(smoothedData[left1Key, right1Key][left2Key, right2Key]['W']) + "\n")
        f.close






def main():

    if len(sys.argv) == 1:
        '''for small debugs'''
        firstKey = "birthyear"
        secondKey = "raceyear"
        fileString = "MW_from_birthYear_1975.0_to_1976.0.dat"
        #print loadFile("MW_from_birthYear_1975.0_to_1976.0.dat")
    
    elif len(sys.argv) == 4:
        fileString = sys.argv[1]
        firstKey = sys.argv[2]
        secondKey = sys.argv[3]
        if not (firstKey == 'birthyear' and secondKey == 'raceyear') and not (firstKey == 'raceyear' and secondKey == 'birthyear'):
            print "please give mevalue keys which are raceyear, birthyear or birthyear, raceyear ONLY"
            sys.exit(1)

    else:
        print "please give me 3 arguments, first one is a string to match in the file"
        print "the second one is the key associated with the each file (birthyear or raceyear)"
        print "the third one is the key associated with lines in each file (raceyar or birthyear)"
        print " YOU MUST USE RACEYEAR AND BIRTHYEAR "
        sys.exit(1)

    files = [f for f in os.listdir('.') if os.path.isfile(f) and fileString in f]
    
    allTheData = Data(loadAllFiles(files),firstKey, secondKey)
    
    smoothedData = smoothed(allTheData, 3, 3)
    
    printData(allTheData, smoothedData)

if __name__ == '__main__':
    main()


