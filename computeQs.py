import shortwaveDownwardCompute as sd
import numpy as np
from constAndSetting import *

#compute air emissivity
def prata_emis(tak,es):
    W=46.5*(es/tak);
    return 1.0-(1.0+W)*np.exp(-np.sqrt(1.2+3.0*W));

#compute humity from ta,td
def computeRH(ta,td):
    gd=17.27*td/(237.7+td);
    gt=17.27*ta/(237.7+ta);
    return 100*np.exp(gd-gt)

#compute net radiation flux
#dt is the datetime
#p,td,ta,ch,cl:pressure (hPa),dewpoint (C),air temperature(c)
#high cloud cover,low cloud cover
#lat,lon:latitude and longitude
#epsr,sarf:emissivity,albedo
#ts:surface temperature
def computeQstar(dt,lat,lon,p,td,ta,ts,cl,ch,emis_s,sarf):
    CLX=0.4
    CHX=0.8
    kdown=sd.computeKdown(lat,lon,dt,cl,ch,CLX,CHX,p,td,ta)
    if Debuge:
        pass
    if kdown<0:
        return 0,0

    rh=computeRH(ta,td)
    tsk=ts+273.15
    es_hpa=6.11*(10**(7.45*ta/(ta+235)))
    es_hpa=rh*es_hpa/100

    tak=ta+273.15
    emis_a=prata_emis(tak,es_hpa)

    ldown=emis_a*SIG_M*(tak**4)
    result=kdown*(1-sarf)+emis_s*(ldown-SIG_M*(tsk**4))-0.08*kdown*(1-sarf)
    return kdown,result

#compute storage flux by OHM
#a1,a2,a3 is the OHM coffient
#deltt is time step
def computeQs(a1,a2,a3,Qstar,Qstarp,deltt):
    Qs=a1*Qstar+a2*(Qstar-Qstarp)/deltt+a3
    return Qs

#compute sensible heat flux and latent heat flux
def computeHLE(t,a,b,aqstar,aqs):
    e=6.11*(10**7.5*t/(237.3+t))
    s=e*np.log(10)*7.5*237.3/(237.3+t)/(237.3+t)
    r=0.665
    #sensible heat flux and latent heat flux
    return (((1-a)+(r/s))/(1+(r/s)))*(aqstar-aqs)-b,(a/(1+(r/s)))*(aqstar-aqs)+b

                        
    

    
    
