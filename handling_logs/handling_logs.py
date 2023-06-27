import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
from pyparsing_logs import *
import pandas as pd

data = main()


df = pd.DataFrame(data)
print(set(df["appname"].values))


