#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pandas as pd
from os import path as op
import shutil
import argparse

parser = argparse.ArgumentParser(
        prog='studyreport',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
DICOM Study Report
------------------
This is a tool to generate a study report based on DICOM files.
                                '''))
# Mandatory
parser.add_argument('studydir',
                    help='Path to study folder containing sorted dicom '
                         'folders',
                    type=str)
# Optional
parser.add_argument('-o', '--output',
                    help='Output location. '
                    'Default: same path as dwi.',
                    type=str)
parser.add_argument('-r' ,'--report',
                    action='store',
                    help='Generates a study report of DICOM files')
parser.add_argument('-c' ,'--convert',
                    action='store',
                    help='Converts DICOMs to NifTis')
parser.add_argument('-s' ,'--sort',
                    action='store',
                    help='Sorts DICOM files')

args = parser.parse_args()

