# -*- coding: cp936 -*-
#It is father class of reading scatter data，getDataForLinestr
#should be implitate in child class

import numpy as np

class readFileData:
    def readDataFromFile(self,filename,TypeName):
        linestrs=[]
        i=0
        file_object = open(filename,'r')
        try:
           fileline=file_object.readlines()
           for line in fileline:
               line=line.rstrip('\n').strip()
               line=' '.join(line.split('  '))
               line=' '.join(line.split('  '))
               linestrs.append(list((line.split(' '))))
               i=i+1
        finally:
           file_object.close()

        self.data=np.zeros((i,),dtype=TypeName)

        i=0           
        for linestr in linestrs:
            addElement=np.array([self.getDataForLinestr(linestr)],dtype=TypeName)
            self.data[i]=addElement
            i=i+1
   

    
