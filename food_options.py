import pandas as pd
import numpy as np

breakfast_options = pd.read_csv('breakfast.csv', index_col='options')
print(breakfast_options.loc['dairy smoothie']['fibre'])



