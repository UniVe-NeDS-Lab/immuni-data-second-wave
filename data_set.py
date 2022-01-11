import csv
import pandas as pd

pew_data = {}
data_folder = 'static-data/'
pew_datafile = data_folder+'pew-2018.csv'
istat_datafile = data_folder+'italian-population-Jan-2019-ISTAT.csv'
rt_file = data_folder+'rt.csv'

istat_data = {}
istat_total_adults = 0


with open(pew_datafile, newline='') as pew:
    """ smartphone usage for age 18+ """
    data = csv.DictReader(pew)
    for line in data:
        d = {k: float(line[k])/100 for k in line if k != 'Country'}
        pew_data[line['Country']] = d

with open(istat_datafile, newline='') as istat:
    """ Italian demographics, you can download the app if you are 14 """
    data = csv.DictReader(istat)
    for line in data:
        if line['Territory'] == 'Italy' and line['Gender'] == 'total':
            if line['Age'] != 'total':
                age = int(line['Age'].split()[0])
                num = int(line['Value'])
                istat_data[age] = num
                if age >= 14:
                    istat_total_adults += num


rt = pd.read_csv(rt_file,
                 parse_dates=["data"],
                 dtype={'Rt': float},
                 index_col="data")

W = 1860000/2768968
# extracted from the swisscovid app open data, in date 12/11/2020
P = 1  # perfect, as immuni abunds
# P = 0.81  # from ComCom paper, unised in TCSS paper
# this is an estimation of the ratio between running apps and downloads


