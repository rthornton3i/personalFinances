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
    
    def class2df(obj):
        Utility.getAttr(obj)

    
    def getAttr(obj):
        attrs = []
        for att, _ in obj.__dict__.items():
            if not callable(getattr(obj, att)) and not att.startswith("__"):
                attrs.append(att)
                
        return attrs
    
    def getField(obj,field):
        vals = []
        fields = []
        for att, _ in obj.__dict__.items():
            if not callable(getattr(obj, att)) and not att.startswith("__"):
                vals.append(getattr(getattr(obj,att),field))
                fields.append(att)
                
        return vals,fields

    def normalize(x,xi,yi,xj=0,yj=1):
        norm = (((x - xi) / (yi - xi)) * (yj - xj)) + xj

        return 1 if norm > 1 else -1 if norm < -1 else norm
        