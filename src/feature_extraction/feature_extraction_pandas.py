import sys
from functools import reduce

import pandas as pd
import argparse
import os
import torch
import re
import numpy as np

raw_data_path = "../../data/raw"
features_path = "../../data/features.csv"
labels_path = "../../data/labels.csv"
normalized_path = "../../data/normalized.csv"

feature_cols = {'date': str, 'serial_number': str,
                'smart_197_raw': 'float', 'smart_9_raw': 'float', 'smart_241_raw': 'float', 'smart_187_raw': 'float',
                'failure': 'bool'}

def filter_columns_and_write_back():
    for i, read_filename in enumerate(os.listdir(raw_data_path)):
        print(f"Parsing file {i} out of {len(os.listdir(raw_data_path))}")
        read_filepath = os.path.join(raw_data_path, read_filename)
        df = pd.read_csv(read_filepath)
        features = df[feature_cols.keys()].astype(feature_cols)
        header = not os.path.isfile(features_path)
        features.to_csv(features_path, mode='a', index=None, header=header)

def add_failure_columns_to_df_with_one_serial_number(df, num_look_ahead_days):
    entry_count = len(df)

    if df.failure.any():
        df.sort_values('date', inplace=True)
        df.drop(columns=['failure'], inplace=True)
        ones = np.ones((entry_count, num_look_ahead_days))
        float_triangle = np.fliplr(np.tril(ones, num_look_ahead_days - entry_count))
        bool_values = float_triangle != 0
    else:
        bool_values = np.zeros((entry_count, num_look_ahead_days)) != 0

    col_names = [f"fails_within_{i}_days" for i in range(1, num_look_ahead_days + 1)]
    failure_features = pd.DataFrame(data=bool_values, columns=col_names)

    return pd.concat([df, failure_features], axis=1)

def normalization_and_additional_failure_columns():
    features = pd.read_csv('../../data/features_test.csv', parse_dates=['date'])
    print('CSV read finished')

    smart_col_names = ['smart_197_raw', 'smart_9_raw', 'smart_241_raw', 'smart_187_raw']
    smart_means = features[smart_col_names].mean(axis=0)
    smart_stddevs = features[smart_col_names].std(axis=0)

    #replace nan values with column means
    features.fillna(smart_means, inplace=True)

    #normalize to standard normal distribution
    features[smart_col_names] = (features[smart_col_names] - smart_means) / smart_stddevs

    print('Normalization finished')

    #add failure columns
    num_look_ahead_days = 5
    grouped_by_serial_number = features.groupby('serial_number')

    features_with_failure_columns = grouped_by_serial_number.apply(
        lambda df: add_failure_columns_to_df_with_one_serial_number(df, num_look_ahead_days))

    features_with_failure_columns.to_csv(normalized_path, index=None)
    print('Final features file written')

if __name__ == "__main__":
    #filter_columns_and_write_back()
    normalization_and_additional_failure_columns()