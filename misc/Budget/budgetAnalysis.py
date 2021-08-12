import numpy as np
import pandas as pd

file = 'transactions.csv'
transactions = pd.read_csv(file)

categories = list(set(transactions.Category))