
import os
import argparse
import shutil
import subprocess
from pathlib import Path
import numpy as np
import pandas as pd

def _cli_parser():
    """Reads command line arguments and returns input specifications"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, metavar='dicom_dir',
                        help="The path to the directory which contains all "
                             "subjects' dicom images.")
    parser.add_argument('--ignore', nargs='+', type=str, metavar='ignored_dirs',
                        help="Subdirectories in `-d` to ignore.")
    parser.add_argument('-o', type=str, metavar='output_dir',
                        help="The path to the directory which contains all "
                             "subjects' BIDS data.")
    parser.add_argument('-s', type=str, metavar='session',
                        help="Session number.")
    parser.add_argument('-c', type=str.lower, metavar='config',
                        help='Configuration .json file for dcm2bids.')
    return parser.parse_args()


def _run_dcm2bids(sub_id, config, output_path, dicom_path, session=None):
    cmd_str = "dcm2bids -p {} -c {} -o {} -d '{}'".format(sub_id, config, output_path, dicom_path)
    if session is not None:
        cmd_str += " -s {}".format(session)
    print(cmd_str)
    subprocess.run(cmd_str, shell=True)


def main():

    params = vars(_cli_parser())
    print(params)
    sub_data = []
    sub_count = 1
    for dirname in os.listdir(params['d']):

        in_path = os.path.join(params['d'], dirname)
        if dirname in params['ignore']:
            print('Skipping {}'.format(in_path))
            continue
        else:
            print('Processing {}'.format(in_path))

        sub_id = 'sub-{}'.format(str(sub_count).zfill(2))
        sub_count += 1
        sub_data.append([sub_id, dirname])

        _run_dcm2bids(sub_id, params['c'], params['o'], in_path,
                      session=params['s'])

    sub_data = pd.DataFrame(np.array(sub_data),
                            columns=['participant_id', 'dicom_dir'])
    sub_data.to_csv(os.path.join(params['o'], 'participants.tsv'),
                    sep='\t')
    Path(os.path.join(params['o'], 'README')).touch()
    Path(os.path.join(params['o'], 'CHANGES')).touch()
    Path(os.path.join(params['o'], 'dataset_description.json')).touch()









