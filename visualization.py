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


def plot1(df, name):
    order = list(range(1, df["nurses"].max() + 1))
    df['nurses'] = [order.index(x) for x in df['nurses']]
    fig, ax = plt.subplots()
    plt.yticks(range(len(order)), order)
    sns.scatterplot(x='days', y='nurses', hue='shift', data=df)
    ax.xaxis.set_ticks(ticks=np.arange(df["days"].min(), df["days"].max() + 1), minor=1)
    plt.xticks(np.arange(df["days"].min(), df["days"].max() + 1))
    plt.setp(ax.get_xticklabels(), fontsize='x-small')
    plt.title('Nurse schedules')
    plt.legend(bbox_to_anchor=(1.05, 1), title='Shift')
    plt.tight_layout()
    if not os.path.exists('wykresy'):
        os.makedirs('wykresy')
    cwd = os.getcwd()
    fig.savefig(os.path.join(cwd, "wykresy", name + '.png'))


def plot2(df, name):
    order = list(range(1, df["nurses"].max() + 1))
    df['nurses'] = [order.index(x) for x in df['nurses']]
    df['xaxis'] = (df.days - 1) * 3 + df['shift']
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.yticks(range(len(order)), order)
    sns.scatterplot(x='xaxis', y='nurses', data=df, marker=',', color='r', s=1000)
    index_max = df['xaxis'].max()
    shift_names = ['S1', 'S2', 'S3'] * int((index_max / 3))
    for j in range(int(index_max)):
        plt.axvline(x=j + 1 / 2, color='grey')
    for j in range(int(index_max/3)):
        plt.axvline(x=3*j + 1 / 2, color='black',lw=4.5)
    positions = list(range(int(index_max))[1::3])
    positions = [x + 1 for x in positions]
    labels = []
    #Maybe will want to change fontsize of days?
    #fontsize=[10]*len(list(range(1, index_max + 1)))+[15]*len(positions)
    for i in range(1,df['days'].max() + 1):
        labels.append('\n\nD' + str(i))
    plt.xticks(ticks=list(range(1, index_max + 1))+positions, labels=shift_names+labels)
    ax.set_ylim([-1/2, df['nurses'].max()+1/2])
    yticks=[]
    for i in list(range(1,df['nurses'].max() + 2)):
        yticks.append('N' + str(i))
    ax.set_yticklabels(yticks)
    for j in range(df['nurses'].max()):
        plt.axhline(y=j + 1 / 2, color='black')
    ax.set_xlabel("")
    plt.title('Nurse schedules')
    plt.tight_layout()
    if not os.path.exists('wykresy'):
        os.makedirs('wykresy')
    cwd = os.getcwd()
    fig.savefig(os.path.join(cwd, "wykresy", name + '.png'))


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
    plot2(df, p.output_name)
