#! /usr/bin/python3

import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

import plotly.graph_objs as go
from plotly.offline import plot

from tabulate import tabulate
from constants import *
from utils     import *


def main():
    verbose = True

    parser = argparse.ArgumentParser(description='ranking EDACC CSV')
    parser.add_argument('filename_edacc_csv', metavar='<edacc_csv>',
                        help="File containing the benchmark")
    parser.add_argument('--interactive', dest='is_interactive',
                        action="store_true",
                        help='scatter plot interactive')

    parser.add_argument('--timeout', dest='timeout',
                        type=int,
                        help='timeout')

    parser.add_argument('-o', '--output', dest='output',
                        default="scatter.pdf",
                        help='output file of scatter plot')

    parser.add_argument('--title', dest='title',
                        default=None,
                        help='titleof scatter plot')

    parser.add_argument('--s1', dest='s1', metavar='<s1>',
                        help='first solver')
    parser.add_argument('--s2', dest='s2', metavar='<s2>',
                        help='second solver')


    args = parser.parse_args()

    filename_edacc_csv = args.filename_edacc_csv
    df = pd.read_csv(filename_edacc_csv)


    if not args.s1 or not args.s2:
        print("Need solvers names option --s1 and --s2")
        exit()

    solver_one = args.s1
    solver_two = args.s2


    limit = None
    if args.timeout:
        limit = args.timeout

    scatter_plot(df, solver_one, solver_two, limit=limit,
                 output=args.output, title=args.title)



def scatter_plot(df, s1, s2, output="scatter.pdf", limit=None, title=None,
                 key=TIME_KEY):
    df = df.copy()

    solvers = [s1, s2]
    keep_only_solvers(df, solvers)

    ax = None

    # Guess limit
    if limit == None:
        limit = guess_limit(df)

    is_fail = (df[RESULT_KEY] != SAT) & (df[RESULT_KEY] != UNSAT)
    df.loc[is_fail, key] = limit * 1.1

    table_sat   = []
    table_unsat = []

    for instance in column_no_duplicate(df, INSTANCE_KEY):
        is_instance = df[INSTANCE_KEY] == instance

        is_sat     = df[RESULT_KEY] == SAT
        is_unsat   = df[RESULT_KEY] == UNSAT

        is_s1      = df[SOLVER_KEY] == s1
        is_s2      = df[SOLVER_KEY] == s2

        val_s1 = df[(is_instance) & (is_s1)][key].item()
        val_s2 = df[(is_instance) & (is_s2)][key].item()

        if len(df[(is_instance) & (is_sat)].index) > 0:
            table_sat.append([instance, val_s1, val_s2])
        elif len(df[(is_instance) & (is_unsat)].index) > 0:
            table_unsat.append([instance, val_s1, val_s2])

    df_unsat = pd.DataFrame(table_unsat, columns=[INSTANCE_KEY, s1, s2])
    df_sat = pd.DataFrame(table_sat, columns=[INSTANCE_KEY, s1, s2])


    fig_unsat = go.Scatter(
        x=df_unsat[s1],
        y=df_unsat[s2],
        text=df_unsat[EDACC_INSTANCE],
        mode='markers',
        name="UNSAT",
        marker=dict(symbol="cross", color="red", size=10)
    )

    fig_sat = go.Scatter(
        x=df_sat[s1],
        y=df_sat[s2],
        text=df_sat[EDACC_INSTANCE],
        mode='markers',
        name="SAT",
        marker=dict(symbol="x", color="b", size=10)
    )

    linestyle = dict(color='black', dash='dash')
    border_a = go.Scatter(
        x=[0, limit * 1.05],
        y=[0, limit * 1.05],
        showlegend = False,
        hoverinfo="none",
        mode='lines',
        line = linestyle
    )
    border_b = go.Scatter(
        x=[0, limit * 1.15],
        y=[limit * 1.05, limit * 1.05],
        showlegend = False,
        hoverinfo="none",
        mode='lines',
        line = linestyle
    )
    border_c = go.Scatter(
        x=[limit * 1.05, limit * 1.05],
        y=[limit * 1.15, 0],
        showlegend=False,
        hoverinfo="none",
        mode='lines',
        line = linestyle
    )

    data = [fig_unsat, fig_sat, border_a, border_b, border_c]

    layout =  go.Layout(
        height=800,
        width=800,
        yaxis = dict(
            range=[0, limit*1.15],
            showgrid=True,
            zeroline=True,
            showline=True,
            gridcolor='#bdbdbd',
            gridwidth=2,
            zerolinecolor='#969696',
            zerolinewidth=4,
            linewidth=1,
 #           scaleanchor="x",
            scaleratio=1,
            title=s2,
        ),
        xaxis = dict(
            range=[0, limit*1.15],
            showgrid=True,
            zeroline=True,
            showline=True,
            gridcolor='#bdbdbd',
            gridwidth=2,
            zerolinecolor='#969696',
            zerolinewidth=4,
            linewidth=1,
#            scaleanchor="y",
            scaleratio=1,
            title=s1,
        )
    )
    fig = go.Figure(data=data, layout=layout)
    url = plot(fig, filename='plotly.html')
    print(url)


if __name__ == '__main__':
    main()
