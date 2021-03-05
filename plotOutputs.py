import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

savings = pd.read_csv('Savings.csv')
savings = savings.drop(columns='YEARS')

accs = list(savings)

labels = []
plt.subplot(1,3,1)
for acc in accs[-4:]:
    data = savings[acc]
    plt.plot(data)
    labels.append(acc)
labels = tuple(labels)
plt.legend(labels) 

labels = []
plt.subplot(1,3,2)
for acc in accs[0:5]:
    data = savings[acc]
    plt.plot(data)
    labels.append(acc)
labels = tuple(labels)
plt.legend(labels)

labels = []
plt.subplot(1,3,3)
for acc in accs[5:7]:
    data = savings[acc]
    plt.plot(data)
    labels.append(acc)
labels = tuple(labels)
plt.legend(labels)
plt.show()

# print(data)