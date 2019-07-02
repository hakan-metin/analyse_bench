from constants import *

import pandas as pd
import numpy as np

INSTANCE_KEY = EDACC_INSTANCE
SOLVER_KEY   = EDACC_SOLVER_CONFIGURATION
RESULT_KEY   = EDACC_RESULT_CODE
TIME_KEY     = EDACC_WALL_TIME

def column_no_duplicate(df, column):
    assert(column in df.columns)
    return np.unique(df[column])


def guess_limit(df, key=TIME_KEY):
    limit = 0
    for instance in column_no_duplicate(df, INSTANCE_KEY):
        is_instance = df[INSTANCE_KEY] == instance

        is_sat     = df[RESULT_KEY] == SAT
        is_unsat   = df[RESULT_KEY] == UNSAT

        is_complete = (is_sat) | (is_unsat)

        if len(df[(is_instance) & (is_complete)].index) > 0:
            limit = max(limit, max(df[(is_instance) & (is_complete)][key]))
    return limit

def keep_only_solvers(df, solvers):
    for solver in solvers:
        assert(solver in column_no_duplicate(df, SOLVER_KEY))

    for solver in column_no_duplicate(df, SOLVER_KEY):
        is_solver = df[SOLVER_KEY] == solver
        if solver not in solvers:
            df.drop(df[is_solver].index, inplace=True)
    return df
