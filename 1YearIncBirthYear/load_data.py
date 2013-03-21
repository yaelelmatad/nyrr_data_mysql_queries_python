import sys, os, re
import collections 

class Data(object):
    def __init__(self,allData, firstLabel,secondLabel):
        self.allData = allData
        self.firstKeyLabel = firstLabel
        self.secondKeyLabel = secondLabel
        self.minFirstKey = min(allData.keys())
        self.maxFirstKey = max(allData.keys())
        self.maxSecondKey = max([max(allData[year].keys()) for year in allData[year]])
        self.minSecondKey = min([min(allData[year].keys()) for year in allData[year]])


def loadFile(filename):
    '''for a give data file returns a dictionary with a nested dictionary for gender
    {1987: {'w': 34, 'm': 17}, 1988: {...},...},'''
    f = open(filename,'r')
    f.next() #the first line is dead to me
    dataSlice = {}
    for line in f:
        (year, men, women) = [int(x) for x in line.split()]
        dataSlice[year] = {'M': men, 'W': women} 
    return dataSlice

def loadAllFiles(files):
    allData = {}
    minFirstKey = 2020
    maxFirstKey = 1000
    for f in files:
        year = int([year for year in re.findall(r'\d+', '%s' %(f)) if year != '0'][0])
        allData[year] = loadFile(f)

    return allData
    #print allData

def smoothed():
    return 1



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

    

if __name__ == '__main__':
    main()


