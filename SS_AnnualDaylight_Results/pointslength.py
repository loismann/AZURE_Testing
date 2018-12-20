#Calculate the number of points in the file
def calcpoints(pointsfilepath):
    """
    :param pointsfilepath: path for the points file
    :return:
    """
    counter = 0
    with open(pointsfilepath) as pointsdata:
        for lines in pointsdata:
            if lines.strip():
                counter +=1
            else:
                warnings.warn("White Space Detected!!!!!")
    return counter