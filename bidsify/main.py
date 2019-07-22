
import os
import argparse
import shutil
import subprocess
import numpy as np
import pandas as pd

def _cli_parser():
    """Reads command line arguments and returns input specifications"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, metavar='dicom_dir',
                        help="The path to the directory which contains all "
                             "subjects' dicom images.")
    parser.add_argument('--ignore', type='+', metavar='ignored_dirs',
                        help="Subdirectories in `-d` to ignore.")
    parser.add_argument('-o', type=str, metavar='output_dir',
                        help="The path to the directory which contains all "
                             "subjects' BIDS data.")
    parser.add_argument('-s', type=str, metavar='session',
                        help="Session number.")
    parser.add_argument('-c', '--config', type=str.lower, metavar='config',
                        help='Configuration .json file for dcm2bids.')
    return parser.parse_args()


def _run_dcm2bids(sub_id, config, output_path, dicom_path, session=None):
    cmd_str = "dcm2bids -p {} -c {} -o {} -d '{}'"
    cmd_str.format(sub_id, config, output_path, dicom_path)
    if session is not None:
        cmd_str += " -s {}".format(session)
    print(cmd_str)
    subprocess.run(cmd_str, shell=True)


def main():

    params = vars(_cli_parser())
    sub_data = []
    for i, dirname in os.listdir(params['dicom_dir']):

        in_path = os.path.join(params['dicom_dir'], dirname)
        if dirname in params['ignored_dirs']:
            print('Skipping {}'.format(in_path))
            continue
        else:
            print('Processing {}'.format(in_path))

        sub_id = 'sub-0{}'.format(i + 1)
        output_path = os.path.join(params['output_dir'], sub_id)
        sub_data.append([sub_id, dirname])

        _run_dcm2bids(sub_id, params['config'], output_path, in_path,
                      session=params['session'])

    sub_data = pd.DataFrame(np.array(sub_data),
                            columns=['participant_id', 'dicom_dir'])
    sub_data.to_csv(os.path.join(params['output_dir'], 'participants.tsv'),
                    sep=r'\t')









