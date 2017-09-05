# -*- coding: cp936 -*-
import datetime

##CONSTANT
#air density(J/(g* ℃))
ADST = 1.00467

#air specific heat(g/m^3) 
ASPT = 1270.0

#circumference ratio
PI = 3.1415926

#Stefan_Boltzmann constant
SIG_M = 5.67/100000000   #W/(m^2*K^4)

#one hours step
ONE_HOUR = datetime.timedelta(hours=1)


#radian to angle
RAD2DEG = 57.29577951

#angle to radian
DEG2RAD = 0.017453292

#solar constant(w.m-2)
R0 = 1353.0

##SETTING FOR PROGRAM
#for Debuge some data of grid(focusI,focusJ) will
#be output separately.
DEBUG = False
focusI = 49
focusJ = 46

#wheather add anthropogenic heat(True) or not(False)
ADDQF = True

#need to save grid data(True) or not(False)
SaveGridData = True

#need to save serial data(True) or not(False)
SaveSerialData = True

#need to save image(True) or not(False)
SaveImage = True

#simulating range
FROMLON = 120.7
FROMLAT = 32
TOLON = 122.2
TOLAT = 30.5

#grid num
GRIDXNUM = 101
GRIDYNUM = 101

#simulating steps, the first one is used to save initiate data
STEPNUM = 25
