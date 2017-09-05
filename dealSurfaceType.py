#deal with the surface type and compute the area proportion

import numpy as np
import pandas as pd
import os

def readSurfaceData(filename):
    linestrs=[]
    i=0
    file_object = open(filename,'r')
    try:
       fileline=file_object.readlines()
       paramline=fileline[0].rstrip('\n').strip().split(' ')
       ncols=int(paramline[1])
       paramline=fileline[1].rstrip('\n').strip().split(' ')
       nrows=int(paramline[1])
       paramline=fileline[2].rstrip('\n').strip().split(' ')
       xllcorner=float(paramline[1])
       paramline=fileline[3].rstrip('\n').strip().split(' ')
       yllcorner=float(paramline[1])
       paramline=fileline[4].rstrip('\n').strip().split(' ')
       cellsize=float(paramline[1])
       paramline=fileline[5].rstrip('\n').strip().split(' ')
       nodata_value=int(paramline[1])
       a=[]
       for line in fileline[6:]:
           line=line.rstrip('\n').strip().split(' ')
           a.append(np.array(line,float))
    finally:
       file_object.close()
    return ncols,nrows,xllcorner,yllcorner,cellsize,nodata_value,np.array(a,int)

def readMapMappingFile(mapFile):
    lines=[]
    try:
        f=open(mapFile)
        fileline=f.readlines()
        for line in fileline:
            line=line.rstrip('\n')
            lines.append(list(line.split(',')))
    finally:
        f.close()
    result=[]
    #actual data is from the second line
    for line in lines[1:]:
        lineresult=[]
        for linestr in line[1:]:
            lineresult.append(float(linestr))
        result.append(lineresult)
    return np.array(result,dtype=float)

def computeSurfaceAreaByMapFile(mapData,nrows,xllcorner,yllcorner,cellsize,modelTypeNum,fromLon,toLon,fromLat,toLat,Mapfile):
    mapType=readMapMappingFile(Mapfile)
    mapTypeNum=mapType.shape[0]
    if modelTypeNum<>mapType.shape[1]:
        print 'model Type number is different from the model type number in map file,please check the map file setting'
        return 0
    
    #begin of index x(lon direction)
    fromXi=round((fromLon-xllcorner)/cellsize)
    #end of index x(lon direction)
    toXi=round((toLon-xllcorner)/cellsize)
    #begin of index y(lat direction)
    fromYi=nrows-round((toLat-yllcorner)/cellsize+1)
    #end of index x(lat direction)
    toYi=nrows-round((fromLat-yllcorner)/cellsize+1)
    
    focusArr=mapData[fromYi:toYi,fromXi:toXi]    
    mapTypeAreaArr=np.zeros(shape=(mapTypeNum),dtype=float)
    modelTypeAreaArr=np.zeros(shape=(modelTypeNum),dtype=float)    
    total=float((toXi-fromXi)*(toYi-fromYi))
    ll=[]
    for ii in focusArr:
        for jj in ii:
            ll.append(jj)

    for l in ll:
        for m in range(modelTypeNum):
            modelTypeAreaArr[m]=modelTypeAreaArr[m]+mapType[l][m]
    modelTypeAreaArr=modelTypeAreaArr/total
    
    return modelTypeAreaArr

#search replaceGridDir file to replace the grid in modelTypeAreaArr 
def replaceCertainGridSurType(replaceGridDir,modelTypeAreaArr):
    for filename in os.listdir(replaceGridDir):
        aReplaceGridSurTypeFile = '\\'.join([replaceGridDir,filename])
        if os.path.isfile(aReplaceGridSurTypeFile):
            filenameExcludeEtr = filename.split('.')[0]
            filenamestrs = filenameExcludeEtr.split('_')
            try:
                i = int(filenamestrs[1])
                j = int(filenamestrs[2])
                modelTypeAreaArr[i][j] = readReplaceGridSurTypeFile(aReplaceGridSurTypeFile)
                print 'read from "'+aReplaceGridSurTypeFile+'", replace grid(',i,j,') surface type ' ,' as ',modelTypeAreaArr[i][j]
            except:
                print filename,' is an illegit filename of replace grid surface type'
        print '\n'
            

def readReplaceGridSurTypeFile(aReplaceGridSurTypeFile,modelTypeAreaArr):
    if os.path.exists(aReplaceGridSurTypeFile):
        lines = []
        f = open(aReplaceGridSurTypeFile)
        try:
            filelines = f.readlines()
            for fileline in filelines:
                line = fileline.rstrip('\n')
                l = list(line.split(','))
                try:
                    i = int(l[0])
                    j = int(l[1])
                    values = map(float,l[2:])
                    result = np.array(values,dtype=float)
                    modelTypeAreaArr[i][j] = result/100.0
                    print i,j,modelTypeAreaArr[i][j]
                except:
                    print aReplaceGridSurTypeFile,' is an illegit file for replace grid surface type'
        finally:
            f.close()
    else:
        print aReplaceGridSurTypeFile,' does not exists!'

if __name__=='__main__':
    a=readMapMappingFile('conf\\mapData2ModelMapData.csv')
    print a
    
