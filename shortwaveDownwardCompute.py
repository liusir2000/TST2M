# -*- coding: cp936 -*-
#__author__='Dongwei Liu'
#__Date__='2015-11-19'

#Function ComputeTrans(Press_hpa,temp_c_dew,G,Zenith)--compute Atmospheric transmittance
#Function getDoy(dt)--compute doy of day
#Function solar_zenith(lat,lng,dt)--compute solar zenith
#Function computeDewPoint(Temp_C,rh)--compute Dew Point
#Function computeKdown(lat,lon,BJT,CL,CM,CH,p_hpa,rh,ta_c)--compute shortwave radiation downward


import datetime
import time
import numpy as np


from constAndSetting import *


#-----------------------------------------------------------------------------
#compute doy of day
#-----------------------------------------------------------------------------
def getDoy(dt):
    d1=datetime.datetime(dt.year,1,1)
    return (dt-d1).days+1


#-----------------------------------------------------------------------------
#compute time zone
#-----------------------------------------------------------------------------
def getTimeZone(lon):
    if lon>=0:
        timeZone=int((lon+7.5)/15)
    else:
        timeZone=int((lon-7.5)/15)
    return timeZone

#---------------------------------------------------------------------------
#Function computeTrans is used to compute Atmospheric transmittance
#bulk atmospheric transmissivity (Crawford and Duchon, 1999)
#P is pressure (hPa)
#Td is dewpoint (C)
#G is parameter is empirical value from Smith 1966 (JAM) G=2.92 in Shanghai
# zenith in radians
#if zenith > 80 use the value for 80.
#----------------------------------------------------------------------------
def computeTrans(Press_hpa,temp_c_dew,G,zenith):
    DEG2RAD=0.017453292
    if zenith>80*DEG2RAD:
        cosZ=np.cos(80*DEG2RAD)
    else:
        cosZ=np.cos(zenith)
        
    #celsius to fahrenheit
    Tdf=temp_c_dew*1.8+32.0
    
    #compute optical mass
    #optical air mass at p=1013 mb
    m=35/np.sqrt(1224*cosZ*cosZ+1)
    
    #Rayleigh & permanent gases
    TrayTpg=1.021-0.084*np.sqrt(m*(0.000949*Press_hpa+0.051))

    #precipitable water
    w=np.exp(0.113-np.log(G+1)+0.0393*Tdf)

    #vapor transmission coeff
    Twat=1-0.077*((w*m)**0.3)

    #scattering by aerosols
    Taer=0.935**m

    if TrayTpg*Twat*Taer>10:
        print 'TrayTpg*Twat*Taer,w,m,temp_c_dew',TrayTpg,Twat,Taer,w,m,temp_c_dew

    return TrayTpg*Twat*Taer


def solar_zenith_new(lat,lon,dt):
    N=getDoy(dt)
    TimeZone=getTimeZone(lon)
    print TimeZone
    N0=79.6764+0.2422*(dt.year-1985)-int((dt.year-1985)/4.0)
    sitar=2*PI*(N-N0)/365.2422;
    ED=0.3723 + 23.2567*np.sin(sitar)+0.1149*np.sin(2*sitar)-0.1712*np.sin(3*sitar)-0.758*np.cos(sitar) + 0.3656*np.cos(2*sitar) + 0.0201*np.cos(3*sitar)
    ED = ED*PI/180  
    dLon = 0.0
    if (lon >= 0):
        if (TimeZone==-1):
            dLon = lon - (int((lon*10-75)/150)+1)*15.0
        else:
            dLon = lon - TimeZone*15.0
    else:
        if (TimeZone ==-1):
            dLon=(int((lon*10-75)/150)+1)*15.0- lon
        else:
            dLon=TimeZone*15.0-lon

    Et=0.0028-1.9857*np.sin(sitar)+9.9059*np.sin(2*sitar)-7.0924*np.cos(sitar)-0.6882*np.cos(2*sitar) 
    gtdt = dt.hour + dt.minute/60.0 + dt.second/3600.0 + dLon/15 
    gtdt = gtdt + Et/60.0
    dTimeAngle = 15.0*(gtdt-12)
    dTimeAngle = dTimeAngle*PI/180
    latitudeArc = lat*PI/180
    HeightAngleArc = np.arcsin(np.sin(latitudeArc)*np.sin(ED)+np.cos(latitudeArc)*np.cos(ED)*np.cos(dTimeAngle))
    CosAzimuthAngle = (np.sin(HeightAngleArc)*np.sin(latitudeArc)-np.sin(ED))/np.cos(HeightAngleArc)/np.cos(latitudeArc)
    AzimuthAngleArc = np.arccos(CosAzimuthAngle)
    HeightAngle = HeightAngleArc*180/PI
    AzimuthAngle = AzimuthAngleArc *180/PI
    if(dTimeAngle < 0):
        AzimuthAngle = 180 - AzimuthAngle
    else:
        AzimuthAngle = 180 + AzimuthAngle
        
    ZenithAngle = 90-HeightAngle
    return ZenithAngle*PI/180
	
#-----------------------------------------------------------------------------
#compute solar zenith
#Stull, 1989
#returns zenith in radians
#-----------------------------------------------------------------------------
def solar_zenith(lat,lng,dt):
    dt0=datetime.datetime(dt.year,dt.month,dt.day)
    t1=time.mktime(dt.timetuple())
    t2=time.mktime(dt0.timetuple())
    dectime=getDoy(dt)+(t1-t2)/24/60/60
    gamma=2*np.pi/365.25463*dectime
    eqtim=229.18*(7.5/100000+1.868/1000*np.cos(gamma)-0.032077*np.sin(gamma)\
         -0.014615*np.cos(2.*gamma)-0.040849*np.sin(2.0*gamma))
    decl=6.918/1000-0.399912*np.cos(gamma)+0.070257*np.sin(gamma)\
         -0.006758*np.cos(2.0*gamma)+9.07/10000*np.sin(2.0*gamma)-2.697/1000*np.cos(3.0*gamma)\
         +1.48/1000*np.sin(3.0*gamma)
    
    #Hour Angle
    ha=np.pi*(dt.hour-12)/12
    #ha=np.pi*(dt.hour)/12
    temp=np.sin(lat*np.pi/180)*np.sin(decl)+np.cos(lat*np.pi/180)*np.cos(decl)*np.cos(ha);
    return np.arccos(temp);

#------------------------------------------------------------------------------
#compute Dew Point ,from http://en.wikipedia.org/wiki/Dew_point
#------------------------------------------------------------------------------
def computeDewPoint(Temp_C,rh):
    g=((17.27*Temp_C)/(237.7+Temp_C))+np.log(rh/100)
    return (237.7*g)/(17.27-g);

#------------------------------------------------------------------------------
#compute shortwave radiation downward
#lat,lon:latitude and longitude 
#BJT:beijing location time
#CL,CH:cover of low,middle,high cloud        
#CLX,CHX:coeff of cloud
#p_hpa,rh,ta:atmospheric pressure(hpa)、dew Point(℃)、air temperature(℃)
#based on shao(1996)-<an automated Nowcasting Model of Road Surface Temperature
#    and State for Winter Road Maintenance>,a little change on computing tc
#------------------------------------------------------------------------------
def computeKdown(lat,lon,BJT,CL,CH,CLX,CHX,p_hpa,dewPoint,ta_c):
    zenith=solar_zenith(lat,lon,BJT);
    thedoy=getDoy(BJT);
    #the factor to account for deviation in mean earth-sun distance
    f=1+0.034*np.cos(2*np.pi*(thedoy-1)/365);
    tc=(1-CL*(1-CLX))*(1-CH*(1-CHX))
    #G=2.92
    G=2.67
    trans=computeTrans(p_hpa,dewPoint,G,zenith)*tc;
    result=f*R0*trans*np.cos(zenith)
        
    if result<0:
        return 0
    else:
        return result


if __name__=='__main__':
    lat=50.0
    lon=1.2
    dt=datetime.datetime(2013,8,13,18,0,0)
    cl=0.0912
    ch=1
    ps=1026.24
    ta=10.59
    rh=84
    dewPoint=8.16
    #zn=1.21
    #doy=345
    #dp=8.16
    #trans=0.49
    #kd=238.74

    
    x,y=solar_zenith(lat,lon,dt),solar_zenith_new(lat,lon,dt)
    print x*180/PI,np.cos(x),y*180/PI,np.cos(y),90-y*180/PI
    #print computeKdown(lat,lon,dt,cl,0,ch-cl,ps,dewPoint,ta)
    
    
