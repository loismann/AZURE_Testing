"""
    Base module for processing all timeseries based data.
    Use this as the base module for processing illfiles,bf.txt,weafiles.
    Dependencies: none
    Python version : 2.7
"""

from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger("__main__")
logging.basicConfig(format='%(asctime)s -%(levelname)s module:%(module)s function:%(funcName)s message--%(message)s')


import sys
import datetime as  dt
import calendar

def timeStampCalc(mval,dval,tval,yearval=2015):

        """
        return _dt object from month,date and time values
        Note that hours need to range(0,24)
        minutes need to be range(0,60)
        """
        hour = int(tval)-1
        minute = int((tval-hour-1)*60)

        return dt.datetime(int(yearval),int(mval),int(dval),hour,minute)

def readTextFile(filename,delimiter=False):
        "Separate a textfile into lists"
        with open(filename,'r') as ptsfile:
            for lines in ptsfile:
                if delimiter:
                    yield lines.split(delimiter)
                else:
                    yield lines.split()
class TimeData:
    def __init__(self,year,month,date,hour,timeStamp,data,HOY):
        self.year = year
        self.month = month
        self.date = date
        self.hour =hour
        self.timeStamp = timeStamp
        if len(data)==1:
            data = data[0]
        else:
            data = list(data)
        self.data = data
        self.dayOfYear = timeStamp.timetuple().tm_yday
        self.hourOfYear = HOY
    def __str__(self):
        stringVal = self.timeStamp.strftime("Time: %H:%M on %A,%d-%b-%Y")
        stringVal += "\nData: {}".format(self.data)
        return stringVal


class TimeArray(object):
    """
        Base class for all the time series data. Use this to process illfiles, wea files etc.
        This class should be inherited by Ill files, Epw files, etc etc. etc.

        Update: 02/28/2016:
            1. Rewrote the code to make the parameters easier to access.
            2. Added functionality for epw and other comma separated data.


    """

    def __init__(self,filename,timeoffset=False,delimiter=False,year=None,firstDay=None):

        self.filename=filename

        self.timestamps,self.timedata,self.extradata = self.readfile(filename,delimiter,year,firstDay)  #Run readfile and extract data.



    def readfile(self,filenm,delimiter,year,firstDay):
        """A generator to yield time stamps and numerical data
           Numerical data can be ill values, weather file values etc."""

        timefiledata = []
        timefileextra = []
        fixtimeflag = False
        hour0=hour1=False


        if isinstance(filenm,(str,unicode)):
            timeobject = readTextFile(filenm,delimiter)
        else:
            timeobject = filenm

        if firstDay:
            #If a firstDay is selected then select from the following years.
            #Monday is 0 and Sunday is 6.
            assert firstDay in range(1,8),"The first day of the week should be a number within 1(Sunday) to 7(Saturday)"
            dayYears = dict((x,y) for x,y in((6,2006),(0,2007),(1,2013),(2,2014),(3,2015),(4,2010),(5,2011)))
            year = dayYears[firstDay]
        elif year:
            #TMY data is never for a leap year.
            assert not year%4, "The selected year cannot be a leap year"
        else:
            year = 2015

        timeStampsFromFile = []
        HOYCount = 0
        for idx,lines in enumerate(timeobject):
                try:
                    # This one will fire the exception in the case of the first few lines of epw and wea files.
                    testfloat = float(lines[0])

                    HOYCount +=1
                    floatlines = []

                    for data in lines:
                        try:
                            floatlines.append(int(data))
                        except ValueError:
                            floatlines.append(data)


                    if int(floatlines[0])>1000:
                        year,month,date,hour = floatlines[:4]
                        dataval = floatlines[4:]
                    else:
                        month,date,hour =floatlines[:3]
                        dataval = floatlines[3:]

                    timeStampsFromFile.append((month,date,hour))



                    timeStamp = timeStampCalc(month,date,hour,year)


                    timefiledata.append(TimeData(year,month,date,hour,timeStamp,dataval,HOYCount))
                    # timefiledata.append({"m":month,"d":date,"h":hour,"data":dataval,"tstamp":timestamp})

                except ValueError:
                    # print(sys.exc_info())
                    # print(sys.exc_traceback.tb_lineno)
                    timefileextra.append(lines)

        return (timeStampsFromFile,timefiledata,timefileextra)

    @property
    def data(self):
        """
            Just return data without any frills. For example in the case of ill files. Just return ill data for the entire year.
        """
        return [timeObject.data for timeObject in self.timedata]


    def dataHours(self,HOY,includeTimeData=False):
        """
            Return data for one or more hours. Hours will be from 1 to 8760.
            If a single hour is specified, then return a single number or list (in case of EPW etc.).
            If multipler hours are specified then return a list.
        """

        #If by mistake I include numbers inplace of includeTimeDAata, it implies that they should have been numbers and there fore a list.
        if not isinstance(includeTimeData,bool):
            try:
                HOY = HOY+[includeTimeData]
            except TypeError:
                HOY = [HOY]+[includeTimeData]
            includeTimeData = False

        def getData(HOY,includeTimeDetails):
            hourData = self.timedata[HOY-1]
            if not includeTimeDetails:
                data = hourData.data
            else:
                data = hourData

            return data

        data = []
        try:
            for hours in HOY:
                data.append(getData(hours,includeTimeData))
        except TypeError:
            data= getData(HOY,includeTimeData)

        return data

    def dataDays(self,days,includeTimeData=False,combineData=False):
        """
            Return data for a single or multiple days.
            In case combineData is set to True combine separate lists to a single lists.
            If combineData is false, then return a separate list of numbers(or lists) corresponding to every Day.
            days should be numbers within 1 to 365, both inclusive.
        """
        #Step 1 create a list of hours corresponding to those days..

        def fixBoolIssue(dayInput,boolInput):
            if not isinstance(boolInput,bool):
                try:
                    newInput = list(dayInput)+[boolInput]
                except TypeError:
                    newInput = [dayInput]+[boolInput]
                boolInput = False
            else:
                newInput = dayInput

            return  newInput,boolInput

        days,includeTimeData = fixBoolIssue(days,includeTimeData)
        days,combineData = fixBoolIssue(days,combineData)

        hours = []
        try:
            for day in days:
                hours.append( [(day-1)*24+hour for hour in range(1,25)])
        except TypeError:
            hours = [(days-1)*24+hour for hour in range(1,25)]

        try:
            hourlyData = map(lambda x:self.dataHours(x,includeTimeData),hours)
        except TypeError:
            hourlyData = [map(lambda x:self.dataHours(x,includeTimeData),hourList)for hourList in hours]

        hours = list(hourlyData)


        tempHourData =[]
        if combineData:
            try:
                for dayData in hours:
                    tempHourData.extend(dayData)
                hours = list(tempHourData)
            except TypeError:
                pass

        return hours

    def dataMonths(self,months,includeTimeData=False,combineData=False):
        """
            Return data for one more months.
            The optional grouping in this case will happen by
        """

        def fixBoolIssue(dayInput,boolInput):
            if not isinstance(boolInput,bool):
                try:
                    newInput = list(dayInput)+[boolInput]
                except TypeError:
                    newInput = [dayInput]+[boolInput]
                boolInput = False
            else:
                newInput = dayInput

            return  newInput,boolInput

        months,includeTimeData = fixBoolIssue(months,includeTimeData)
        months,combineData = fixBoolIssue(months,combineData)

        try:
            monthLastDays =[calendar.monthrange(2011,month)[1]for month in months]
        except TypeError:
            monthLastDays = [calendar.monthrange(2011,months)[1]]
            months =[months]

        monthData =[]
        for month,monthLastDay in zip(months,monthLastDays):
            startDate = dt.datetime(2011,month,1).timetuple().tm_yday
            endDate = dt.datetime(2011,month,monthLastDay).timetuple().tm_yday
            julianDates = range(startDate,endDate+1)
            monthData.append(self.dataDays(julianDates,includeTimeData,combineData=True))

        if len(monthData)==1:
            monthData= monthData[0]
            return monthData
        elif combineData:
            monthlyCummulativeData =[]
            for monthVal in monthData:
                monthlyCummulativeData.extend(monthVal)
            return monthlyCummulativeData
        else:
            return monthData

    def dataFilterTime(self,months=None,hours=None,weekday=None,includeTimeData=False):
        """
        Filter data according to specify criteria.
        For example months=(11,12),hours=(5,6,7),weekday(2,3,4) will return data for Months of Nov,Dec for horus 5,6,7 on Tue,Wed,Thu
        The order of data will be months,weekday and hours.

        Weekdays are from 0 (Monday) to Sunday(6)
        """
        def fixData(data,valRange):
            if not data:
                data = valRange
            else:
                try:
                    dummyVar = len(data)
                except TypeError:
                    data = [data]
            return data

        months = fixData(months,range(1,13))
        hours = fixData(hours,range(1,25))
        weekdays = fixData(weekday,range(7))

        filteredValues = []
        for dataPoint in self.timedata:
            timeStamp = dataPoint.timeStamp
            weekday = timeStamp.weekday()
            month = timeStamp.timetuple().tm_mon
            hour = timeStamp.timetuple().tm_hour+1

            #Note: this if loop below is a hack to account for hours such as 1.5,2.5 etc in Stadic.
            #So, 0.5 is the first hour, 23.5 ==24 etc.
            if timeStamp.timetuple().tm_min >0:
                hour += 1


            if (hour in hours)and (month in months)and (weekday in weekdays):
                if includeTimeData:
                    filteredValues.append(dataPoint)
                else:
                    filteredValues.append(dataPoint.data)
        return filteredValues

#Test the module.
if __name__ ==  '__main__':
    pass