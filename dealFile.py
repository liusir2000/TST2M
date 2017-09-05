# -*- coding: cp936 -*-
import os
import numpy as np

def mkdir(path):
    # 引入模块
 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
 
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        str1=u' 创建成功'
        print path+str1.encode('utf-8')
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        return False

def writetofile(filename,mystr):
     try:
         if os.path.isfile(filename):
             man_file = open(filename,'a')
         else:
             man_file = open(filename,'w')
         man_file.write(mystr+'\n')
     except IOError,e:
             print('File Error',e)
     man_file.close

def writeLog(filename,linestr,firstLinestr):
    try:
        if os.path.exists(filename):
            #print 'fileexists '+ filename
            f=open(filename,'a')
            f.write(linestr)
            f.write('\n')
        else:
            if firstLinestr<>'':
                f=open(filename,'w')
                f.write(firstLinestr)
                f.write('\n')
                f.write(linestr)
                f.write('\n')
    finally:
        f.close()

#read "name Lon Lat" from file
def readLonLatFile(filename):
    nameLonLats=[]
    file_object = open(filename,'r')
    try:
       fileline=file_object.readlines()
       for line in fileline:
           line=line.rstrip('\n').strip()
           if line<>'':
               lonLatStr=line.split(',')
               nameLonLats.append([lonLatStr[0],float(lonLatStr[1]),float(lonLatStr[2])])
    finally:
       file_object.close()
    return nameLonLats

def addGisHead(filename,ncols,nrows,xllcorner,yllcorner,cellsize,nodata_value):
    import os
    if os.path.exists(filename):
        f = open(filename,'r')
        linestrs=f.readlines()
        f.close()
        f = open(filename,'w')
        f.writelines('ncols '+str(ncols)+'\n')
        f.writelines('nrows '+str(nrows))
        f.writelines('xllcorner '+('%6.2f'%xllcorner).strip()+'\n')
        f.writelines('yllcorner '+('%6.2f'%yllcorner).strip()+'\n')
        f.writelines('cellsize '+('%6.4f'%cellsize).strip()+'\n')
        f.writelines('NODATA_value '+('%6.0f'%nodata_value).strip()+'\n')
        for linestr in linestrs:
            f.writelines(linestr)
        f.close()

if __name__=='__main__':
    m=readLonLatFile('conf\\listStationForOutput.txt')
    print m
