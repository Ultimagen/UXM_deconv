#!/usr/bin/python3 -u

import os
import os.path as op
import argparse
import subprocess
import tempfile
from homog_mem import eprint, validate_file



def main():
    args = parse_args()
    atlas = args.atlas

    # validation
    validate_file(atlas)
    rscrip_path = op.join(op.abspath(op.dirname(__file__)), 'atlas_heatmap.R')
    validate_file(rscrip_path)

    # sort by target column and dump to a temp file
    tmp_name = next(tempfile._get_candidate_names())
    try:
        cmd = f'head -1 {atlas} > {tmp_name} && '
        cmd += f'tail +2 {atlas} | '
        if args.stubs:
            cmd += f' | grep "'
            cmd += '\\|'.join(args.stubs)
            cmd +'" | '
        cmd += f'sort -k6,6 >> {tmp_name}'
        subprocess.check_call(cmd, shell=True)

        cmd = f'Rscript {rscrip_path} {tmp_name} {args.outpath}'
        subprocess.check_call(cmd, shell=True)
        eprint(f'Dumped heatmap to: {args.outpath}')
    finally:
        if op.isfile(tmp_name):
            os.remove(tmp_name)
        if op.isfile('Rplots.pdf'):
            os.remove('Rplots.pdf')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('atlas', help='Atlas to plot. ' \
                        'Must be generated by uxm build,' \
                        ' or have similar format')
    parser.add_argument('outpath',
            help='Output path. should end with pdf or png.')
    parser.add_argument('--stubs', nargs='+',
            help='Show only reference cell types that match any of the stubs')
    return parser.parse_args()


if __name__ == '__main__':
    main()
