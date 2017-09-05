# -*- coding: cp936 -*-
import matplotlib.pyplot as plt
import numpy as np
import datetime
import matplotlib as mpl

zhfont1 = mpl.font_manager.FontProperties(fname='E:/pythonProgram/study_example/font/simhei.ttf')
def drawPic(l,data,element,filename,resultSavedDir):
     plt.clf()
     h=datetime.timedelta(hours=1)       
     tsMax=int(np.max(data))
     tsMin=int(np.min(data))         
     norm=mpl.colors.Normalize(vmin=tsMin,vmax=tsMax)
     fig, axes = plt.subplots(nrows=4, ncols=6, sharex=True, sharey=True)
     fig.set_size_inches(12,7)
     fig.subplots_adjust(wspace=0.1)
     j = 0
     for ax in axes.flat:
         j=j+1
         cdt=l.initiateTime+h*j      
         im = ax.imshow(data[j],extent=(l.fromLon,l.toLon,l.toLat,l.fromLat),origin='upper',norm=norm)
         mystr=cdt.strftime("%y%m%d%H")
         ax.set_title(mystr)
         ax.set_xticks(np.arange(l.fromLon,l.toLon+0.5, 1.0))
         
     cax,kw = mpl.colorbar.make_axes([ax for ax in axes.flat])
     plt.colorbar(im, cax=cax, **kw)
     plt.title(element)
     #plt.show() 
     fig.savefig(resultSavedDir+'\\'+filename+'.png') 
