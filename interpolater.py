# -*- coding: cp936 -*-

import math
import numpy as np

'''nearest inteplot'''
#nΪx������������mΪy������������ncΪ�����Ŀ��x,y,z�ֱ�Ϊ�۲��ĺ������������ֵ����Ӧ��ĸ߳�ֵ��bbΪ���
#�������ĸ߳�ֵ�Ľ����dx,dy�ֱ�Ϊ������Ĳ���,x0,y0Ϊ��ʼ�������
def nearest(n,m,nc,x,y,z,dx,dy,x0,y0):  
   result=[[9999 for xx in range(n)] for yy in range(m)]
   nn=range(0,n)
   mm=range(0,m)
   print x
   for jj in nn:
       for kk in mm:
           A=x0+jj*dx
           B=y0+kk*dy
           mins=1000000.00
           for i in range(nc):
               Rs=(x[i]-A)*(x[i]-A)+(y[i]-B)*(y[i]-B)
               Rs=math.sqrt(Rs)
               if Rs<mins:
                   mins=Rs
                   ZResult=z[i]
           result[jj][kk]=ZResult
   return result

'''inserved distant weight interplot'''
#nΪx������������mΪy������������ncΪ�����Ŀ��x,y,z�ֱ�Ϊ�۲��ĺ������������ֵ����Ӧ��ĸ߳�ֵ��bbΪ���
#�������ĸ߳�ֵ�Ľ����dx,dy�ֱ�Ϊ������Ĳ���,x0,y0Ϊ��ʼ�������
#����ɺ͵�ͼһ���Ĵ��˳�򣬼�γ�ȷ���i=0ʱ���ڸ�γ��y1��γ����γ����ߵ�λ��
def inserveDW(n,m,nc,x,y,z,dx,dy,x0,y0):
    #print x,y,z
    result=np.zeros(shape=(m,n),dtype=float)
    for jj in range(m):
        for kk in range(n):
            A=y0+jj*dy
            B=x0+kk*dx
            TWs=0.0
            WSHTs=0.0
            for i in range(nc):
                Rs=(y[i]-A)*(y[i]-A)+(x[i]-B)*(x[i]-B)
                Rs=np.sqrt(Rs)
                Ws=1/(Rs+0.00000001)
                TWs=TWs+Ws
                WSHTs=WSHTs+Ws*z[i]
            ZResult= WSHTs/(TWs+0.00000001)
            result[m-1-jj][kk]=ZResult
    return result

'''cressman interplot'''
#nΪx������������mΪy������������ncΪ�����Ŀ��x,y,z�ֱ�Ϊ�۲��ĺ������������ֵ����Ӧ��ĸ߳�ֵ��bbΪ���
#�������ĸ߳�ֵ�Ľ����dx,dy�ֱ�Ϊ������Ĳ���,x0,y0Ϊ��ʼ�������
#MaxRidus:Ӱ�췶Χ
def cressman(MaxRidus,n,m,nc,x,y,z,dx,dy,x0,y0):
    #result=[[9999 for xx in range(n)] for yy in range(m)]
    rangeStep=(n*dx)/10
    for jj in range(n):
        for kk in range(m):
            A=x0+jj*dx
            B=y0+kk*dy
            StationNum=0
            TempA=MaxRidus-rangeStep
            #find three nearest points
            while(StationNum<3):
                TempA=TempA+rangeStep
                for i in range(nc):
                    Rs=(x[i]-A)*(x[i]-A)+(y[i]-B)*(y[i]-B)
                    Rs=math.sqrt(Rs)
                    if(Rs<TempA):
                        StationNum=StationNum+1
                if(TempA>5.0*MaxRidus):
                    break
            if(StationNum>=3):
               Ws=0.0
               TWs=0.0
               WSHTs=0.0
               for i in range(nc):
                  Rs=(x[i]-A)*(x[i]-A)+(y[i]-B)*(y[i]-B)
                  Rs=math.sqrt(Rs)
                  if(Rs<TempA): 
                     Ws=(TempA*TempA-Rs*Rs)/(TempA*TempA+Rs*Rs)
                     TWs=TWs+Ws
                     WSHTs=WSHTs+Ws*z[i]
               if TWs==0.0:
                  result[jj][kk]=9999.0
               else:
                  result[jj][kk]= WSHTs/TWs
            else:
               result[jj][kk]=9999 
    return result




