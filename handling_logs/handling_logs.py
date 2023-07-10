import sys
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/reading_logs/')
from pyparsing_logs import *
from pyparsing_logs_network import *
import pandas as pd

data_main = pyparse_logs()
data_network = pyparse_logs_network()


df_main = pd.DataFrame(data_main)
df_network = pd.DataFrame(data_network)
df = pd.concat([df_main, df_network], ignore_index=True)


# print(set(df_main["hostname"].values))
# print(df_main.head)
# print(set(df_network["hostname"].values))
# print(df_network.head)
print(df.head)


