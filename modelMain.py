# -*- coding: cp936 -*-
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd


from TST2MClass import *
import shortwaveDownwardCompute as sdc
import readDiamondData as rdd
import dealFile as df
from ReadAwsData import readAws
from interpolater import inserveDW
import getH as gm
import dealSurfaceType as dsft
from drawpic import drawPic

def dateStrToDatetime(astr):
    t=time.strptime(astr,"%Y%m%d%H")
    y,m,d,h=t[0:4]
    return datetime.datetime(y,m,d,h)

#get ecmwf data file name, dt is initiate time, i is the step
#headstr is the head string
def getEcDatafilename(headstr,dt,i):
    dtstr = dt.strftime("%y%m%d%H")
    stepstr = '%03d' % i
    return ''.join([headstr,dtstr,'.',stepstr])


def LonLat2ij(curLon,curLat,fromLon,toLon,fromLat,toLat,nx,ny):
    lonStep=(toLon-fromLon)/(nx-1)
    latStep=(toLat-fromLat)/(ny-1)
    j=round((curLon-fromLon)/lonStep)
    i=nx-1-round((curLat-fromLat)/latStep)
    return i,j
    

def computeOneTime(l,dt,sourceDataDir,resultDir):
     print '\nsimulate date ',dt.strftime("%Y-%m-%d"),'............'
     l.setInitiateTime(dt)
     h=datetime.timedelta(hours=1)
     filename='zdz_'+dt.strftime("%Y%m%d%H00.txt")
     filename='\\'.join([sourceDataDir,dt.strftime("%Y%m%d%H"),filename])
     a=readAws()
     a.readAwsDataFromFile(filename)
     fromLon,toLon,fromLat,toLat,nx,ny=l.fromLon,l.toLon,l.fromLat,l.toLat,l.lonGridNum,l.latGridNum
     lonStep=(toLon-fromLon)/(nx-1)
     latStep=(toLat-fromLat)/(ny-1)
     
     print '\nstep 1:initialize air temperature and surface temperature data'
     lonPoints,latPoints,tas,tss,tsb=[],[],[],[],[]
     pointNum=a.data.size
     validPointNum=0
     print pointNum
     for i in range(pointNum):
         print a.data[i]["sur_t"],a.data[i]["t"]
         if (a.data[i]["sur_t"]<100) and (a.data[i]["t"]<100):
             lonPoints.append(a.data[i]["lon"])
             latPoints.append(a.data[i]["lat"])
             tas.append(a.data[i]["t"])
             tss.append(a.data[i]["sur_t"])
             tsb.append(a.data[i]["Tsb"])
             validPointNum=validPointNum+1
     print validPointNum
     x=np.asarray(lonPoints,float)
     y=np.asarray(latPoints,float)
     z=np.asarray(tas,float)
     ta0=inserveDW(nx,ny,validPointNum,x,y,z,lonStep,latStep,fromLon,fromLat)
     z=np.asarray(tss,float)
     ts0=inserveDW(nx,ny,validPointNum,x,y,z,lonStep,latStep,fromLon,fromLat)
     z=np.asarray(tsb,float)
     print tas,tss,tsb
     tb=inserveDW(nx,ny,validPointNum,x,y,z,lonStep,latStep,fromLon,fromLat)     
     l.initiateMetData(ts0,ta0)

     print '\nstep 2:set background data'     
     rh=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     td=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     u=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     v=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     p=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     #lower cloud cover
     cl=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     #middle cloud cover
     cm=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     #total cloud cover
     ct=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     #high cloud cover
     ch=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     bta=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)
     tUpLevel=np.zeros(shape=(l.stepNum,l.latGridNum,l.lonGridNum),dtype=float)     
     mlb=np.zeros(shape=(l.stepNum+1),dtype=float)

     #get temperature in 850hpa
     headstr = 'T_850'
     rdd.fillData(tUpLevel,l,sourceDataDir,headstr,dt,l.stepNum)             

     
     #get u in 10 m
     headstr = '10u_999'
     rdd.fillData(u,l,sourceDataDir,headstr,dt,l.stepNum) 

     #get v in 10 m
     headstr = '10v_999'
     rdd.fillData(v,l,sourceDataDir,headstr,dt,l.stepNum) 

     #get lower cloud cover
     headstr = 'LCC_999'
     rdd.fillData(cl,l,sourceDataDir,headstr,dt,l.stepNum) 
     #print cl

     #get total cloud cover
     headstr = 'TCC_999'
     rdd.fillData(ct,l,sourceDataDir,headstr,dt,l.stepNum) 
     
     #get sea level pressure
     headstr = 'MSL_999'
     rdd.fillData(p,l,sourceDataDir,headstr,dt,l.stepNum) 


     #get dew temperature in 2m
     headstr = '2D_999'
     rdd.fillData(td,l,sourceDataDir,headstr,dt,l.stepNum) 

     #get air block height
     for i in range(0,l.stepNum):
         needTime=dt+i*h
         mlb[i]=gm.getHByDt(dt+h*i)
         
     ch = ct - cl
     l.setBackgroudMetDataOfEachTime(u,v,td,p,cl/10,ch/10,tb,tUpLevel,mlb)
     if ADDQF:
         print '       set Qf data'
         filename=confDir+'\\output-lucy.csv'
         qf=pd.read_csv(filename)

         qfArr=np.zeros(shape=(367,24),dtype=float)

         for d in qf.values:
             qfArr[d[0]][d[1]]=d[9]

         l.setQf(qfArr)
     
     print '\nstep 3: set iniatated time',dt
     l.setInitiateTime(dt)

     print '\nstep 4:run model from '+datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')+'...'
     l.run()
     print ' run finished at '+datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')

     #save grid data or not
     if SaveGridData:
           print 'saveing grid data.....'
           #save result to file
           resultSavedDir='\\'.join([resultDir,'grid',dt.strftime("%Y%m%d%H00")])
           if not os.path.exists(resultSavedDir):
               os.makedirs(resultSavedDir)
           for j in range(1,l.stepNum,1):
               cdt=l.initiateTime+h*j
               mystr=cdt.strftime("%m%d%H")
               np.savetxt(resultSavedDir+'\\ta'+mystr+'.txt', l.ta[j],fmt="%5.1f")
               df.addGisHead(resultSavedDir+'\\ta'+mystr+'.txt',l.lonGridNum,l.latGridNum,l.fromLon,l.toLat,np.abs((l.fromLat-l.toLat)/(l.latGridNum-1)),-9999)
               np.savetxt(resultSavedDir+'\\ts'+mystr+'.txt', l.ts[j],fmt="%5.1f")
               np.savetxt(resultSavedDir+'\\QsAverage'+mystr+'.txt', l.QsAverage[j],fmt="%5.1f")
               np.savetxt(resultSavedDir+'\\LEAverage'+mystr+'.txt', l.LEAverage[j],fmt="%5.1f")
               np.savetxt(resultSavedDir+'\\HAverage'+mystr+'.txt', l.HAverage[j],fmt="%5.1f")
               np.savetxt(resultSavedDir+'\\qstarAverage'+mystr+'.txt', l.qstarAverage[j],fmt="%5.1f")         
         
         
                 
if __name__=='__main__':
     mapDir,confDir,sourceDataDir,resultDir='conf','conf','dataSource','result'

     l=TST2MModel('\\'.join([confDir,'physicalParam.csv']))

     #initiate surfaceAreaArr
     surfAreaArr=np.zeros(shape=(l.latGridNum,l.lonGridNum,l.surfaceTypeNum),dtype=float)

     ncols,nrows,xllcorner,yllcorner,cellsize,nodata_value,mapData=dsft.readSurfaceData('\\'.join([mapDir,'land2011.txt']))
     for i in range(l.latGridNum):
          for j in range(l.lonGridNum):
               curToLat=l.fromLat-i*l.latStep
               curFromLat=l.fromLat-(i+1)*l.latStep
               curFromLon=l.fromLon+j*l.lonStep
               curToLon=l.fromLon+(j+1)*l.lonStep
               surfAreaArr[i,j]=dsft.computeSurfaceAreaByMapFile(mapData,nrows,xllcorner,yllcorner,\
                                                                   cellsize,l.surfaceTypeNum,curFromLon,curToLon,curFromLat,curToLat,'\\'.join([mapDir,'mapData2ModelMapData.csv']))
     #replace a certain grid surface type
     print 'replace grid surface type'
     replaceGridSurTypeFile = '\\'.join([confDir,'replaceMapPointSurType.csv'])
     dsft.readReplaceGridSurTypeFile(replaceGridSurTypeFile,surfAreaArr)
     #set surface type
     l.setSurfaceArea(surfAreaArr)

     #set station that wants to output serial data               
     lonLatName=df.readLonLatFile('\\'.join([confDir,'listStationForOutput.txt']))
     print lonLatName
     fromTime=datetime.datetime(2017,8,18)
     toTime=datetime.datetime(2017,8,18)     
     while fromTime<=toTime:
         ct=fromTime+20*ONE_HOUR       
         computeOneTime(l,ct,sourceDataDir,resultDir)
         fromTime=fromTime+24*ONE_HOUR

         print 'saving serial data...'
         serialDirstr='\\'.join([resultDir,'serial',ct.strftime("%Y%m%d%H")])
         if not os.path.exists(serialDirstr):
            os.makedirs(serialDirstr)
         for lln in lonLatName:
            for k in range(1,l.stepNum):
                i,j=LonLat2ij(lln[1],lln[2],l.fromLon,l.toLon,l.fromLat,l.toLat,l.lonGridNum,l.latGridNum)
                linestr=(l.initiateTime+k*ONE_HOUR).strftime("%Y-%m-%d %H:00 ")+' %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f'%(l.ta[k][i][j],l.ts[k][i][j],l.qstarAverage[k][i][j],\
                        l.QsAverage[k][i][j],l.LEAverage[k][i][j],l.HAverage[k][i][j],l.Kdown[k][i][j])
                LogFirstLinestr = 'datetime ta ts qstar Qs LE H Kdown'              
                df.writeLog(serialDirstr+'\\log_'+lln[0]+'.txt',linestr,LogFirstLinestr)
                for y in range(l.surfaceTypeNum):
                    linestr=(ct+k*ONE_HOUR).strftime("%Y-%m-%d %H:00 ")+' %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f %5.2f'%(l.tsOfEachType[k][i][j][y],l.qstar[k][i][j][y],\
                                                l.Qs[k][i][j][y],l.LE[k][i][j][y],l.H[k][i][j][y],l.tslend[i][j],l.tsOfEachType[k-1][i][j][y],l.surfaceArea[i][j][y])
                                                                                                                                       
                    LogFirstLinestr = 'datetime ts qstar Qs LE H pts AreaPercent'                                                                                                  
                    df.writeLog(serialDirstr+'\\log_'+lln[0]+l.physicalParam[y]['NAME']+'.txt',linestr,LogFirstLinestr)
                    
         resultSavedDir='\\'.join([resultDir,'img',ct.strftime("%Y%m%d%H")])

         print 'saving images ...'
         if not os.path.exists(resultSavedDir):
             os.makedirs(resultSavedDir)
             
         drawPic(l,l.ta,u'Ta($^\circ$C)','Ta',resultSavedDir)
         drawPic(l,l.ts,u'Ts($^\circ$C)','Ts',resultSavedDir)
         drawPic(l,l.qstarAverage,u'qstar(w/m^2)','qstar',resultSavedDir)
         drawPic(l,l.QsAverage,u'Qs(w/m^2)','Qs',resultSavedDir)
         drawPic(l,l.LEAverage,u'LE(w/m^2)','LE',resultSavedDir)
         drawPic(l,l.HAverage,u'H(w/m^2)','H',resultSavedDir)
         #drawPic(l,l.altAverage,u'diflt(w/m^2)','diflt',resultSavedDir)
         #drawPic(l,l.difhAverage,u'difh(w/m^2)','difh',resultSavedDir)
         #drawPic(l,l.difleAverage,u'difle(w/m^2)','difle',resultSavedDir)
         #drawPic(l,l.energyByAirAverage,u'EAir(w/m^2)','EAir',resultSavedDir)

