import numpy as np
#match mixed well air block height from 0 to 23 o'clock
arrMLH=[78,76,74,83,91,100,108,117,126,133,141,149,157,165,172,158,144,130,115,101,87,85,83,81]
mlhs=np.array(arrMLH)

def getHByDt(dt):
    h=dt.hour
    return mlhs[h]

if __name__=='__main__':
    import datetime
    dt = datetime.datetime(2017,8,12)
    h = datetime.timedelta(hours=1)
    for i in range(24):
        print getHByDt(dt)
        dt = dt + h
