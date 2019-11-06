#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import path as op
import pandas as pd
import numpy as np
import pydicom as pyd
import shutil
import argparse
import glob
from tqdm import tqdm, trange
import multiprocessing
from joblib import Parallel, delayed

class studyreport():
    """
    The study report class object computes and holds important study
    metrics for a dicom-based study. It serves as a means to estimate
    study health based on a dicom headers.

    Parameters
    ----------
    studydir:   str
                path to study directory containing dicom files

    Methods
    -------
    getsubid:       Returns patient ID from the 'PatientName' field of a
                    DICOM header

    get sublist:
    """
    def __init__(studydir, outdir, nthreads=-1):
        self.flist = np.array(glob.glob(op.join(args.studydir, '**/*.dcm'),
                           recursive=True))
        if not isinstance(nthreads, int):
            raise Exception('Variable nthreads need to be an integer')
        if nthreads < -1 or nthreads == 0:
            raise Exception('Variable nthreads is a positive integer or '
                            '-1')
        if nthreads is None:
            self.workers = -1
        else:
            self.workers = nthreads
        if self.workers == -1:
            tqdm.write('Processing with ' +
                       np.str(multiprocessing.cpu_count()) +
                       ' workers...')
        else:
            tqdm.write('Processing with ' +
                       np.str(self.workers) +
                       ' workers...')

    @property
    def getstudyinfo(self):
        inputs = trange(len(self.flist),
                        desc='Analyzing Files',
                        unit='files')
        self.dicoprops = Parallel(n_jobs=8, prefer='processes') \
            (delayed(getsubfield)(self.flist[i]) for i in inputs)
        self.dicoprops = pd.DataFrame(self.dicoprops,
                                      columns=['PatientID',
                                               'AcquisitionDate',
                                               'PatientSex',
                                               'PatientAge',
                                               'SoftwareVersion',
                                               'ProtocolName',
                                               'SequenceName'])

    @function
    def getsublist(self):
        sublist = pd.unique(self.dicomprops.loc[:, 'PatientID'])
        tqdm.write('Discovered '+ str(len(sublist)) + ' subjects')
        return sublist



    @function
    def makeunique(self, inlist, colidx=0):
        """
        Makes a numpy array unique based on an input column index

        Parameters
        ----------
        inlist: input numpy array
        colidx: column index according which to make unique

        Returns
        -------
        Numpy array containing unique list
        """
        if inlist=None:
            raise Exception('Input list or numpy array cannot be '
                            'Nonetype. Please enter a valid list or array')
        inlist = np.array(inlist)
        master = inlist[:, colidx]
        umaster, idx = np.unique(master, return_index=True)


    @function
    def getsubfield(self, dcmpath):
        """
        Returns a numpy array containing essential information for an
        input dicom file

        Parameters
        ----------
        dcmpath:    string
            path to dicom file (.dcm)

        Returns
        -------
        List containing subject information
        """
        subinfo = []
        dcmfile = pyd.dcmread(dcmpath)
        subinfo.append(dcmfile.PatientID)
        try:
            subinfo.append(dcmfile.AcquisitionDate)
        except:
            subinfo.append('N/A')
        subinfo.append(dcmfile.PatientSex)
        subinfo.append(dcmfile.PatientAge)
        subinfo.append(dcmfile.SoftwareVersions)
        subinfo.append(dcmfile.ProtocolName)
        try:
            subinfo.append(dcmfile.SequenceName)
        except:
            subinfo.append('N/A')
        return subinfo

    @function
    def getsubid(self, dcmpath):
        """
        Returns patient ID from the 'PatientID' field of a DICOM header

        Parameters
        ----------
        dcmpath:    string
            path to dicom file (.dcm)

        Returns
        -------
        Patient ID in string
        """
        dcmfile = pyd.dcmread(dcmpath)
        return dcmfile.PatientID


