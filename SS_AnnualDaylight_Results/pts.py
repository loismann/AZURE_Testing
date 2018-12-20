"""
    This module defines two classes:
        1. Point is a simple 3d Point
        2. roomgrid is a collection of points in a room. that can be read off of a pts file or a zone file.
"""

from __future__ import print_function
from __future__ import division

import os
import logging
logger = logging.getLogger("__main__")
logging.basicConfig(format='%(asctime)s -%(levelname)s module:%(module)s function:%(funcName)s message--%(message)s')


import logging

class Point(object):
    def __init__(self,x,y,z,vector,idx=None):
        self.x = x
        self.y = y
        self.z = z
        self.vector = vector
        self.ptid = "({},{},{}),{}".format(self.x,self.y,self.z,self.vector)
        self.idx = idx #This is the location where the point occurs in the point occurs in the pts file or zone file.

    def __str__(self):
        """retrun a string representation of the point"""
        return "3D Point at x:{}, y:{}, z:{}. The vector is {}".format(self.x,self.y,self.z,self.vector)

class RoomGrid(object):
    """
    Analyze a daysim format points file.
    """
    def __init__(self,ptsfile):

        assert os.path.exists(ptsfile),'The points file %s was not found'%ptsfile


        try:
            with open(ptsfile) as ptsstring:
                ptsfile = [line for line in ptsstring]
        except:
            pass

        self.ptsdict = self.procPtsFile(ptsfile)


    def procPtsFile(self,ptsfile,vector=[0,0,1]):
        """Return a dictionary containing points """
        ptsdict = {}

        for idx,lines in enumerate(ptsfile):

            try:
                linesnum = map(float,lines.split())
                x,y,z=linesnum[:3]

                # This assertion is meant for checking if there are 6 values in line,
                #  ie its a pts file. If yes get vector from the pts file. Else use
                #  default or user defined vector
                assert len(linesnum)==6
                vector = linesnum[3:]
                temppt = Point(x,y,z,vector,idx)
                ptsdict[temppt.idx]=temppt

            # If the assertion fails use the vector value which is defined default or specified.
            except AssertionError:
                linesnum = map(float,lines.split())
                x,y,z=linesnum[:3]
                temppt = Point(x,y,z,vector,idx)
                ptsdict[temppt.idx]=temppt

            logging.info("x: {}y: {}z: {}v: {}".format(x,y,z,vector))

        return ptsdict

    @property
    def minMax(self):
        """
        :return: Return the minimum and maximum limits of x,y and z dimensions. The output
        will be something like {'x':(minX,maxX),'y':(minY,maxY),'z':(minZ,maxZ)}

        """
        return {'x':(self.minX,self.maxX),'y':(self.minY,self.maxY),'z':(self.minZ,self.maxZ)}

    @property
    def minX(self):
        """
        :return: Return the min X coordinate for the entire grid.
        """
        return min([pt.x for pt in self.ptsdict.values()])

    @property
    def maxX(self):
        """
        :return: Return the max X coordinate for the entire grid.
        """
        return max([pt.x for pt in self.ptsdict.values()])

    @property
    def minY(self):
        """
        :return: Return the min Y coordinate for the entire grid.
        """
        return min([pt.y for pt in self.ptsdict.values()])

    @property
    def maxY(self):
        """
        :return: Return the max Y coordinate for the entire grid.
        """
        return max([pt.y for pt in self.ptsdict.values()])

    @property
    def minZ(self):
        """
        :return: Return the min Z coordinate for the entire grid.
        """
        return min([pt.z for pt in self.ptsdict.values()])

    @property
    def maxZ(self):
        """
        :return: Return the max Z coordinate for the entire grid.
        """
        return max([pt.z for pt in self.ptsdict.values()])

    @property
    def ptArray(self):
        """return an array of points sorted according to their index value"""

        # sort the points according to their index values.
        ptslist = sorted(self.ptsdict.values(),key=lambda pt:pt.idx)
        ptslist = [(pt.x,pt.y,pt.z,pt.vector)for pt in ptslist]

        return ptslist

    @property
    def ptArrayXYZ(self):
        """Return list of points in the order that they were found in the points file."""
        return [(x,y,z)for x,y,z,vector in self.ptArray]

    @property
    def ptArrayX(self):
        """Return list of X dimensions alone in the order that they were found in the points file."""
        return [x for x,y,z,vector in self.ptArray]

    @property
    def ptArrayY(self):
        """Return list of Y dimensions alone in the order that they were found in the points file."""
        return [y for x,y,z,vector in self.ptArray]

    @property
    def ptArrayZ(self):
        """Return list of Z dimensions alone in the order that they were found in the points file."""
        return [z for x,y,z,vector in self.ptArray]

    @property
    def uniCor(self):
        """return a dictionary containing of tuples of unique coordinates in x,y,z direction"""
        ptslist = self.ptsdict.values() #sort the points according to their index values.
        ptsx = sorted(set([pt.x for pt in ptslist]))
        ptsy = sorted(set([pt.y for pt in ptslist]))
        ptsz = sorted(set([pt.z for pt in ptslist]))
        maxgridsize = len(ptsx)*len(ptsy)*len(ptsz)
        actgridsize = len(self.ptsdict)
        return {'x':ptsx,'y':ptsy,'z':ptsz,'maxgridsize':maxgridsize,'actgridsize':actgridsize}

    @property
    def uniCorX(self):
        """
        :return: List of unique x coordinates
        """
        return self.uniCor['x']

    @property
    def uniCorY(self):
        """
        :return: List of unique y coordinates
        """
        return self.uniCor['y']

    @property
    def uniCorZ(self):
        """
        :return: List of unique z coordinates
        """
        return self.uniCor['z']

    @property
    def gridSizeMax(self):
        """Maximum possible gridsize. If the pts file is a square grid with 10x 10y pts
        then this value will be 100"""
        return self.uniCor['maxgridsize']

    @property
    def gridSizeActual(self):
        """Maximum possible gridsize. If the pts file is a square grid with 10x 10y pts but
        with 5 points missing due to the odd shape of the room, then this value will be 95"""
        return self.uniCor['maxgridsize']

    @property
    def testUniformSpc(self):
        """
        Test if the points are uniformly spaced in x,y,z direction. Returns in a dictionary
        like {'z_spacings': (), 'y_spacings': [24.0], 'x_spacings': [24.0]}. In this example,
        there is no spacing in z direction, while points in x and y direction are spaced
        24.0 apart from each other.
        :return:
        """

        spcdict = dict.fromkeys(('x_spacings','y_spacings','z_spacings'),())
        coord = self.uniCor
        rounder = lambda lst:[round(val,4)for val in lst] #lambda for rounding to 4 dec digits.
        x,y,z = rounder(sorted(coord['x'])),rounder(sorted(coord['y'])),rounder(sorted(coord['z'])) #Sort and round values for unique x,y,z coord

        if len(x)-1: #If there are more than 1 unique points in x..then check for spacing..same applies to other coords
             xspc= set(rounder([x[idx]-x[idx-1]for idx in range(1,len(x))]))
             spcdict['x_spacings']=sorted(xspc)
        if len(y)-1: #If there are more than 1 unique points in x..then check for spacing..same applies to other coords
             yspc= set(rounder([y[idx]-y[idx-1]for idx in range(1,len(y))]))
             spcdict['y_spacings']=sorted(yspc)
        if len(z)-1: #If there are more than 1 unique points in x..then check for spacing..same applies to other coords
             zspc= set(rounder([z[idx]-z[idx-1]for idx in range(1,len(z))]))
             spcdict['z_spacings']=sorted(zspc)
        return spcdict

    @property
    def gridMatrixRelative(self):
        """
        :return: Returns a list containing the relative index and spatial postion of
        invidivdual points in a pts file. Example:
        [{'scaledGrid': (0.0, 0.0, 0), 'grid': (1, 1, 1)},{'scaledGrid': (0.0, 0.056, 0), 'grid': (1, 2, 1)} ... ].

        scaledGrid refers to the spatial scaling, while grid refers to index-based scaling,
        both in x,y,z dimensions.
        """
        unicor = self.uniCor
        ptarray = self.ptArray


        x,y,z,maxgrid,act = unicor['x'],unicor['y'],unicor['z'],unicor['maxgridsize'],unicor['actgridsize']
        xlen,ylen,zlen = map(len,(x,y,z))
        xmin,ymin,zmin = map(min,(x,y,z))
        xmax,ymax,zmax = map(max,(x,y,z))

        #This lambda is for calculating on basis of grid pont
        grid = lambda point:(x.index(point[0])+1,y.index(point[1])+1,z.index(point[2])+1)

        gridscale = lambda point:(round(point[0]/xmin,3),round(point[1]/ymin,3),round(point[2]/zmin,3))

        if  (xmin-xmax):
            gridscalex = lambda point:round((point[0]-xmin)/(xmax-xmin),3)
        else:
            gridscalex = lambda point:0

        if  (ymin-ymax):
            gridscaley = lambda point:round((point[1]-ymin)/(ymax-ymin),3)
        else:
            gridscaley = lambda point:0

        if  (zmin-zmax):
            gridscalez = lambda point:round((point[1]-zmin)/(zmax-zmin),3)
        else:
            gridscalez = lambda point:0

        grids = [grid(point)for point in ptarray]
        scaledgrids = [(gridscalex(point),gridscaley(point),gridscalez(point)) for point in ptarray]

        return [{'grid':gridtuple,'scaledGrid':scaledgrids[idx]}for idx,gridtuple in enumerate(grids)]

    @property
    def gridMatrixFull(self):
        """

        :return:
        This property returns the maximum possible grid points in a roomGrid. For example
        a roomgrid could have 10 (x) and 10 (y) unique coordinates. But the actual number
        of points in the points file could be only 80. This property will calculate all
        the possible coordiantes. The order followed is X,Y,Z. Return a 2d grid if Z has
        only dimension. Or else return a 3d grid.
        """

        xCor = self.uniCorX
        yCor = self.uniCorY
        zCor = self.uniCorZ

        gridMatrix =[]

        for xVal in xCor:
            for yVal in yCor:
                for zVal in zCor:
                    gridMatrix.append((xVal,yVal,zVal))

        return gridMatrix

    @property
    def gridMatrixLocations(self):
        """
        This property returns the location of each point with resepct to the gridMatrixFull.
        For example a pts file with max possible 100 points could have 70 points.
        This property will return the location of those points wrt to the 100 point grid.
        Locations where the points exists in the pts file will have the locaiton index of the point while others will have None.
        This property is useful in creating a rectangular grid of points from a non rectangular shaped pts file.
        :return:
        """
        fullGridMatrix = self.gridMatrixFull
        ptArray = self.ptArrayXYZ
        locations = []
        for pointTuples in fullGridMatrix:
            if pointTuples in ptArray:
                locations.append(ptArray.index(pointTuples))
            else:
                locations.append(None)

        return locations

    @property
    def spacingX(self):
        """
        :return: X spacing between grid points
        """
        coord = self.uniCorX
        rounder = lambda lst:[round(val,4)for val in lst] #lambda for rounding to 4 dec digits.
        unique = rounder(sorted(coord))
        if len(unique)-1:
            spacings =  sorted(set(rounder([unique[idx]-unique[idx-1]for idx in range(1,len(unique))])))
        else:
            spacings = ()
        return spacings
    @property
    def spacingY(self):
        """
        :return: Y spacing between grid points
        """
        coord = self.uniCorY
        rounder = lambda lst:[round(val,4)for val in lst] #lambda for rounding to 4 dec digits.
        unique = rounder(sorted(coord))
        if len(unique)-1:
            spacings =  sorted(set(rounder([unique[idx]-unique[idx-1]for idx in range(1,len(unique))])))
        else:
            spacings = ()
        return spacings

    @property
    def spacingZ(self):
        """
        :return: Z spacing between grid points
        """
        coord = self.uniCorZ
        rounder = lambda lst:[round(val,4)for val in lst] #lambda for rounding to 4 dec digits.
        unique = rounder(sorted(coord))
        if len(unique)-1:
            spacings =  sorted(set(rounder([unique[idx]-unique[idx-1]for idx in range(1,len(unique))])))
        else:
            spacings = ()
        return spacings

    def summaryDict(self):
        """
        :return:
        Return a summary of the points file in the form of a dictionary. The dictionary
        contains the following values. The dictionary contains the following keys:

        totalPoints: Total number of points in points file.

        maxGridSize: The maximum possible size of the grid. This value can be differ from
        total points as it is possible that there are some pts files were some of
        the possible points might be missing.

        dimLimXYZ: Limits of x,y,z dimensions. The value of this data will be something
        like ((18.0, 378.0),(6.0, 438.0), (36.00001, 36.00001))

        uniqueNumPtsXYZ: is the number of unique points in each dimension. For example in
        a square grid containing 100 points this will be something like (10,10,1).

        uniformSpacing: This will return true if all the points in the pts file are
        spaced uniformly wrt each other.

        """
        extents = self.minMax
        totalpts = len(self.ptsdict)
        unicor = self.uniCor
        unitest = self.testUniformSpc

        # Get the length of list of unique coor in x,y,z
        checkval = [len(coor) for coor in unitest.values()]

        # return a list of true/false. False if val is 0 or 1.
        # True otherwise. evaluate to False if any one value is True
        checkspc = not any([False if (val == 1) | (val == 0) else True for val in checkval])

        sumDict = {}
        sumDict['totalPoints'] = totalpts
        sumDict['dimLimXYZ']=(extents['x'],extents['y'],extents['z'])
        sumDict['uniqueNumPtsXYZ'] = (len(unicor['x']),len(unicor['y']),len(unicor['z']))
        sumDict['maxGridSize']=unicor['maxgridsize']
        sumDict['uniformSpacing']=checkspc

        return sumDict

    def __str__(self):
        """Return a pretty string version of the summaryDict """

        sumDict = self.summaryDict()
        totalPts =sumDict['totalPoints']
        dimX,dimY,dimZ = sumDict['dimLimXYZ']
        uniqueX,uniqueY,uniqueZ = sumDict['uniqueNumPtsXYZ']
        gridSize=sumDict['maxGridSize']
        uniSpc = sumDict['uniformSpacing']

        return """
        The total number of grid points is {}.
        Dimension limits: X:{}, Y:{}, Z:{}.
        Unique number of points in each dimension(X,Y,Z):({},{},{}).
        Maximum possible grid size: {}.
        Uniformly spaced grid points:{}""".format(totalPts,dimX,dimY,dimZ,uniqueX,uniqueY,uniqueZ,
                                                  gridSize,uniSpc)


if __name__ ==  '__main__':
    y = RoomGrid('examples/grid.pts')
    print(y.ptArrayXYZ)
    print(y.uniCorY)
    print(y.gridMatrixRelative)
