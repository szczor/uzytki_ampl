import pandas as pd
import re
import seaborn as sns
import os
import matplotlib.pyplot as plt
import numpy as np


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


def plot(df, name):
    order = list(range(1, df["nurses"].max()+1))
    df['nurses'] = [order.index(x) for x in df['nurses']]
    fig, ax = plt.subplots()
    plt.yticks(range(len(order)), order)
    sns.scatterplot(x='days', y='nurses', hue='shift', data=df)
    ax.xaxis.set_ticks(np.arange(df["days"].min(), df["days"].max()+1), 1)
    plt.xticks(np.arange(df["days"].min(), df["days"].max()+1))
    plt.setp(ax.get_xticklabels(), fontsize='x-small')
    plt.title('Nurse schedules')
    plt.legend(bbox_to_anchor=(1.05, 1),title='Shift')
    plt.tight_layout()
    if not os.path.exists('wykresy'):
        os.makedirs('wykresy')
    cwd = os.getcwd()
    fig.savefig(os.path.join(cwd, "wykresy", name + '.png'))


if __name__ == '__main__':
    lista1, schedule = parse_sol('uzytki.sol')
    lista1 = list(map(parse_first_string, lista1))
    schedule = list(map(parse_second_string, schedule))
    nurses, days, shifts = create_lists(lista1)
    d = {'nurses': nurses, 'days': days, 'shift': shifts, 'schedule': schedule}
    df = pd.DataFrame(d)
    df = df.astype(int)
    df = df[df.schedule == 1]
    plot(df, 'output')
