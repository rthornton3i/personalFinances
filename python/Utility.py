import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tick

class Utility:
    
    def expCurve(numel,steepness=3,reverse=False):
        steepness = steepness * (numel / 10)
        
        curve = np.exp(np.arange(numel)*(1/steepness))
        curve = (curve - min(curve)) / (max(curve) - min(curve))
        if reverse:
            curve = 1 - curve[::-1]
        
        if len(curve) == 1:
            curve = [1]
            
        return curve
    
    def avg(vals,avgType='simple',steepness=4):            
        if avgType.lower() == 'simple':
            mean = np.mean(vals)
        elif avgType.lower() == 'exponential':
            mean = np.average(vals,weights=Utility.expCurve(len(vals),steepness))
        elif avgType.lower() == 'logarithmic':
            mean = np.average(vals,weights=Utility.expCurve(len(vals),steepness,reverse=True))
        elif avgType.lower() == 'weighted':
            mean = np.average(vals,weights=np.arange(len(vals))+1)
        elif avgType.lower() == 'wilders':
            mean = 0
        elif avgType.lower() == 'median':
            mean = np.median(vals)
            
        return mean
        
    def nmspc2df(nmspc):
        def createDf(ns):
            tempDf = pd.DataFrame()
            
            attrs = Utility.getAttr(ns)
            for attr in attrs:
                tempDf[attr] = getattr(ns,attr)
            
            return tempDf

        if isinstance(nmspc,list):
            for i,ns in enumerate(nmspc):
                if i == 0:
                    df = createDf(ns)
                else:
                    tempDf = createDf(ns)
                    df = df.append(tempDf,ignore_index=True)
        else:
            df = createDf(nmspc)
                
        return df
    
    def dicts2df(dicts):
        if isinstance(dicts,list):
            for i,dic in enumerate(dicts):
                if i == 0:
                    df = pd.DataFrame.from_dict(dic)
                else:
                    df = df.append(pd.DataFrame.from_dict(dic))
        else:
            df = pd.DataFrame.from_dict(dicts)
            
        return df
    
    def getAttr(obj):
        attrs = []
        for a in dir(obj):
            if not callable(getattr(obj, a)) and not a.startswith("__"):
                attrs.append(a)
                
        return attrs

    def normalize(x,xi,yi,xj=0,yj=1):
        norm = (((x - xi) / (yi - xi)) * (yj - xj)) + xj

        return 1 if norm > 1 else -1 if norm < -1 else norm
        