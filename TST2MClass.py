# -*- coding: cp936 -*-
#this class is the main class to run TST2M model
#author:Liu Dongwei;email:liudongwei2000@163.com
#unit:Shanghai Meteorological Science Research Institute

import dealFile as df
import numpy as np
import pandas as pd
import computeQs as cq
import datetime
import os
from constAndSetting import *

'''def force_restore(deltt,cap,aks,Qs,atslend,atsp):
     c2=2*PI/(24*3600)
     c1=0.95*2*np.sqrt(PI/(cap*aks*24*3600))
     tempc2=deltt*c2*(atsp-atslend)
     tempc1=deltt*c1*Qs
     ats=atsp+(tempc1-tempc2)
     return ats
'''
#cap:heat capacity,cm^-3 K^-1
#aks:thermal conductivity,cm^-1 s^-1 deg^-1
#deltt:time step,s
#tslend:soil border temperature,deg
#tsp: surface temperature at last time,deg
#ts:return surface temperature,deg
def force_restore(deltt,cap,aks,Qs,atslend,atsp,cof):
     c2=(24*3600)/2/PI
     c1=np.sqrt(0.5*c2*cap*aks)
     ats=atsp+cof*deltt*(Qs/c1-(atsp-atslend)/c2)
     return ats


class TST2MModel:
    def __init__(self,paramFilename):
        #read physical param from parameter setting file
        print 'Reading physical parameter setting....'  
        self.physicalParam=self.readPhysicalParamFormFile(paramFilename)
        print self.physicalParam,'\n'
        
        #get number of surface type
        self.surfaceTypeNum=len(self.physicalParam)
        
        #read variable from setting file
        print 'seting simulated range etc.:'
        print 'fromLon,toLon,fromLat,toLat,lonGridNum,latGridNum,stepNum'
        self.fromLon,self.toLon,self.fromLat,self.toLat = FROMLON,TOLON,FROMLAT,TOLAT
        self.lonGridNum,self.latGridNum,self.stepNum = GRIDXNUM,GRIDYNUM,STEPNUM
        print self.fromLon,self.toLon,self.fromLat,self.toLat,self.lonGridNum,self.latGridNum,self.stepNum,'\n'

        #get each grid longitude
        resx=abs((self.toLon-self.fromLon)/(self.lonGridNum-1))
        self.lon=np.arange(self.fromLon,self.toLon+0.0001,resx)

        #get lonstep
        self.lonStep=resx

        #get each grid latitude
        resy=abs((self.toLat-self.fromLat)/(self.latGridNum-1))
        self.lat=np.arange(self.toLat,self.fromLat+0.0001,resy)

        #get latstep
        self.latStep=resy

        #initialize surface temperature array
        self.ts=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize surface temperature of each surface type array
        self.tsOfEachType=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        #initialize air temperature array
        self.ta=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize net allwave radiation flux array
        self.qstar=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        #initialize storage flux array
        self.Qs=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        #initialize sensiable heat flux array
        self.H=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        #initialize talent heat flux array
        self.LE=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        #initialize kdown array
        self.Kdown=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize average net allwave radiation flux array in a single grid
        self.qstarAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize averagestorage flux array in a single grid
        self.QsAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize average sensiable heat flux array in a single grid
        self.HAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #initialize average talent heat flux array in a single grid
        self.LEAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        #middle used variable
  
        #energy changed due to surface temperature,sensible heat flux, talent heat flux
        self.alt=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)
        self.difh=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)
        self.difle=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum,self.surfaceTypeNum),dtype=float)

        self.altAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)
        self.difhAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)
        self.difleAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)
        self.energyByAirAverage=np.zeros(shape=(self.stepNum,self.latGridNum,self.lonGridNum),dtype=float)

        
    def readPhysicalParamFormFile(self,paramFilename):
        lines=[]
        f=open(paramFilename)
        try:
            fileline=f.readlines()
            for line in fileline:
                line=line.rstrip('\n')
                lines.append(list(line.split(',')))
        finally:
            f.close()  
        paramType=np.dtype({'names':lines[0],'formats': ['i','S30','f','f','f','f','f','f','f','f','f','f']}, align=True)
        result=[]
        #actual data is from the third line
        for line in lines[3:]:
            a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11=int(line[0]),line[1],float(line[2]),\
                                                  float(line[3]),float(line[4]),float(line[5]),\
                                                  float(line[6]),float(line[7]),float(line[8]),\
                                                  float(line[9]),float(line[10]),float(line[11])
            a=(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11)
            b=np.array(a,dtype=paramType)
            result.append(b)
        return np.array(result)

    def readSettingFromFile(self,settingFilename):
        lines=[]
        f=open(settingFilename)
        try:
            fileline=f.readlines()
            for line in fileline:
                line=line.rstrip('\n')
                lines.append(list(line.split('=')))
        finally:
            f.close()
            
        for line in lines:
            if line[0].lower()=='fromlon':
                fromlon=float(line[1])
            if line[0].lower()=='tolon':
                tolon=float(line[1])
            if line[0].lower()=='fromlat':
                fromlat=float(line[1])
            if line[0].lower()=='tolat':
                tolat=float(line[1])
            if line[0].lower()=='gridxnum':
                lonGridNum=int(line[1])
            if line[0].lower()=='gridynum':
                latGridNum=int(line[1])
            if line[0].lower()=='stepnum':
                stepNum=int(line[1])
                
        try:
            return fromlon,tolon,fromlat,tolat,lonGridNum,latGridNum,stepNum            
        except:
            print 'setting is not correct,please check the setting file--"setting.txt"'

    #initiate meterological data field include initiate ts0(surface temperature),ta0(air temperature)
    def initiateMetData(self,ts0,ta0):
        self.ta[0]=ta0
        self.ts[0]=ts0
        self.ts0=ts0
        self.ta0=ta0

        for y in range(self.surfaceTypeNum):
            for i in range(self.latGridNum):
                for j in range(self.lonGridNum):
                    if y==0: #water
                        self.tsOfEachType[0][i][j][y]=15.0
                    else:
                        self.tsOfEachType[0][i][j][y]=ts0[i][j]

    #get backgroud meterological data field include wind,td(dewpoint temperature),cloud cover
    #u,v,td,cl,ch:wind u,wind v,dewpoint,lower/middle cloud cover,high cloud cover
    #tslend,mlh:soil border temperature,mixed-well air block hight
    def setBackgroudMetDataOfEachTime(self,u,v,td,p,cl,ch,tslend,tUpLevel,mlb):
        #Wind U component ,shape with (stepNum+1,lonGridNum,latGridNum)
        self.u=u

        #Wind V component,shape with (stepNum+1,lonGridNum,latGridNum)
        self.v=v

        #dewpoint temperature,shape with (stepNum+1,lonGridNum,latGridNum)
        self.td=td

        #surface pressure,shape with (stepNum+1,lonGridNum,latGridNum)
        self.p=p

        #low/middle cloud cover,shape with (stepNum+1,lonGridNum,latGridNum)
        self.cl=cl

        #high cloud cover,shape with (stepNum+1,lonGridNum,latGridNum)
        self.ch=ch

        #constant lay temperature,shape with (lonGridNum,latGridNum)
        self.tslend=tslend

        #mixed-well air block height
        self.mlb=mlb

        #up level temperature
        self.tUpLevel = tUpLevel

    #set initial time
    def setInitiateTime(self,dt):
        self.initiateTime=dt

    #set anthropogenic heat
    def setQf(self,df):
        self.Qf=df

    #set surface type area proportion
    #SurfaceAreaArr:np.array(lonGridNum,latGridNum,typenum)
    def setSurfaceArea(self,surfaceAreaArr):
        self.surfaceArea=surfaceAreaArr

    #defferent way to compute incoming air temperature
    def computeTaIn(self,k,i,j,tempu,tempv,u_gridNum,v_gridNum,method):         
         #Method one: single grid move,one air block move from one grid swith to another
         if method==1:                               
             #wind from west to east(go ahead to west)
                  #else wind from east(go ahead to east)
             if tempu>0:
                  old_j=j-u_gridNum
                  if old_j<0:
                       old_j=0
             else:
                  old_j=j+u_gridNum
                  if old_j>=self.lonGridNum:
                       old_j=self.lonGridNum-1

             if tempv>0:
                  old_i=i+v_gridNum
                  if old_i>=self.latGridNum:
                       old_i=self.latGridNum-1
             else:
                  old_i=i-v_gridNum
                  if old_i<0:
                       old_i=0
             ta_in=self.ta[k-1][old_i][old_j]
             #if ta_in==0:
             #     print k-1,old_i,old_j,v_gridNum,u_gridNum

         #Method two:computed by the average temperature change of the air going throught as a line
         if method==2:               
             tempt=0
             if u_gridNum<v_gridNum:
                  for jj in range(u_gridNum):
                       if tempu>0:
                            tempj=j-jj
                            #limited to the range
                            if tempj<0:
                                 tempj=0
                       else:
                            tempj=j+jj
                            if tempj>=self.lonGridNum:
                                 tempj=self.lonGridNum-1

                       if tempv>0:
                            tempi=i+int(np.round(jj*(v_gridNum/u_gridNum),0))
                            if tempi>=self.latGridNum:
                                 tempi=self.latGridNum-1
                       else:
                            tempi=i-int(np.round(jj*(v_gridNum/u_gridNum),0))
                            if tempi<0:
                                 tempi=0

                       tempt=tempt+self.ta[k-1][tempi][tempj]
                  ta_in=tempt/u_gridNum
             else:
                  for ii in range(v_gridNum):
                       if tempv>0:
                            tempi=i+ii
                            #limited to the range
                            if tempi>=self.latGridNum:
                                 tempi=self.latGridNum-1
                       else:
                            tempi=i-ii
                            if tempi<0:
                                 tempi=0

                       if tempu>0:
                            tempj=j-int(np.round(ii*(u_gridNum/v_gridNum),0))
                            if tempj<0:
                                 tempj=0
                       else:
                            tempj=j+int(np.round(ii*(u_gridNum/v_gridNum),0))
                            if tempj>=self.lonGridNum:
                                 tempj=self.lonGridNum-1
                       tempt=tempt+self.ta[k-1][tempi][tempj]
                  ta_in=tempt/v_gridNum


         #Method three:computed by the average temperature change of the air going throught as an area
         if method==3:             
             tempt=0
             for jj in range(u_gridNum):
                  if tempu>0:
                       tempj=j-jj
                       #limited to the range
                       if tempj<0:
                            tempj=0
                  else:
                       tempj=j+jj
                       if tempj>=self.lonGridNum:
                            tempj=self.lonGridNum-1

                  for ii in range(v_gridNum):                  
                       if tempv>0:
                            tempi=i+ii
                            #limited to the range
                            if tempi>=self.latGridNum:
                                 tempi=self.latGridNum-1
                       else:
                            tempi=i-ii
                            if tempi<0:
                                 tempi=0
                       tempt=tempt+self.ta[k-1][tempi][tempj]
             ta_in=tempt/v_gridNum/u_gridNum


         #Method four:computed by the average temperature change of the air going throught as two line,one through U direct,other through V direct    
         if method==4:
             jj=0
             tempt=0.0
             while jj<=u_gridNum:
                  #wind from west to east
                  if tempu>0:
                       tempj=j+jj
                       #deal border
                       if tempj>=self.lonGridNum:
                            tempj=self.lonGridNum-1
                  #wind from east to west
                  else:
                       tempj=j-jj
                       #deal border
                       if tempj<0:
                            tempj=0
                  tempt=tempt+self.ta[k-1][i][tempj]
                  jj=jj+1
             ta_in=tempt/u_gridNum
             ta_out=self.ta[k-1][i][j]
             delt_ta_u=ta_in-ta_out
             
             tempt=0.0
             ii=0
             while ii<=v_gridNum:
                  #wind from south to north
                  if tempv>0:
                       tempi=i+ii
                       if tempi>self.latGridNum:
                            tempi=self.lonGridNum-1
                  else:
                       tempi=i+ii
                       if tempi<0:
                            tempi=0
                  tempt=tempt+self.ta[k-1][tempi][j]
                  jj=jj+1
             ta_in=tempt/v_gridNum
             ta_out=self.ta[k-1][i][j]
             delt_ta_v=ta_in-ta_out             
         return ta_in
             
               
    #compute moveable air energy
    #amlb is mixed-well air height
    def getEnergyByAirFlow(self,k,i,j,z0,amlb):
        if k==0:
             return 0
        tempu=self.u[k-1][i][j]
        tempv=self.v[k-1][i][j]
        u_distance=np.abs(tempu*3600/1000)
        v_distance=np.abs(tempv*3600/1000)

        u_gridNum=int(np.round(u_distance/np.abs((self.toLon-self.fromLon)*110/(self.lonGridNum-1))))
        v_gridNum=int(np.round(v_distance/np.abs((self.toLat-self.fromLat)*110/(self.latGridNum-1))))

        if u_gridNum==0:
             u_gridNum=1
        if v_gridNum==0:
             v_gridNum=1
             
        ta_in=self.computeTaIn(k,i,j,tempu,tempv,u_gridNum,v_gridNum,2)
        ta_out=self.ta[k-1][i][j]
        
        return (ta_in-ta_out)*amlb*ADST*ASPT/(np.e**(1+z0))
        #return (ta_in-ta_out)*amlb*ADST*ASPT
     
  
        

    #compute change of air temperature
    #diffta:change ta by  horizontal flow
    #difh,difle:change of sensiable heat flux and talent heat flux
    #diflt:change of surface heating(caused by surface temperature change)
    #amlb:height of mixed well air block
    #Adst:density of air Aspt
    #t_num:time span
    def getDeltTa(self,energyByAir,difh,difle,diflt,t_num,amlb,Adst,Aspt):
        tempe=diflt+difh+difle
        return tempe*t_num/(Adst*Aspt*amlb)+energyByAir/(Adst*Aspt*amlb)
        
    #compute a single grid surface temperature and air temperature
    #dt:Beijing time
    #k is time step number
    #i,j is the grid position(x,y)
    #y is index of surface type
    def computeSingleTypeTemperature(self,dt,k,i,j,y):
        #if ((k>=100) and (i<=1) and (j<=1)):
             #print 'computeSingleType beging',datetime.datetime.now()
        h=datetime.timedelta(hours=1)
        #compute current datetime
        cdt=dt+k*h

        #get surface temperature and air temperature of last time
        if k==0:
           atsp=self.tsOfEachType[k][i][j][y]
           #atsp=self.ts[k][i][j]
           atap=self.ta0[i][j]
        else:
           atsp=self.tsOfEachType[k-1][i][j][y]
           #atsp=self.ts[k-1][i][j]  
           atap=self.ta[k-1][i][j]

        atspk=atsp+273.15

        #get border surface temperature   
        atslend=self.tslend[i][j]
        #if the surface type is water,set tslend as 15 degree
        if y==0:
            atslend=15.0

        atslendk=atslend+273.15

        #capacity
        acap=self.physicalParam[y]['CAP']
        #conductivity
        aaks=self.physicalParam[y]['AKS']
        #emissivity
        aems_s=self.physicalParam[y]['EMS']
        #albedo
        aald=self.physicalParam[y]['ALD']
        #OHM a1
        a1=self.physicalParam[y]['a1']
        #OHM a2
        a2=self.physicalParam[y]['a2']
        #OHM a3
        a3=self.physicalParam[y]['a3']
        #LUMPS alph
        aalph=self.physicalParam[y]['alph']
        #LUMPS belt
        abelt=self.physicalParam[y]['belt']
        #zero height
        z0=self.physicalParam[y]['Z0']

        akdown,aqstar=cq.computeQstar(cdt,self.lat[j],self.lon[i],self.p[k][i][j],\
                              self.td[k][i][j],atap,atsp,\
                              self.cl[k][i][j],self.ch[k][i][j],aems_s,aald)
        
        #thinking about anthropogenic heat
        if ADDQF:
             d1=datetime.datetime(cdt.year,1,1)
             doy=(cdt-d1).days+1
             Qf=self.Qf[doy][cdt.hour]
             aqstar=aqstar+Qf
             
        #save net allwave radiation flux in this time
        self.qstar[k][i][j][y]=aqstar

        #get net allwave radiation flux in last time
        if k==0:
            aqstarp=aqstar
        else:
            aqstarp=self.qstar[k-1][i][j][y]

        deltt=60*60

        #compute storage flux
        aqs=cq.computeQs(a1,a2,a3,aqstar,aqstarp,deltt)

        #give a conf for compute surface temperature
        #if surface type is water conf=0.1
        #else conf=1.0
        if y==0:
            cof=0.1
        else:
            cof=1.0

        #compute current surface temperature
        atsk=force_restore(deltt,acap,aaks,aqs,atslendk,atspk,cof)
        ats=atsk-273.15
        self.tsOfEachType[k][i][j][y]=ats

        #get mixed well block air hight
        amlb=self.mlb[k]

        #compute sensiable heat flux and talent heat flux
        ah,ale=cq.computeHLE(atap,aalph,abelt,aqstar,aqs)
        self.H[k][i][j][y]=ah
        self.LE[k][i][j][y]=ale
        self.Qs[k][i][j][y]=aqs
        self.Kdown[k][i][j]=akdown
        
        #if k=0 means that current time is initiate time
        if k==0:
             return self.ts0[i][j],self.ta0[i][j],0
          
        #compute moveable air energy         
        energyByAir=self.getEnergyByAirFlow(k,i,j,z0,amlb)
        self.energyByAir=energyByAir

        #energy changed due to surface temperature
        alt=cq.SIG_M*(atsk**4-atspk**4)+cq.SIG_M*(self.tUpLevel[k][i][j]**4-self.tUpLevel[k-1][i][j]**4)
        self.alt[k][i][j][y]=alt

        self.difh[k][i][j][y]=self.H[k][i][j][y]-self.H[k-1][i][j][y]
        if self.difh[k][i][j][y]<0:
             if atsk-atspk>0:
                  self.difh[k][i][j][y]=0

   
        self.difle[k][i][j][y]=self.LE[k][i][j][y]-self.LE[k-1][i][j][y]
        if self.difle[k][i][j][y]<0:
             if atsk-atspk>0:
                  self.difle[k][i][j][y]=0
         
    
        #compute change of air temperature     
        self.deltTa=cof*self.getDeltTa(self.energyByAir,self.difh[k][i][j][y],0,self.alt[k][i][j][y],3600,amlb,ADST,ASPT)
        
        #compute air temperature in current time
        ata=self.ta[k-1][i][j]+self.deltTa
             
        return ats,ata,energyByAir

    #compute ts and ta of each time
    def run(self):
        h=datetime.timedelta(hours=1)

        for k in range(self.stepNum):
             print k,' simulating time:',self.initiateTime+k*h
             for i in range(self.lonGridNum):
                 #print 'step ',k,self.initiateTime+k*h,datetime.datetime.now(),i
                 for j in range(self.latGridNum):
                    if i==focusI and j==focusJ:
                        cq.Debuge=True
                    else:
                        cq.Debuge=False
                    tsOfGrid,taOfGrid,qstarOfGrid,qsOfGrid,LEOfGrid,HOfGrid,altOfGrid,difhOfGrid,difleOfGrid,energyByAirOfGrid=0,0,0,0,0,0,0,0,0,0
                    for y in range(self.surfaceTypeNum):                        
                        tmpts,tmpta,tmpEnergyByAir=self.computeSingleTypeTemperature(self.initiateTime,k,i,j,y)
                        self.tsOfEachType[k][i][j][y]=tmpts
                        tsOfGrid=tsOfGrid+tmpts*self.surfaceArea[i][j][y]
                        taOfGrid=taOfGrid+tmpta*self.surfaceArea[i][j][y]
                        energyByAirOfGrid=energyByAirOfGrid+tmpEnergyByAir*self.surfaceArea[i][j][y]
                        qstarOfGrid=qstarOfGrid+self.surfaceArea[i][j][y]*self.qstar[k][i][j][y]
                        qsOfGrid=qsOfGrid+self.surfaceArea[i][j][y]*self.Qs[k][i][j][y]
                        LEOfGrid=LEOfGrid+self.surfaceArea[i][j][y]*self.LE[k][i][j][y]
                        HOfGrid=HOfGrid+self.surfaceArea[i][j][y]*self.H[k][i][j][y]
                        altOfGrid=altOfGrid+self.surfaceArea[i][j][y]*self.alt[k][i][j][y]
                        difhOfGrid=difhOfGrid+self.surfaceArea[i][j][y]*self.difh[k][i][j][y]
                        difleOfGrid=difleOfGrid+self.surfaceArea[i][j][y]*self.difle[k][i][j][y]

                    self.ts[k][i][j]=tsOfGrid
                    self.ta[k][i][j]=taOfGrid
                    self.qstarAverage[k][i][j]=qstarOfGrid
                    self.QsAverage[k][i][j]=qsOfGrid
                    self.LEAverage[k][i][j]=LEOfGrid
                    self.HAverage[k][i][j]=HOfGrid
                    self.altAverage[k][i][j]=altOfGrid
                    self.difhAverage[k][i][j]=difhOfGrid
                    self.difleAverage[k][i][j]=difleOfGrid
                    self.energyByAirAverage[k][i][j]=difleOfGrid  




    
     


                                                        
                                                        
