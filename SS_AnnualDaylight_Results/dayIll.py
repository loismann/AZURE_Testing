"""
Contains a class called Dayill that can be instantiated with an Illuminance file and points file. For Radiance outputs
from programs like Dctimestep and Rmtxop additional functions are provided.


"""

from __future__ import division
from __future__ import print_function
from ill import Illarr
import pts
import timeSeries
from timeSeries2 import TimeArray
import tempfile,os,warnings

class Dayill(timeSeries.TimeArray):
    """This is a class for annual or time series ill files. Needs the ill file path and points file to be instantiated.
    This file will be able to handle conventional (ie 8760 values illfiles) and also files with less number of timestamps.

    NOTE:
        This is a terrible class!! But re-writing it is not a good idea. So, I have added a bunch of new methods to
        access the data that is generated.

    Some hints on accessing data:
        1. For accessing illuminance for the entire space:
            illuminanceDataHOY (hour): Get illuminance data for a particular hour.
            illuminanceDataMonthly(month): Get illuminance data for a particular month.
            illuminanceDataHourly(hour): Get illuminance data for a particular hour for every day of the year (or the days
                for which the data is present).
            illuminanceDataFull: Get the entire illuminance data in the form of list of lists.
        2. For accessing time:
            timeStamps: datetime.datetime values in a tuple for all the points at which data exists. This can be useful
            for plotting.
        3. For accessing all the data: self.timeData is a list of dictionaries where each dictionary contains the
            following keys: "m":month,"d":date,"h":hour,"data":dataval,"tstamp":timestamp. month,date will usually be
            ints while hour can be a decimal. tstamp is a datetime.datetime object. 'data' is a class of the type
            Illarr
        4. To get a summary of the entire file: Just print the instance through (the __str__ option_).

    """

    def __init__(self,illfile,ptsfile,weaFile=None,convertFromRadiance=False,directoryForConversion=None,
                 convertedFilePath=None):
        """
        Typical constructor behaviour would involve specifying a Daysim format timeseries file and a pts file as input.
        Another, now frequently occuring possibility, is to do a conversion from a Radiance-format output file to Daysim
        and then do calculations from there on. For this the convertFromRadiance flag needs to be set to True.
        Additionally, the temp or /tmp/ directory is likely not the best place to store the converted files, so the
        directoryForConversion and convertedFilePath are to be used for that.

        :param illfile: A time series file of illuminance values in Daysim format.
        :type illfile: basestring

        :param ptsfile: The points file corresponding to that ill file.
        :type ptsfile: basestring

        :param weaFile: The wea file that was used for the simulation. This is essential for converting Radiance format
            files to Daysim format. The wea file provides the timestamps (which can be less than 8760 to).
        :type weaFile: basestring

        :param directoryForConversion: Path for the directory to which the temporary converted Radiance-to Daysim file
            must be written.
        :type directoryForConversion: basestring

        :type convertFromRadiance: bool
        :param convertFromRadiance: Set this to True to convert a Radiance result file to Daysim format first.

        :type convertedFilePath: basestring
        :param convertedFilePath: The path to which the converted file should be written to.
        """

        self.illfile = illfile
        self.weaFile = weaFile
        self.ptsfile = ptsfile
        self.__directoryForConversion=directoryForConversion
        self.__convertedFilePath = convertedFilePath

        if convertFromRadiance:
            assert self.weaFile, 'The wea file needs to be provided for the conversion from Radiance to happen.'

            #Convert a Radiance file to Daysim format and return that file.
            self.illfile = self.mergeTimesFromDaysim(outputFile=self.__convertedFilePath)

            msg = "Converted the original file %s to a Daysim format file %s"%(illfile,self.illfile)
            illfile = self.illfile
            warnings.warn(msg)

        # Call the constructor from timeseries array. This will define self.timedata and self.extradata
        timeSeries.TimeArray.__init__(self, illfile)
        # create a dictionary of points from the pts file.
        self.roomgrid = pts.RoomGrid(ptsfile)

        self.timedata_TO_ill()

    def timedata_TO_ill(self):
        """
        This method populates the illuminance data in the class. DO NOT DELETE !!
        """
        for timestamps in self.timedata:
               timestamps['data']=Illarr(timestamps['data'],self.roomgrid)
        return self

    def __add__(self, other):
        #Create a new timedata, then instantiate a new class of dayill and replace the time data in that with the new time data.
        #This seems like a very hacky way to do this thing...however it will work for the time being.

        newdayill = Dayill(self.illfile,self.ptsfile)

        for idx,timestamps in enumerate(self.timedata):
             newdayill.timedata[idx]['data'] = timestamps['data'] + other

        return newdayill
    def __sub__(self, other):
        newdayill = Dayill(self.illfile,self.ptsfile)

        for idx,timestamps in enumerate(self.timedata):
             newdayill.timedata[idx]['data'] = timestamps['data'] - other

        return newdayill
    def __mul__(self, other):
        newdayill = Dayill(self.illfile,self.ptsfile)

        for idx,timestamps in enumerate(self.timedata):
             newdayill.timedata[idx]['data'] = timestamps['data'] * other

        return newdayill

    def illLimits(self,maxval=2500,minval=200,verbose=False,percent=False):
        return [timestamps['data'].filterill(maxval,minval,verbose=verbose,
                                             percent=percent)for timestamps in self.timedata]

    @property
    def max_ill(self):
         """Returns a list Maximum illuminance in the space for all hours."""
         return [timestamps['data'].max_ill['max_ill'] for timestamps in self.timedata]

    @property
    def min_ill(self):
        """Returns a list Minimum illuminance in the space for all hours."""
        return [timestamps['data'].min_ill['min_ill'] for timestamps in self.timedata]

    def singlePointIlluminance(self, gridPtIndex, startTime=None, endTime=None, returnAsPercentOf=None,
                               returnAsDifferenceFrom=None,percentRoundOff=3):
        """
        Return the illuminance for a single point in the room.
        :param gridPtIndex: The grid point for whcih illuminance is to be returned.
        :param startTime: start time.
        :param endTime: end time.
        :param returnAsPercentOf: Return values as a percentage of this value. For example,
            if this value is 1000 then all the illuminances will be divided by 1000.
        :param returnAsDifferenceFrom: For (x - returnAsDifferenceFrom) where x is illuminance
            at a given hour.
        :param percentRoundOff: Defaults to 3.
        :return:
        """

        #get the size of room.
        gridSize = self.roomgrid.gridSizeActual

        #get a list of minimum and maximum hours from the first 25 data points.
        possibleHours = [t['h'] for t in self.timedata[:30]]

        if startTime is None:
            startTime = min(possibleHours)

        if endTime is None:
            endTime = max(possibleHours)

        assert gridPtIndex in range(1, gridSize + 1), \
            'The value for gridPtIndex(%s) must be between 1 and %s'%(gridPtIndex,gridSize)

        illuminanceData=[]

        for timeStamps in self.timedata:
            if startTime <= timeStamps['h'] <= endTime:
                illuminanceData.append(timeStamps['data'].illarr[gridPtIndex-1])

        assert not (returnAsDifferenceFrom and returnAsPercentOf),\
            "Both returnAsDifferenceFrom(%s) and returnAsPercentOf(%s) cannot be specified" \
            "."%(returnAsDifferenceFrom,returnAsPercentOf)

        if returnAsDifferenceFrom is not None:
            illuminanceData = [round(val-returnAsDifferenceFrom,percentRoundOff) for val in illuminanceData]

        if returnAsPercentOf is not None:
            illuminanceData = [round(val/returnAsPercentOf,percentRoundOff) for val in illuminanceData]

        return illuminanceData

    def pointsIlluminanceTimeSummary(self,illMin=None, illMax=None,
                                     startTime=None,endTime=None,returnPercent=False,
                                     specificPoints=None,percentRoundOff=3):
        """
        Return the illuminance summary of a room in terms of hours. The returned value
        will be a list containing data pertaining to grid points. Each data point in that
        list corresponds to a count of hours or a fraction of hours.

        If only illMin is provided then count all hours where illuminance equal to and above illMin
        If only illMax is provided then count all hours where illuminance is equal to or below illMax
        If both illMin and illMax are provided, then count all hours illuminance is between these
        values (limits inclusive).

        :param percentRoundOff: No. of significant digits to which percent should be
            rounded off to.
        :param illMin: Minimum illuminance to be counted for that point. If
            illuminance is below that value for a given, then that hour won't be included
            in the total. Defaults to 200 lux. To exclude this filter set it to None.
        :param illMax: Maximum illuminance to be counted for that point. If
            illuminance is above that value for a given, then that hour won't be included
            in the total. Defaults to 2000 lux. To exclude this filter set it to None.
        :param startTime: Hour of the day at which to begin counting. The limit is included
            in counting. Defaults to None.
        :param endTime: Hour of the day at which to stop counting. Limit included. Defaults
            to None.
        :param returnPercent: If set to True, the value for each point will be divided
            by the total number of hours (that lie between startTime and endTime). Defaults
            to None.
        :param specificPoints: A single point of list of points for which the data is needed.
            If None(default) is specified data for all points will be returned. The points
            are based on sequence in the pts file and start from 1 (and not zero).
            So, for a pts file with 100 points the valid input will be any number(s) between
            1 and 100.
        :return:
        """

        #get a list of minimum and maximum hours from the first 25 data points.
        possibleHours = [t['h'] for t in self.timedata[:30]]

        if startTime is None:
            startTime = min(possibleHours)

        if endTime is None:
            endTime = max(possibleHours)

        assert not ((illMin is None) and (illMax is None)),\
            'Both illMin and illMax cannot be specified as None'

        assert not ((illMin is False) or (illMax is False)),\
            'illMin(%s) and illMax(%s) can either be an integer or None. They cannot be False.'%(illMin,illMax)

        illuminanceData=[]
        hourCount = 0
        for timeStamps in self.timedata:
            if startTime <= timeStamps['h'] <= endTime:
                hourCount +=1
                illuminanceData.append(timeStamps['data'].illarr)

        illuminanceData = zip(*illuminanceData)
        ptsLen = len(illuminanceData)

        if specificPoints:
            if isinstance(specificPoints,int):
                specificPoints = [specificPoints]

            ptStatement = "The total number of points in the point file is %s and the value" \
                          " for points should be between 1 and %s."%(ptsLen,ptsLen)

            assert len([pt for pt in specificPoints if pt in range(1,ptsLen+1)])==len(specificPoints),\
            "The points %s do not all lie between 1 and %s. %s"%(specificPoints,ptsLen+1,ptStatement)

        else:
            specificPoints = range(1,ptsLen+1)

        #Subtract each pt index by 1 so that it is in sync with the standard indexing
        # for lists.

        specificPoints = [pt-1 for pt in specificPoints]

        pointsData = []
        for pt in specificPoints:
            ptHourCount = 0
            for hourlyIlluminanceValue in illuminanceData[pt]:
                if illMin and (illMax is None):
                    if hourlyIlluminanceValue >= illMin:
                        ptHourCount +=1
                if illMax and (illMin is None):
                    if hourlyIlluminanceValue <= illMax:
                        ptHourCount +=1
                if (illMax is not None) and (illMin is not None):
                    if illMax>= hourlyIlluminanceValue >= illMin:
                        ptHourCount +=1

            if returnPercent:
                ptHourCount = round(ptHourCount/hourCount,percentRoundOff)

            pointsData.append(ptHourCount)

        return pointsData

    def metricSDAdetailed(self, illThreshold=300, startTime=8, endTime=18):
        """
        Spatial Daylight Autonomy is the percentage of points in a room that exceed a
        threshold of 300 lux for more than 50% of the analysis time. This function
        will return a all the points and the perecent of time for which they are above
        the threshold value. So the output will be something like [ 0.90, 0.80 ... ] where
        the values 0.90, 0.80 etc represent the perecent of hours for which illuminance
        at those points is equal to or above 300 lux.

        For, LM83 and Dayim based data, use start time of 8 and 18 if the hours are 0.5,
        1.5 .. 23.5 and use start time of 9 to 18 if the hours are 1,2,3..24.

        :param illThreshold: Threshold illuminance for SDA. Defaults to 300 lux.
        :param startTime: Defaults to 8.
        :param endTime: Defaults to 18.
        :return:
        """

        data = self.pointsIlluminanceTimeSummary(illMin=illThreshold, startTime=startTime,
                                                 endTime=endTime, returnPercent=True)

        return data

    def metricSDA(self, illThreshold=300, startTime=8, endTime=18,DA=0.5):
        """
        Spatial Daylight Autonomy is the percentage of points in a room that exceed a
        threshold of 300 lux for more than 50% of the analysis time. This function will return
        sDA only. For detailed info refer the function metricsSDAdetailed.

        For, LM83 and Dayim based data, use start time of 8 and 18 if the hours are 0.5,
        1.5 .. 23.5 and use start time of 9 to 18 if the hours are 1,2,3..24.

        :param DA: The value for percent cut off for each point. Defaults to 0.5. This
            is the percentage of hours below which that particular point will not be counted.
        :param illThreshold: Threshold illuminance for SDA. Defaults to 300 lux.
        :param startTime: Defaults to 8.
        :param endTime: Defaults to 18.
        :return:
        """

        data = self.metricSDAdetailed(illThreshold=illThreshold,startTime=startTime,
                                      endTime=endTime)

        data = len([val for val in data if val >=DA])/len(data)

        return data

    def metricASEdetailed(self,illThreshold=1000,startTime=8,endTime=18,returnAsPercent=False):
        """
        ASE is defined as the percent of sensors in the analysis area that are found to
        be exposed to more than 1000 lux of direct sunlight for more than 250 hours. This function
        will return all the points and the perecent of time for which they are above
        the threshold value. So the output will be something like [ 0.90, 0.80 ... ] where
        the values 0.90, 0.80 etc represent the perecent of hours for which illuminance
        at those points is above 1000 lux.

        For, LM83 and Dayim based data, use start time of 8 and 18 if the hours are 0.5,
        1.5 .. 23.5 and use start time of 9 to 18 if the hours are 1,2,3..24.

        :param returnAsPercent: Default value is False as this function is passed on to
            generate ASE by metricASE function. Set this to True to make this data
            plottable.
        :param illThreshold: Threshold value for ASE
        :param startTime: Defaults to 8
        :param endTime: Defaults to 18
        :return:
        """
        #Note that illuminance should more than the threshold.
        data = self.pointsIlluminanceTimeSummary(illMin=illThreshold+1, startTime=startTime,
                                                 endTime=endTime,returnPercent=returnAsPercent)
        return data

    def metricASE(self, illThreshold=1000, startTime=8, endTime=18,hours=250):
        """
        ASE is defined as the percent of sensors in the analysis area that are found to
        be exposed to more than 1000 lux of direct sunlight for more than 250 hours. This function
        will return ASE only. For more info check the funtion metricASEdetailed.

        For, LM83 and Dayim based data, use start time of 8 and 18 if the hours are 0.5,
        1.5 .. 23.5 and use start time of 9 to 18 if the hours are 1,2,3..24.

        :param hours: Hours beyond which the point will be counted for ASE.
        :param illThreshold: Threshold value for ASE
        :param startTime: Defaults to 8
        :param endTime: Defaults to 18
        :return:
        """
        # Note that illuminance should more than the threshold.
        data = self.metricASEdetailed(illThreshold=illThreshold,startTime=startTime,
                                      endTime=endTime)

        data = len([val for val in data if val>hours])/len(data)

        return data

    def metricUDIdetailed(self,illThresholdLow=100,illThresholdHigh=2000,startTime=8,
                          endTime=18,returnAsPercent=False):
        """
        The illThresholdLow and illThresholdHigh values are based on Reinhart,Mardaljevic
        and Rogers. 2006.
        :param illThresholdLow: Lower illuminance threshold. Defaults to 100.
        :param illThresholdHigh: Higher illuminance threshold. Defaults to 2000.
        :param startTime: Defaults to 8
        :param endTime: Defaults to 18.
        :param returnAsPercent: Defaults to False. Set this to True to get percentage values
        for plotting.

        :return: A list containing three tuples corresponding to UDImin, UDImid, UDImax.
        The size of each tuple is equal to the number of grid points. The data inside each
        tuple is a list of hours corresponding to a particular point that satisfies the
        low, mid or high setting.

        """

        illLow = self.pointsIlluminanceTimeSummary(illMax=illThresholdLow-1,startTime=startTime,
                                                   endTime=endTime,returnPercent=returnAsPercent)
        illMid = self.pointsIlluminanceTimeSummary(illMin=illThresholdLow,
                                                   illMax=illThresholdHigh,startTime=startTime,
                                                   endTime=endTime,returnPercent=returnAsPercent)
        illMax = self.pointsIlluminanceTimeSummary(illMin=illThresholdHigh+1,
                                                   startTime=startTime,
                                                   endTime=endTime,returnPercent=returnAsPercent)
        return [illLow,illMid,illMax]

    def summaryPts(self):
        """Return a dictionary containing the summary of the grid points file"""
        sumDict = {'fileIll': self.illfile, 'filePts': self.ptsfile}
        sumDict.update(self.roomgrid.summaryDict())
        return sumDict

    def illuminanceDataHOY(self, hour):
        """Return the illuminance list data for a particular hour. This is based on index. So, for a full year, this
        value can be between 0 to 8759.
        :type hour: int
        :param hour: Hour of the year based on index.
        """
        timeData = self.timedata
        assert hour<len(timeData),'The hour(%s) entered is an index that is higher than the number of hourly data ' \
                                  'points(%s).'%(hour,len(timeData))
        illumData = list(timeData[hour]['data'].illarr)
        return illumData

    def illuminanceDataMonthly(self,month):
        """
        Get illuminance data for a specific month.
        :param month:
        :return:
        """
        timeStamps = self.timeStamps
        months = [val.month for val in timeStamps]
        assert month in months,'The month %s was not found in timeStamps. ' \
                               'The months in the current data set are: %s'%(month," ".join(map(str,sorted(set(months)))))
        illumData = self.illuminanceDataFull

        illumDataMonthly = []
        for idx,ill in enumerate(illumData):
            currMonth = months[idx]
            if currMonth == month:
                illumDataMonthly.append(ill)

        return illumDataMonthly

    def illuminanceDataHourly(self,hour):
        """
        Get illuminance data for a specific hour
        :param hour: Hour for which the data is to be extracted.
        :return:
        """
        timeStamps = self.timeStamps
        hours = [val.hour for val in timeStamps]
        assert hour in hours,'The hour %s was not found in timeStamps. ' \
                               'The hours in the current data set are: %s'%(hour," ".join(map(str,sorted(set(hours)))))
        illumData = self.illuminanceDataFull

        illumDataHourly = []
        for idx,ill in enumerate(illumData):
            currHour = hours[idx]
            if currHour == hour:
                illumDataHourly.append(ill)

        return illumDataHourly

    @property
    def illuminanceDataFull(self):
        """Return the illuminance data for the entire dataset. This will typically be 8760 values but could be lower,
        based on how many timestamps there are."""
        timeData = self.timedata
        illumData = [list(val['data'].illarr) for val in timeData]
        return illumData

    @property
    def timeStamps(self):
        """Return datetime.datetime format values for all the timestamps in the ill file. This can be useful (hopefully)
        in plotting."""
        timeData = self.timedata
        timeStamp = [data['tstamp'] for data in timeData]
        return timeStamp

    def mergeTimesFromDaysim(self, outputFile=None, sigFigForResults=2, outputFileSuffix='_rev.ill', useTempFile=True,
                             roundToInt=True):
        """
         Create a daysim format file (or data) from a file containing illuminance values and
        another file containing the timestamps. This function will be useful in putting
        timestamps on files created by programs such as rmtxop, dctimestep etc.
        NOTE: This file is a drop-in from a different module, so it might contain some fluff.
        :param outputFile: Path for output file. optional.
        :param sigFigForResults: Significant figure for results. Defautls to 2.
        :param outputFileSuffix: Defaults to "_rev.ill"
        :param useTempFile: If outputFile is not named, then this file will be used.
        :return:
        """
        illFile = self.illfile

        daysimTimeSeriesFmtFile  = self.weaFile

        writeToDirectory = self.__directoryForConversion


        assert os.path.exists(illFile), \
            'The file path %s does not exist' % illFile

        assert os.path.exists(daysimTimeSeriesFmtFile), \
            'The file path %s does not exist' % daysimTimeSeriesFmtFile

        if not outputFile:
            if not useTempFile:
                outputFile = os.path.splitext(illFile)[0] + outputFileSuffix
            else:
                outputFile = tempfile.mktemp(suffix=outputFileSuffix,dir=writeToDirectory)

            msg = "\nSince no output file was specified an output file was written to %s" % outputFile
            warnings.warn(msg)
        else:
            assert illFile is not outputFile, \
                'The path for input file(%s) and output file(%s) cannot be same!' % (illFile, outputFile)

        daysimFileData = TimeArray(daysimTimeSeriesFmtFile).timestamps

        textData = ""
        countHOY = 0
        with open(illFile) as illData, open(outputFile, 'w') as illWrite:
            for lines in illData:
                lines = lines.strip()
                if lines:
                    try:
                        illValues = map(float, lines.split())

                        if isinstance(sigFigForResults, int):
                            illValues = [round(val, sigFigForResults) for val in illValues]

                        if roundToInt:
                            illValues = [int(val) for val in illValues]
                        illValues = map(str, illValues)

                        illValues = list(daysimFileData[countHOY]) + illValues

                        illValues = map(str, illValues)
                        illValues = " ".join(illValues) + '\n'
                        illWrite.write(illValues)

                        countHOY += 1
                    except ValueError:
                        textData += "\n" + lines

        return outputFile

    def __str__(self):

        ptsDict = dict(self.summaryPts())
        ptsKeys = sorted(ptsDict.keys())
        ptsData = "\n\t".join(["%s: %s"%(key,str(ptsDict[key])) for key in ptsKeys])

        data = "Files and Points Summary:" +"\n\t" +ptsData


        timeData = self.timedata
        months = list(sorted(set([val['m'] for val in timeData])))
        dates = list(sorted(set([val['d'] for val in timeData])))
        hours = list(sorted(set([val['h'] for val in timeData])))
        dataSetLength = len(timeData)

        data+="\n\nTimeSeries summary:"
        data+="\n\tMonths(%s): %s"%(len(months),",".join(map(str,months)))
        data += "\n\tDates(%s): %s" %(len(dates), ",".join(map(str,dates)))
        data += "\n\tHours(%s): %s" % (len(hours),",".join(map(str,hours)))
        data += "\n\tTotal Number of data points: %s"%dataSetLength
        return data


if __name__ == "__main__":
    pass