import pandas as pd
import re
import seaborn as sns
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path


def parse_sol(nazwa):
    looking = 'schedule'
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
def plot_workhours(df, name):
    pass


def plot_schedule(df_plot, name):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    sns.scatterplot(x='xaxis', y='nurses', data=df_plot, marker=',', color='r', s=350,ci=100,alpha=1, edgecolor='None')
    index_max = df_plot['xaxis'].max()
    index_min = df_plot['xaxis'].min()
    shift_names = ['S1', 'S2', 'S3'] * int((((index_max+1)-index_min) / 3))
    for j in range(int(index_min),int(index_max)):
        plt.axvline(x=j + 1 / 2, color='grey')
    for j in range(int(index_min/3),int(index_max / 3)+1):
        plt.axvline(x=3 * j + 1 / 2, color='black', lw=4.5)
    positions = list(range(int(index_min), int(index_max))[1::3])
    positions = [x for x in positions]
    labels = []
    # Maybe will want to change fontsize of days?
    # fontsize=[10]*len(list(range(1, index_max + 1)))+[15]*len(positions)
    for i in range(df_plot['days'].min(), df_plot['days'].max() + 1):
        labels.append('\n\nD' + str(i))
    plt.xticks(ticks=list(range(index_min, index_max + 1)) + positions, labels=shift_names + labels)
    ax.set_ylim([-1 / 2, df_plot['nurses'].max() + 1 / 2])
    yticks = []
    for i in list(range(1, df_plot['nurses'].max()+2)):
        yticks.append('N' + str(i))
    plt.yticks(ticks=list(range(0,df_plot['nurses'].max()+1)),labels=yticks)
    for j in range(df_plot['nurses'].min(), df_plot['nurses'].max()):
        plt.axhline(y=j + 1 / 2, color='black')
    ax.set_xlabel("")
    plt.title('Nurse schedules')
    plt.tight_layout()
    fig.savefig(os.path.join(os.getcwd(), "wykresy", name + '.png'))


if __name__ == '__main__':
    # command line path for solution file
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path, help='Path for .sol file')
    parser.add_argument("output_name", type=str, help='Output name')
    p = parser.parse_args()

    lista1, schedule = parse_sol(p.file_path)
    lista1 = list(map(parse_first_string, lista1))
    schedule = list(map(parse_second_string, schedule))
    nurses, days, shifts = create_lists(lista1)
    d = {'nurses': nurses, 'days': days, 'shift': shifts, 'schedule': schedule}

    df = pd.DataFrame(d)
    df = df.astype(int)
    df = df[df.schedule == 1]
    order = list(range(1, df["nurses"].max() + 1))
    df['nurses'] = [order.index(x) for x in df['nurses']]
    df['xaxis'] = (df.days - 1) * 3 + df['shift']
    if df.empty:
        print('There is no solution')
        exit()
    days_max = df['days'].max()
    day_list = list(range(1, days_max + 1))
    #create a folder for plots
    create_folder()
    ## divide into weeks
    weeks = list(chunk_based_on_size(day_list, 7))
    i = 1
    for week in weeks:
        boolean_series = df.days.isin(week)
        df_week = df[boolean_series]
        if df_week.empty:
            exit()
        plot_schedule(df_week, p.output_name + '_week_' + str(i))
        i += 1
