'''
Basic chart generation routines

Mike Widner <mikewidner@stanford.edu>
'''

import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


def timeseries(df, time, y, filename=None):
    p = sns.tsplot(data=df, time=time, value=y)
    plt.show()


def barplot(df, x, y, filename, xlabel = None, ylabel = None, title=None, show = False):
    p = sns.barplot(x=x, y=y, data=df, palette='Greys_r')
    if xlabel is not None:
        plt.xlabel(xlabel, fontname='Times New Roman')
    if ylabel is not None:
        plt.ylabel(ylabel, fontname='Times New Roman')
    if title is not None:
        plt.title(title, fontsize=20, fontname='Times New Roman')
    plt.xticks(rotation=-65, rotation_mode="anchor", ha="left", va="center")
    plt.tick_params(axis='both', which='major', labelsize=10)
    # plt.tick_params(axis='x', which='major', pad=10)
    plt.tight_layout()
    plt.savefig(filename, pad_inches=.1, dpi=600)
    if show:
        plt.show()

