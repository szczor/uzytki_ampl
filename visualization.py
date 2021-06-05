import pandas as pd
import re
import seaborn as sns
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import configparser
from pathlib import Path


def parse_sol(nazwa):
    looking = 'Vschedule'
    i = 0
    lista1, lista2 = [], []
    with open(nazwa, newline='\n') as csvfile:
        for value in csvfile:
            if looking in value:
                lista1.append(value)
                i = 1

            if i == 1 and value.find(looking) == -1:
                lista2.append(value)
                i = 0
            else:
                continue
    return lista1, lista2


def parse_first_string(str):
    pat = r'.*?\[(.*)].*'
    match = re.search(pat, str)
    return match.group(1)


def parse_second_string(str):
    return re.search(r'\d+', str).group()


def create_lists(li):
    lista1, lista2, lista3 = [], [], []
    for str in li:
        str = str.split(',')
        lista1.append(str[0])
        lista2.append(str[1])
        lista3.append(str[2])
    return lista1, lista2, lista3


def chunk_based_on_size(lst, n):
    for x in range(0, len(lst), n):
        each_chunk = lst[x: n + x]

        if len(each_chunk) < n:
            each_chunk = each_chunk + [None for y in range(n - len(each_chunk))]
        yield each_chunk


def create_folder():
    if not os.path.exists('wykresy'):
        os.makedirs('wykresy')
    return 0


def import_df(name, index_col=None, header=None):
    df = pd.read_csv(name, header=header, index_col=index_col)
    df = df.astype(int)
    df = df.loc[:, (df != 0).any(axis=0)]
    return df


def check_companions(row, df, df_comp):
    nurse = row['nurses']
    companions = list(df_comp.loc[nurse])
    df_pom = df.loc[(df['days'] == row['days']) & (df['shift'] == row['shift'])]
    for comp in companions:
        if comp in set(df_pom['nurses']):
            return 1
        else:
            return 0

#########SOLVE THIS SHIT
def check_shifts(row, df_shift):
    nurse = row['nurses']
    pom_df=df_shift.reset_index()
    pom_df.columns=['nurses','days','shift']
    day, shift = row['days'], row['shift']
    pom_df=pom_df.loc[(pom_df['nurses']==nurse) & (pom_df['days'] ==day) & (pom_df['shift'] == shift)]
    if pom_df.empty:
        return 0
    return 1


def plot_workhours(df, name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    sns.barplot(x=df['nurses'], y=df['workhours_limit'], palette=['red'])
    sns.barplot(x=df['nurses'], y=df['work'], palette=['salmon'])
    locs, labels = plt.xticks()
    x_ticks = []
    for i in list(range(1, df['nurses'].max() + 1)):
        x_ticks.append('N' + str(i))
    plt.xticks(ticks=locs, labels=x_ticks)
    for index, row in df.iterrows():
        ax.text(index, row.workhours_limit + 2.5, round(row.workhours_limit), color='black', ha="center", fontsize=10)
    for index, row in df.iterrows():
        ax.text(index, row.work - 5, round(row.work), color='black', ha="center", fontsize=10)
    plt.title('Workhours for nurses')
    plt.tight_layout()
    fig.savefig(os.path.join(os.getcwd(), "wykresy", name + '.png'))


def plot_schedule(df_plot, name, plot, df_vacation=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if df_vacation is not None:
        sns.scatterplot(x='xaxis', y='nurses', data=df_vacation, marker=',',
                        color='y', s=350, ci=100, alpha=1, edgecolor='None')
    color_dict = dict({1: 'green',
                       0: 'black',
                       -1: 'red'})
    sns.scatterplot(x='xaxis', y='nurses', hue=plot, data=df_plot, marker=',',
                    color='r', s=350, ci=100, alpha=1, edgecolor='None', palette=color_dict)
    index_max = df_plot['xaxis'].max()
    index_min = df_plot['xaxis'].min()
    shift_names = ['S1', 'S2', 'S3'] * int((((index_max + 1) - index_min) / 3))
    for j in range(int(index_min), int(index_max)):
        plt.axvline(x=j + 1 / 2, color='grey')
    for j in range(int(index_min / 3), int(index_max / 3) + 1):
        plt.axvline(x=3 * j + 1 / 2, color='black', lw=4.5)
    positions = list(range(int(index_min), int(index_max))[1::3])
    positions = [x + 0.000001 for x in positions]
    labels = []
    for i in range(df_plot['days'].min(), df_plot['days'].max() + 1):
        labels.append('\n\nD' + str(i))
    plt.xticks(ticks=list(range(index_min, index_max + 1)) + positions, labels=shift_names + labels)
    ax.set_ylim([-1 / 2, df_plot['nurses'].max() + 1 / 2])
    yticks = []
    for i in list(range(1, df_plot['nurses'].max() + 2)):
        yticks.append('N' + str(i))
    plt.yticks(ticks=list(range(0, df_plot['nurses'].max() + 1)), labels=yticks)
    for j in range(df_plot['nurses'].min(), df_plot['nurses'].max()):
        plt.axhline(y=j + 1 / 2, color='black')
    ax.set_xlabel("")
    ax.get_legend().remove()
    plt.title('Nurse schedules')
    plt.tight_layout()
    fig.savefig(os.path.join(os.getcwd(), "wykresy", name + '.png'))


if __name__ == '__main__':
    # command line path for solution file
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path, help='Path for .sol file')
    parser.add_argument("data_folder", type=str, help='Output name')
    parser.add_argument("output_name", type=str, help='Output name')
    p = parser.parse_args()

    lista1, schedule = parse_sol(p.file_path)
    lista1 = list(map(parse_first_string, lista1))
    schedule = list(map(parse_second_string, schedule))
    nurses, days, shifts = create_lists(lista1)

    data_folder = p.data_folder
    config = configparser.ConfigParser()
    config.read(p.data_folder)

    data_frames = {}
    # translate config-relative paths
    rel_dir = os.path.dirname(p.data_folder)
    for file_key in config["Files"]:
        if not os.path.isabs(config["Files"][file_key]):
            config["Files"][file_key] = os.path.join(rel_dir, config["Files"][file_key])
    for csv in list(config["Files"]):
        try:
            if csv == 'vacation' or csv == 'workhourslimits':
                df = import_df(config["Files"][csv], index_col=None)
            else:
                df = import_df(config["Files"][csv], index_col=0)
        except:
            continue
        data_frames[csv] = df
    d = {'nurses': nurses, 'days': days, 'shift': shifts, 'schedule': schedule}

    df = pd.DataFrame(d)
    df = df.astype(int)
    df = df[df.schedule == 1]
    if df.empty:
        print('There is no solution')
        exit()
    ##COMPANIONS
    preferred_companions_schedule = []
    unpreferred_companions_schedule = []
    for index, row in df.iterrows():
        try:
            pc = check_companions(row, df, data_frames['likedcoworkers'])
            preferred_companions_schedule.append(pc)
        except:
            pass
        try:
            upc = check_companions(row, df, data_frames['dislikedcoworkers'])
            unpreferred_companions_schedule.append(upc * (-1))
        except:
            pass
    companions = []
    if (preferred_companions_schedule) and (unpreferred_companions_schedule):
        for (item1, item2) in zip(preferred_companions_schedule, unpreferred_companions_schedule):
            companions.append(item1 + item2)
        df['companions'] = companions
    elif preferred_companions_schedule:
        df['preferred_slots'] = preferred_companions_schedule
    elif unpreferred_companions_schedule:
        df['preferred_slots'] = unpreferred_companions_schedule
    ##SLOTS
    preferred_shifts_schedule = []
    unpreferred_shifts_schedule = []
    for index, row in df.iterrows():
        try:
            ps = check_shifts(row, data_frames['preferredshifts'])
            preferred_shifts_schedule.append(ps)
        except:
            pass
        try:
            ups = check_shifts(row, data_frames['nonpreferredshifts'])
            unpreferred_shifts_schedule.append(ups * (-1))
        except:
            pass
    preferred_slots = []
    if (preferred_shifts_schedule) and (unpreferred_shifts_schedule):
        for (item1, item2) in zip(preferred_shifts_schedule, unpreferred_shifts_schedule):
            preferred_slots.append(item1 + item2)
        df['preferred_slots'] = preferred_slots
    elif preferred_shifts_schedule:
        df['preferred_slots'] = preferred_shifts_schedule
    elif unpreferred_shifts_schedule:
        df['preferred_slots'] = unpreferred_shifts_schedule

    order = list(range(1, df['nurses'].max() + 1))
    df['nurses'] = [order.index(x) for x in df['nurses']]
    df['xaxis'] = (df.days - 1) * 3 + df['shift']

    # VACATION
    try:
        vacation = data_frames['vacation']
        vacation.columns = ['nurses', 'days']
        vacation = vacation.reindex(vacation.index.repeat(3))
        vacation['shift'] = vacation.groupby(level=0).cumcount() + 1
        vacation = vacation.reset_index(drop=True)
        order_vacation = list(range(1, vacation["nurses"].max() + 1))
        vacation['nurses'] = [order_vacation.index(x) for x in vacation['nurses']]
        vacation['xaxis'] = (vacation.days - 1) * 3 + vacation['shift']
    except:
        pass

    # WORKHOURS
    try:
        workhours = data_frames['workhourslimits']
        workhours.columns = ['nurses', 'workhours_limit']
        work = df.groupby(['nurses']).sum()['schedule'] * 8
        workhours['work'] = work
    except:
        pass

    days_max = df['days'].max()
    day_list = list(range(1, days_max + 1))

    # create a folder for plots
    create_folder()
    ## divide days into weeks
    weeks = list(chunk_based_on_size(day_list, 7))
    if companions and preferred_slots:
        visualisations = ['companions', 'preferred_slots']
    elif preferred_companions_schedule or unpreferred_companions_schedule:
        visualisations = ['companions']
    elif preferred_shifts_schedule or unpreferred_shifts_schedule:
        visualisations = ['preferred_slots']
    for plot in visualisations:
        i = 1
        for week in weeks:
            boolean_series = df.days.isin(week)
            df_week = df[boolean_series]
            vacation_week = None
            try:
                boolean_vacation = vacation.days.isin(week)
                vacation_week = vacation[boolean_vacation]
            except:
                pass
            plot_schedule(df_week, p.output_name + '_' + plot + '_week_' + str(i), plot, vacation_week)
            i += 1
    try:
        plot_workhours(workhours, p.output_name+'_'+'workhours')
    except:
        print('No workhours in csv')
