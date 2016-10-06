'''
Basic chart generation routines

Mike Widner <mikewidner@stanford.edu>
'''

import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


def timeseries(df, time, y, filename):
    p = sns.tsplot(data=df, time=time, value=y)
    plt.show()


def barplot(df, x, y, filename, xlabel = None, ylabel = None, show = False):
    p = sns.barplot(x=x, y=y, data=df, palette='Greys_r')
    if xlabel is not None:
        p.set(xlabel=xlabel)
    if ylabel is not None:
        p.set(ylabel=ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(filename, pad_inches=.1, dpi=600)
    if show:
        plt.show()

