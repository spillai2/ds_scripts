import json
import pandas as pd
import numpy as np

path= '/home/san/python/data_analysis/pydata/ch02/usagov_bitly_data2012-03-16-1331923249.txt'

records = [json.loads(line) for line in open(path)]

##Counting time zones in pure python
time_zones = [rec['tz'] for rec in records if 'tz' in rec]

def get_counts(sequence):
    counts = {}
    for x in sequence:
        if x in counts:
            counts[x] += 1
        else:
            counts[x] = 1
    return counts

counts = get_counts(time_zones)

def top_counts(counts_dict, n=10):
    value_key_pairs = [(count, tz) for tz,count in counts_dict.items()]
    value_key_pairs.sort()
    return value_key_pairs[-n:]
    
top_counts(counts)

#Alternatively use collections.Counter. Use its 'most_common()' method
from collections import Counter
counts = Counter(time_zones)
counts.most_common(10)

##Counting time zones and more munging using pandas    
frame = pd.DataFrame(records)
clean_tz = frame['tz'].fillna('Missing')
clean_tz[clean_tz == ''] = 'Unknown'
tz_counts = clean_tz.value_counts()
tz_counts[:10]
# make a horizontal bar plot
tz_counts[:10].plot(kind='barh',rot=0)
# fetch all the browser info from column 'a' of the dataframe
# and see the most commonly used
browsers = pd.Series([x.split()[0] for x in frame.a.dropna()])
browsers.value_counts()
# decompose time zones into windows and non-windows using 'windows' string in frame['a]
cframe = frame[frame.a.notnull()]
os = np.where(cframe['a'].str.contains('Windows'), 'Windows', 'Not Windows')
# group data frame by time zones and OS
os_by_tz = cframe.groupby(['tz', os])
agg_counts = os_by_tz.size().unstack().fillna(0)
#select top overall timezones and split by OS
indexer = agg_counts.sum(1).argsort()
count_subset = agg_counts.take(indexer)[-10:]
# plot 
count_subset.plot(kind='barh', stacked=True)
# normalize rows to 1 and then plot, for better visibility of windows vs non-windows
norm_subset = count_subset.div(count_subset.sum(1), axis = 0)
norm_subset.plot(kind='barh', stacked=True)
