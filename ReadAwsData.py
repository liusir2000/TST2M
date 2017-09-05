# -*- coding: utf8 -*-
#自动站读取类readzdz.py
import numpy as np
from readFileData import readFileData
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

from interpolater import *

#定义自动站的数据类型
Z=np.dtype({'names':["name","lon","lat","t","rh",
                        "p","sur_t","tb","Tsb","fx","fs"],'formats': ['S10','f','f','f','f','f','f','f','f','f','f']}, align=True)

class readAws(readFileData):
    #从文件中读取自动站数据
    def readAwsDataFromFile(self,filename):
        return self.readDataFromFile(filename,Z)

    def getDataForLinestr(self,linestr):
        for i in range(1,31):
            if linestr[i]=='-':
                linestr[i]='9999'
        name,lon,lat,t,rh=linestr[0],float(linestr[1]),float(linestr[2]),float(linestr[3]),float(linestr[9])
        l=linestr[7].split(',')
        newstr=''.join(l)                  #处理气压数据中的","字符
        p=float(newstr)
        sur_t,tb,Tsb,fx,fs=float(linestr[23]),float(linestr[29]),float(linestr[27]),float(linestr[13]),float(linestr[14])
        return name,lon,lat,t,rh,p,sur_t,tb,Tsb,fx,fs

    def getSeaStaData(self,dt,ylType,fromLon,toLon,fromLat,toLat,xn,yn):                   #插值以后的数据
        lonStep=(toLon-fromLon)/(xn-1)
        latStep=(toLat-fromLat)/(yn-1)
        grid_x,grid_y=np.mgrid[fromLon:toLon:lonStep,fromLat:toLat:latStep]
        points=[]
        values=[]
        for i in range(self.data.size):
            points.append([self.data[i]["lon"],self.data[i]["lat"]])
            values.append(self.data[i]["total14"])
        #print points,values
        return griddata(points, values, (grid_x, grid_y), method='linear')

    def getLandStaData(self,dt,ylType,fromLon,toLon,fromLat,toLat,xn,yn):                   #插值以后的数据
        lonStep=(toLon-fromLon)/(xn-1)
        latStep=(toLat-fromLat)/(yn-1)
        grid_x,grid_y=np.mgrid[fromLon:toLon:lonStep,fromLat:toLat:latStep]
        points=[]
        values=[]
        for i in range(self.data.size):
            points.append([self.data[i]["lon"],self.data[i]["lat"]])
            values.append(self.data[i]["t"])
        return griddata(points, values, (grid_x, grid_y), method='linear')


if __name__=='__main__':
    filename='X:/gpsdata/forAll/20160906/201609061000.txt'
    a=readAws()
    a.readAwsDataFromFile(filename)
    fromLon,toLon,fromLat,toLat,nx,ny=120.7,122.2,30.5,32,201,201
    #grid_z2 =a.getLandStaData(1,1,120.7,122.2,30.5,32,nx,ny)
    lonStep=(toLon-fromLon)/(nx-1)
    latStep=(toLat-fromLat)/(ny-1)
    lonPoints,latPoints,valuesPoints=[],[],[]
    pointNum=a.data.size
    for i in range(pointNum):
        lonPoints.append(a.data[i]["lon"])
        latPoints.append(a.data[i]["lat"])
        valuesPoints.append(a.data[i]["t"])
    x=np.asarray(lonPoints,float)
    y=np.asarray(latPoints,float)
    z=np.asarray(valuesPoints,float)
    #grid_z2=cressman(2.0,nx,ny,pointNum,x,y,z,lonStep,latStep,fromLon,fromLat)
    grid_z2=inserveDW(nx,ny,pointNum,x,y,z,lonStep,latStep,fromLon,fromLat)
    #grid_z2=nearest(nx,ny,pointNum,x,y,z,lonStep,latStep,fromLon,fromLat)
    #grid_z2=zip(*grid_z2)
    plt.subplot(111)
    ax=plt.gca()
    #plt.imshow(grid_z2,extent=(120.7,122.2,30.5,32),origin='upper')
    plt.imshow(grid_z2,extent=(120.7,122.2,30.5,32),origin='upper')
    plt.title('Cubic')
    #plt.gcf().set_size_inches(6,6)
    plt.colorbar()#使用颜色条
    plt.show()

    





        
        
        

        
