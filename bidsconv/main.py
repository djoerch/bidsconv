
import os
import argparse
import shutil
import subprocess
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import natsort

def _cli_parser():
    """Reads command line arguments and returns input specifications"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, metavar='dicom_dir',
                        help="The path to the directory which contains all "
                             "subjects' dicom images.")
    parser.add_argument('-o', type=str, metavar='output_dir',
                        help="The path to the directory which contains all "
                             "subjects' BIDS data.")
    parser.add_argument('--ignore', nargs='+', type=str, metavar='ignored_dirs',
                        help="Subdirectories in `-d` to ignore.")
    parser.add_argument('-s', type=str, metavar='session',
                        help="Session number, e.g., 'ses-01'")
    parser.add_argument('-c', type=str.lower, metavar='config',
                        help='Configuration .json file for dcm2bids. Refer to '
                             'dcm2bids documentation for examples.')
    parser.add_argument('--force-run-labels', action='store_true', 
                        help='Force all functional runs to have a run number. '
                             'This means that singleton runs, i.e. tasks that '
                             'have only one functional run will be labeled '
                             'as `run-01`. This is a necessary workaround for '
                             'fmriprep 1.4.0 or greater. Otherwise, singleton '
                             'runs will not have a run number/label, which is '
                             'the default for dcm2bids.')
    parser.add_argument('-m', type=str.lower, metavar='mapping',
                        help='.json file containing specific mappings between '
                             'input dicom folders (keys) and subject IDs (values). '
                             'Useful for multi-session data in which different '
                             'dicom folders belong to the same subject.')
    return parser.parse_args()


def _run_dcm2bids(sub_id, config, output_path, dicom_path, session=None):
    cmd_str = "dcm2bids -p {} -c {} -o {} -d '{}'".format(sub_id, config,
                                                          output_path, dicom_path)
    if session is not None:
        cmd_str += " -s {}".format(session)
    print(cmd_str)
    subprocess.run(cmd_str, shell=True)


def _label_runs(path):
    """Provide a run label for singleton runs

    dcm2bids only gives run label if more than one detected per task. Identify
    files without run labels, which means that they are singletons, and give
    these files a run-01 label.

    This is a necessary workaround for fmriprep 1.4.0-1.4.1, which fails to
    generate report figures for files without a run label if at a run label is
    found in at least one file.
    See: https://neurostars.org/t/missing-runs-from-reports/4758

    Parameters
    ----------
    path : str
        Path to subject/session bids output
    """

    if not os.listdir(path):
        raise ValueError('No files found in path')

    if not [i.endswith('bold.nii.gz') for i in os.listdir(path)]:
        raise Exception('No functional BOLD files found in dir')

    for i in os.listdir(path):
        if '_run-' not in i:
            fname = i.split('_')
            fname.insert(-1, 'run-01')
            labeled_fname = '_'.join(fname)
            src_file = os.path.join(path, i)
            dst_file = os.path.join(path, labeled_fname)
            os.rename(src_file, dst_file)
            # print(src_file, dst_file)
            print("(!) : {} => Run label added".format(i))


def main():

    params = vars(_cli_parser())
    print(params)
    sub_data = []
    sub_count = 1

    if params['m'] is not None:
        with open(params['m'], 'rb') as f:
            sub_map = json.load(f)

    directories = natsort.natsorted(os.listdir(params['d']))
    for dirname in directories:
        in_path = os.path.join(params['d'], dirname)
        if params['ignore'] is not None:
            if dirname in params['ignore']:
                print('Skipping {}'.format(in_path))
                continue
        else:
            print('Processing {}'.format(in_path))

        if params['m'] is None:
            sub_id = 'sub-{}'.format(str(sub_count).zfill(2))
        else:
            sub_id = str(sub_map[dirname]).zfill(2)
        sub_count += 1
        sub_data.append([sub_id, dirname])

        _run_dcm2bids(sub_id, params['c'], params['o'], in_path,
                      session=params['s'])

        if params['force_run_labels']:

            if not sub_id.startswith('sub-'):
                sub_dir = 'sub-' + sub_id
            else:
                sub_dir = sub_id

            if params['s'] is not None:
                func_path = os.path.join(params['o'], sub_dir, params['s'], 'func')
            else:
                func_path = os.path.join(params['o'], sub_dir, 'func')

            if os.path.isdir(func_path):
                _label_runs(func_path)

    sub_data = pd.DataFrame(np.array(sub_data),
                            columns=['participant_id', 'dicom_dir'])

    participants_file = os.path.join(params['o'], 'participants.tsv')
    if os.path.isfile(participants_file):
        # check if this multi-session data
        if (params['s'] is not None) & (params['m'] is not None):
            print('Existing participants.tsv found; dicom directories will be '
                  'merged in file according to {}. You will need to adjust '
                  'the column names to reflect the multiple '
                  'sessions'.format(params['m']))
            participants = pd.read_table(participants_file)
            sub_data = participants.merge(sub_data, on='participant_id')
        else:
            # avoid overwriting if this is a re-run
            warnings.warn('participants.tsv already detected, which is likely '
                          'due to running bidsconv multiple times for the same '
                          'output directory. No session label and and ' 
                          'participant mapping were provided. A '
                          '`participants_1.tsv` file has been created to '
                          'prevent the original from being overwritten. Only '
                          'one participants file can exist so you will have to '
                          'adjust things accordingly.', Warning)
            participants_file = os.path.join(params['o'], 'participants_1.tsv')
    
    sub_data.to_csv(participants_file, sep='\t')

    os.makedirs(os.path.join(params['o'], 'derivatives'), exist_ok=True)
    Path(os.path.join(params['o'], 'README')).touch()
    Path(os.path.join(params['o'], 'CHANGES')).touch()
    Path(os.path.join(params['o'], '.bidsignore')).touch()
    Path(os.path.join(params['o'], 'dataset_description.json')).touch()
