import numpy as np

#d is the array should initiated,i is time index
#d1,d2,is the array data that value had set
#n,m,is the shape of d1 and d2
def getThreeForOne(d,index,n,m):
    for i in range(n):
        for j in range(m):
            deltd=(d[index+2][i][j]-d[index-1][i][j])/3
            d[index][i][j]=d[index-1][i][j]+deltd

def getThreeForTwo(d,index,n,m):
    for i in range(n):
        for j in range(m):
            deltd=(d[index+1][i][j]-d[index-2][i][j])/3
            d[index][i][j]=d[index-2][i][j]+2*deltd

#fill the array by file heading with headstr in dirstr        
def fillData(data,setting,dirstr,headstr,dt,times):
     filenamehead=dirstr+'\\'+dt.strftime("%Y%m%d%H")+'\\'+headstr+'_'+dt.strftime("%y%m%d%H")
     #resLat=(setting.fromLat-setting.toLat)/(setting.latGridNum-1)
     for k in range(times):
          if ((k%3)==0):
               fileExt='%03d'%k
               filename=filenamehead+'.'+fileExt
               '''
               lonStep,latStep,fromLon,toLon,fromLat,toLat,xnum,ynum,tempData=rd.readDiamondDataFromFile(filename)
               for i in range(setting.latGridNum):
                    for j in range(setting.lonGridNum):
                         curLat=setting.fromLat-i*resLat
                         curLon=setting.fromLon+j*resLon
                         data[k][i][j]=rd.insertData(tempData,lonStep,latStep,fromLon,toLon,fromLat,toLat,curLon,curLat)
               '''
               DiamondDataToModelData(filename,setting,data[k])
               
     for k in range(times):
          if ((k%3)==1):
               getThreeForOne(data,k,setting.latGridNum,setting.lonGridNum)
               
          if ((k%3)==2):
               getThreeForTwo(data,k,setting.latGridNum,setting.lonGridNum)


def DiamondDataToModelData(filename,setting,datak):
    lonStep,latStep,fromLon,toLon,fromLat,toLat,xnum,ynum,diamondDataTd=readDiamondDataFromFile(filename)
    resLat=np.abs((setting.toLat-setting.fromLat)/(setting.latGridNum-1))
    resLon=(setting.toLon-setting.fromLon)/(setting.lonGridNum-1)
    for i in range(setting.latGridNum):
          for j in range(setting.lonGridNum):
               curLat=setting.fromLat-i*resLat
               curLon=setting.fromLon+j*resLon
               datak[i][j]=insertData(diamondDataTd,lonStep,latStep,fromLon,toLon,fromLat,toLat,curLon,curLat)


def readDiamondDataFromFile(filename):
    linestrs=[]
    i=0
    file_object = open(filename,'r')
    try:
       fileline=file_object.readlines()
       paramline=fileline[2].rstrip('\n').strip().split(' ')
       lonStep=float(paramline[0])
       latStep=float(paramline[1])
       fromLon=float(paramline[2])
       toLon=float(paramline[3])
       fromLat=float(paramline[4])
       toLat=float(paramline[5])
       xnum=int(paramline[6])
       ynum=int(paramline[7])
       #print xnum,ynum
       a=[]
       for line in fileline[3:]:
           line=line.rstrip('\n').strip().split('\t')
           a.append(np.array(line,float))
    finally:
       file_object.close()

    return lonStep,latStep,fromLon,toLon,fromLat,toLat,xnum,ynum,np.array(a,float)

#compute the value of position (curLon,curLat) from diamond data array(diamondData)
#be sure that (curLon,curLat) is in the range of lon ,lat
def insertData(diamondData,lonStep,latStep,fromLon,toLon,fromLat,toLat,curLon,curLat):
    x0=int(np.trunc((curLon-fromLon)/lonStep))
    y0=np.abs(int(np.trunc((fromLat-curLat)/latStep)))
    x1=x0+1
    y1=y0+1
    
    lon=x0*lonStep+fromLon
    lat=fromLat+y0*latStep
    h1=np.sqrt((lon-curLon)*(lon-curLon)+(lat-curLat)*(lat-curLat))
    w1=1/(h1+1e-8)

    lon=x0*lonStep+fromLon
    lat=fromLat+y1*latStep
    h2=np.sqrt((lon-curLon)*(lon-curLon)+(lat-curLat)*(lat-curLat))
    w2=1/(h2+1e-8)

    lon=x1*lonStep+fromLon
    lat=fromLat+y0*latStep
    h3=np.sqrt((lon-curLon)*(lon-curLon)+(lat-curLat)*(lat-curLat))
    w3=1/(h3+1e-8) 
    
    lon=x1*lonStep+fromLon
    lat=fromLat+y1*latStep
    h4=np.sqrt((lon-curLon)*(lon-curLon)+(lat-curLat)*(lat-curLat))
    w4=1/(h4+1e-8)

    #deal with missing data(value=9999)
    if np.abs(diamondData[y0][x0])>2000:
        z1=0
        w1=0
    else:
        z1=diamondData[y0][x0]

        
    if np.abs(diamondData[y0][x1])>2000:
        z3=0
        w3=0
    else:
        z3=diamondData[y0][x1]

    if np.abs(diamondData[y1][x0])>2000:
        z2=0
        w2=0
    else:
        z2=diamondData[y1][x0]


    if np.abs(diamondData[y1][x1])>2000:
        z4=0
        w4=0
    else:
        z4=diamondData[y1][x1]

        
    if ((z1+z2+z3+z4)==0) and ((z1*z2*z3*z4)==0) and (np.abs(diamondData[y1][x0])>2000):
        result=9999
    else:
        result=(z1*w1+z2*w2+z3*w3+z4*w4)/(w1+w2+w3+w4)
    return result
    
if __name__=='__main__':
    lonStep,latStep,fromLon,toLon,fromLat,toLat,xnum,ynum,x=readDiamondDataFromFile(r"dataSource\2016080120\2D_999_16080120.000")
    
