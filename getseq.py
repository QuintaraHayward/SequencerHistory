import os
import datetime
import pandas as pd
import csv
import re
from abifpy import Trace
import cutadapt

df_ab1 = pd.read_csv('df_ab1.csv', index_col=[0])
print(df_ab1.to_string())

subfolder_path = df_ab1['SubFolder Path'].tolist()
sequencer = []

for path in subfolder_path:
    # Split the string based on underscore character
    parts = path.split('_')
    # Access the fourth element (index 3) and get the first two characters
    if len(parts) > 3:
        first_two_chars = parts[3][:2]
        sequencer.append(first_two_chars)
    else:
        # Handle the case where there are not enough underscores in the string
        sequencer.append("")

print(sequencer)

df_ab1['Sequencer'] = sequencer

df_ab1.to_csv('df_ab1.csv')
