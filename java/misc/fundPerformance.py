import numpy as np
import matplotlib.pyplot as plt

star = [21.43,22.21,-5.34,18.33,6.55,-0.15,7.35,17.80,13.79,0.77]
indAdm = [18.37,31.46,-4.43,21.79,11.93,1.36,13.64,32.33,15.96,2.08]
lifeInc = [9.13,12.05,-1.05,6.98,4.58,0.22,6.76,3.40,6.54,3.77]
lifeConGrow = [11.51,15.68,-2.95,10.92,5.96,-0.17,6.95,9.08,9.19,1.76]

years = 10
loops = 1000
startValue = 100000

acc = np.divide(lifeInc,100)
mu = np.mean(acc)
sigma = np.std(acc)

print('Mean: ' + format(mu*100,'.2f') + '%')
print('Std:  ' + format(sigma*100,'.2f') + '%')

#plt.close('all')

totalValue = []
allValue = []
annualPerf = []
for i in range(loops):
    earnings = [np.random.normal(mu,sigma) for n in range(years)]
    
    value = [startValue]
    perf = [0]
    for n in range(years-1):
        value.append(value[n]*(1+earnings[n]))
        perf.append((value[n]/value[n-1])-1)
    
    allValue.append(value)
    totalValue.append(value[-1])
    annualPerf.append(np.mean(perf))

plt.figure(1)
plt.clf()
for ind,value in enumerate(allValue):
    r = 1 - ((totalValue[ind] - min(totalValue)) / (max(totalValue) - min(totalValue)))# if totalValue[ind] <= max(totalValue) / 2 else 0
    g = (totalValue[ind] - min(totalValue)) / (max(totalValue) - min(totalValue))# if totalValue[ind] > max(totalValue) / 2 else 0
    b = (totalValue[ind] - min(totalValue)) / ((max(totalValue) - min(totalValue)) / 2) if \
            totalValue[ind] - min(totalValue) <= (max(totalValue) - min(totalValue)) / 2 else \
            1 - (((totalValue[ind] - min(totalValue)) / ((max(totalValue) - min(totalValue)) / 2)) - 1)
#    b = 0
    plt.plot(value,color=(r,g,b),linewidth=0.5)
plt.plot(np.mean(allValue,axis=0),color='k',linewidth=1)
plt.plot(np.arange(years),np.ones((years))*startValue,'k--',linewidth=1)
plt.title('Account Value over Time')
    
plt.figure(2)
plt.clf()
fig,ax = plt.subplots(2,1,num=2)
ax[0].hist(totalValue,bins=30)
ax[0].set_title('Final Account Value')
ax[1].hist(annualPerf,bins=30)
ax[1].set_title('Annual Performance')