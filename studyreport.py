#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import textwrap
import os.path as op
from dcmreport import studyreport as sr

parser = argparse.ArgumentParser(
        prog='studyreport',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
DICOM Study Report
------------------
This is a heuristic tool to generate a study report based on DICOM files in
a study directory. A recursive search is performed on all dicom files 
in a folder and analyzed for important information, which is then condensed
into a Pandas Datafram and output as a .csv file.
                                '''))
# Mandatory
parser.add_argument('input',
                    help='Path to study folder containing sorted dicom '
                         'folders',
                    type=str)

parser.add_argument('output',
                    help='Output location. '
                    'Default: same path as dwi.',
                    type=str)
# Optional
parser.add_argument('-r' , '--report',
                    action='store',
                    help='Generates a study report of DICOM files')
parser.add_argument('-c' , '--convert',
                    action='store',
                    help='Converts DICOMs to NifTis (Work in Progress')
parser.add_argument('-n', '--nthreads',
                    action='store',
                    help='Number of workers to process with. Default: 1')
args = parser.parse_args()

# Perform Checks
if not op.exists(args.input):
    raise Exception('Study directory does not exist. Please ensure that '
                    'the directory provided exists')
if not args.output:
    raise Exception('Please provide an output filename (.csv) or '
                    'directory')
if not args.nthreads:
    args.nthreads = 1
else:
    args.nthreads=int(args.nthreads)

# Run Script
study = sr(args.input,
           nthreads=args.nthreads)
study.getstudyinfo()
table = study.createstudytable()
study.writepdtable(table, args.output)