import urllib.request
import datetime
import csv
import os
import data_set
import pandas as pd
import numpy as np
from copy import copy
from pathlib import Path


class DataFetcher():
    """ Check if we have a cache, else just download new data.
        Can be used for other apps and other data too. """

    cache_folder = './cache-data/'
    Path(cache_folder).mkdir(parents=True, exist_ok=True)
    data_folder = './data/'
    Path(data_folder).mkdir(parents=True, exist_ok=True)

    def check_cache(self, fname, age=0):
        try:
            st = os.stat(fname)
        except IOError:
            return False
        last_mod = st.st_mtime
        if last_mod > age:
            return True

    def fetch_file(self, url, fname='', age=0):
        if not self.check_cache(fname, age):
            urllib.request.urlretrieve(url, fname)

    def fetch_csv(self, url, fname='', age=0):
        self.fetch_file(url, fname, age)
        with open(fname, newline='') as f:
            download = csv.DictReader(f)
            return [dict(d) for d in download]


class ItalianData(DataFetcher):
    """ Specific class for the Italian Covid data """

    infection_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/"\
                     "master/dati-andamento-nazionale/"\
                     "dpc-covid19-ita-andamento-nazionale.csv"
    regional_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master"\
                    "/dati-regioni/dpc-covid19-ita-regioni-"
    population_data = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-statistici-riferimento/popolazione-istat-regione-range.csv"

    date = "data"

    infected_daily = "nuovi_positivi"
    tested_total = "tamponi"
    tested_people = "tamponi"
    start_date = '20200813'
    end_date = '20201104'
    # more available fields, in case they are useful:
    # ,stato,ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,
    # isolamento_domiciliare,totale_positivi,variazione_totale_positivi,
    # nuovi_positivi,dimessi_guariti,deceduti,casi_da_sospetto_diagnostico,
    # casi_da_screening,totale_casi,tamponi,casi_testati,note
    cache_infected_file = DataFetcher.cache_folder + 'italy_data.csv'
    labels = [infected_daily, tested_total, tested_people]
    download_types = {x: np.int32 for x in labels}
    regional_data_dict = {}
    population_data_dict = {}
    start_day = datetime.datetime(int(start_date[:4]),
                                  int(start_date[4:6]),
                                  int(start_date[6:8]))
    end_day = datetime.datetime(int(end_date[:4]),
                                int(end_date[4:6]),
                                int(end_date[6:8]))

    def __init__(self):
        self.infected_dict = {}

    def fetch_regional_data(self):
        """ Fetch data region by region """
        day = copy(self.start_day)
        data_dic = {}
        while day < self.end_day:
            date_str = f"{day.year:4d}{day.month:02d}{day.day:02d}.csv"
            data_file = self.regional_data + date_str
            cache_file = self.cache_folder + 'regional-data' + date_str
            data_dic[date_str[0:8]] = self.fetch_csv(data_file, cache_file,
                                                     age=24*60*60*1000)
            day += datetime.timedelta(days=1)
        cache_file = self.cache_folder + 'population-data.csv'
        population_data = self.fetch_csv(self.population_data, cache_file,
                                         age=24*60*60*1000)
        return data_dic, population_data

    def update_data(self):
        infected = self.fetch_csv(self.infection_data,
                                  self.cache_infected_file,
                                  age=24*60*60)
        for row in infected:
            data_line = {x: int(row[x]) for x in self.labels if row[x]}
            d = datetime.datetime.strptime(row[self.date], '%Y-%m-%dT%H:%M:%S')
            self.infected_dict[d] = data_line
        self.regional_data_dict, self.population_data_dict = \
            self.fetch_regional_data()
        self.compute_incidence()

    def compute_incidence(self, window=14, scale_factor=6):
        outfile = self.data_folder + 'regions.csv'
        region_codes = {}
        grand_total = 0
        # get data for total population
        for line in self.population_data_dict:
            code = line['codice_regione']
            if code not in region_codes:
                region_codes[code] = 0
            else:
                region_codes[code] += int(line['totale_generale'])
                grand_total += int(line['totale_generale'])
        day = copy(self.start_day)
        counter = 1
        data_list = []
        # get positive by region
        while day < self.end_day:
            date_str = f"{day.year:4d}{day.month:02d}{day.day:02d}"

            all_regions = self.regional_data_dict[date_str]
            region_dict = {}
            for reg in all_regions:
                region_dict[reg['codice_regione']] = reg['nuovi_positivi']
            data_list.append([date_str, region_dict])
            day += datetime.timedelta(days=1)

        window_incidence = []
        # we start from window-1, e.g. 13
        for i in range(window-1, len(data_list)):
            date_str = data_list[i][0]
            date = date_str[0:4]+'-'+date_str[4:6]+'-'+date_str[6:8]
            data_row = {}
            data_row['date'] = date
            tot_incidence = 0
            min_inc = 1000000  # just a big number
            max_inc = 0
            for code in data_list[i][1]:
                if code not in window_incidence:
                    data_row[code] = []
                tot_region_by_window = 0
                # we sum from i-window to i, we range from i+1-window to i+1,
                # e.g. from 13+1-14=0 to 14 (excluding the last)
                for day_index in range(i+1-window, i+1):
                    tot_region_by_window += int(data_list[day_index][1][code])
                tot_incidence += tot_region_by_window
                data_row[code] = tot_region_by_window/region_codes[code]
                if data_row[code] > max_inc:
                    max_inc = data_row[code]
                if data_row[code] < min_inc:
                    min_inc = data_row[code]
            data_row['Tot AVG'] = tot_incidence/grand_total
            # scale_factor = 6 comes from seroprevalence study in Italy
            data_row['rescaled'] = scale_factor*tot_incidence/grand_total
            data_row['min'] = min_inc*scale_factor
            data_row['max'] = max_inc*scale_factor
            window_incidence.append(data_row)

        with open(outfile, 'w', newline='') as csvfile:
            fieldnames = ['date'] + [code for code in region_codes] + \
                         ['Tot AVG', 'rescaled', 'min', 'max']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in window_incidence:
                writer.writerow(row)


class Immuni(DataFetcher):
    download_data = "https://raw.githubusercontent.com/immuni-app/"\
                    "immuni-dashboard-data/master/dati/andamento-download.csv"
    national_data = "https://raw.githubusercontent.com/immuni-app/"\
                    "immuni-dashboard-data/master/dati/"\
                    "andamento-dati-nazionali.csv"
    regional_data = "https://raw.githubusercontent.com/immuni-app/"\
                    "immuni-dashboard-data/master/dati/"\
                    "andamento-settimanale-dati-regionali.csv"
    # column names for download file
    date = 'data'
    week = 'settimana'
    ios_daily = 'ios'
    android_daily = 'android'
    ios_android = 'ios_android'
    ios_total = 'ios_total'
    android_total = 'android_total'
    ios_android_total = 'ios_android_total'

    download_labels = [ios_daily, android_daily, ios_android, ios_total,
                       android_total, ios_android_total]
    download_types = {x: np.int32 for x in download_labels}
    download_types[date] = 'str'
    # column names for data file
    warning_sent_daily = 'notifiche_inviate'
    positive_users_daily = 'utenti_positivi'
    warning_sent_tot = 'notifiche_inviate_totali'
    positive_users_tot = 'utenti_positivi_totali'

    warning_labels = [warning_sent_daily, positive_users_daily,
                      warning_sent_tot, positive_users_tot]

    region = 'denominazione_regione'
    warning_labels_regional = [region, warning_sent_daily,
                               positive_users_daily,
                               warning_sent_tot, positive_users_tot]
    warning_types = {x: np.int32 for x in warning_labels}
    warning_types_regional = {x: np.int32 for x in warning_labels_regional}
    warning_types[date] = 'str'
    cache_download_file = DataFetcher.cache_folder + 'immuni-download.csv'
    cache_warning_file = DataFetcher.cache_folder + 'immuni-warnings.csv'
    cache_warning_file_regional = DataFetcher.cache_folder + \
                                  'immuni-warnings-regional.csv'
    refresh_interval = 24*60*60  # once per day

    def __init__(self, Rt, monitor_period=7):
        self.Rt = Rt
        self.print_labels = self.download_labels[:] + ['nuovi_positivi',
                                                       'iprime',
                                                       'nt', 'rho']
        for rt in self.Rt:
            self.print_labels.append('PPV-'+str(rt))
        self.print_labels.extend(['daily_tests',
                                  'daily_tests_per_person', 'Rt',
                                  'rescaled_warnings',
                                  'rescaled_warnings_weekly',
                                  'positive_users_weekly',
                                  'alpha_weekly',
                                  self.positive_users_daily])
        self.download_dict = {}
        self.warning_dict = {}
        self.ios_download = 0
        self.android_download = 0
        self.warning_sent_tot_number = 0
        self.sprime = 0
        self.iprime = 0
        self.D = 0
        self.M = data_set.pew_data['Italy']['Total']
        self.R = data_set.istat_total_adults
        self.monitor_period = monitor_period

    def fetch_data(self):
        download = self.fetch_csv(self.download_data, self.cache_download_file,
                                  age=self.refresh_interval)
        national_data = self.fetch_csv(self.national_data,
                                       self.cache_warning_file,
                                       age=self.refresh_interval)
        regional_data = self.fetch_csv(self.regional_data,
                                       self.cache_warning_file_regional,
                                       age=self.refresh_interval)
        return download, national_data, regional_data

    def update_data(self, national_data=None):
        self.fetch_data()
        warning = pd.read_csv(self.cache_warning_file,
                              parse_dates=[self.date],
                              dtype=self.warning_types,
                              index_col=self.date)
        # documentation says that if warnings are below 5 they use -1 (?)
        # remove the days without warnings or negative ones
        warning = warning[warning[self.warning_sent_tot] > 0]
        download = pd.read_csv(self.cache_download_file,
                               parse_dates=[self.date],
                               dtype=self.download_types,
                               index_col=self.date)

        self.dataset = warning.join(download, how='inner')
        if national_data:
            infections = pd.read_csv(national_data.cache_infected_file,
                                     parse_dates=[national_data.date],
                                     dtype=self.download_types,
                                     index_col=self.date)
            infections.index = infections.index.normalize()
            self.dataset = self.dataset.join(infections, how='inner')
            self.dataset = self.dataset.join(data_set.rt, how='inner')
        self.ios_download = download.tail(1)[self.ios_total]
        self.android_download = download.tail(1)[self.android_total]

        def rescale_warnings(line):
            """ Rescale warnings according to the comment on immuni
                dashboard github """
            if line[self.warning_sent_daily] < 0:  # if warnings < 5
                return 0                           # they use -1
            scaling_f = (3*self.android_download + self.ios_download) /\
                        (self.android_download + self.ios_download)
            return int(line[self.warning_sent_daily]*scaling_f)

        self.dataset['rescaled_warnings'] = self.dataset.apply(
                                                rescale_warnings,
                                                axis=1)

    def compute_contacts_number(self, window=7):
        max_day = self.dataset.index[-1]
        min_day = self.dataset.index[0]
        window_td = pd.Timedelta(days=window)
        one_day = pd.Timedelta(days=1)
        freq = '-' + str(window) + 'D'
        dates = []
        nts = []
        iprimes = []
        rhos = []
        PPV_dict = {}
        # we passed a list of Rt to the constructor, we will have more than
        # PPV column with a different Rt
        if isinstance(self.Rt, list):
            for rt in self.Rt:
                PPV_dict[rt] = []
        daily_tests = []
        tests_per_person = []
        for end_day in pd.date_range(max_day, min_day + window_td - one_day,
                                     freq='-1D'):
            start_day = end_day - window_td
            win_frame = self.dataset.iloc[(self.dataset.index <= end_day) &
                                          (self.dataset.index > start_day)]
            Sprime = win_frame['rescaled_warnings'].sum()
            avg_downloads = win_frame[self.ios_android_total].mean()
            tot_warnings = win_frame[self.ios_android_total].mean()
            A = avg_downloads/self.R
            ct = self.M*data_set.W*A
            iprime = win_frame[self.positive_users_daily].sum()
            nt = Sprime/(ct*data_set.P*iprime)
            dates.append(end_day)
            nts.append(nt)
            iprimes.append(iprime)
            tested_people = win_frame[ItalianData.tested_people][-1] - \
                            win_frame[ItalianData.tested_people][0]
            i = win_frame[ItalianData.infected_daily].sum()
            S_bar = nt * self.M * data_set.P * i
            rho = S_bar/tested_people
            rhos.append(rho)
            for k in PPV_dict:
                PPV_dict[k].append(k/nt)
            daily_tests.append(int(tested_people/window))
            tests_per_person.append(S_bar/(window*self.R))

        nt = pd.Series(nts, dates, name='nt')
        ip = pd.Series(iprimes, dates, name='iprime')
        rf = pd.Series(rhos, dates, name='rho')
        ddf = pd.Series(daily_tests, dates, name='daily_tests')
        tppf = pd.Series(tests_per_person, dates,
                         name='daily_tests_per_person')
        self.dataset = self.dataset.join(nt)
        self.dataset = self.dataset.join(ip)
        self.dataset = self.dataset.join(rf)
        for k in PPV_dict:
            ppvf = pd.Series(PPV_dict[k], dates, name='PPV-'+str(k))
            self.dataset = self.dataset.join(ppvf)
        self.dataset = self.dataset.join(ddf)
        self.dataset = self.dataset.join(tppf)
        self.dataset['rescaled_warnings_weekly'] = \
            self.dataset['rescaled_warnings'].rolling(7).sum()
        self.dataset['positive_users_weekly'] = \
            self.dataset[self.positive_users_daily].rolling(7).sum()
        self.dataset['alpha_weekly'] = \
            self.dataset['rescaled_warnings_weekly']/self.dataset['positive_users_weekly']

    def export_table(self, cols=[], outfile=''):
        if not outfile:
            outfile = DataFetcher.data_folder + 'italian-data.csv'
        if not cols:
            cols = self.print_labels
        self.dataset[cols].to_csv(outfile)

# dowload or update data on the Covid pandemic from institutional sources
it = ItalianData()
it.update_data()
# 1.7  from the ministry
# 2.8  from N. Chintalapudi et al.
Rt_list = [1.7, 2.8]
immp = Immuni(Rt_list)
immp.update_data(national_data=it)
immp.compute_contacts_number()
immp.export_table()
