#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path as op
import pandas as pd
import numpy as np
import pydicom as pyd
import glob
from tqdm import tqdm, trange
import multiprocessing
from joblib import Parallel, delayed

tqdmwidth = 70

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
    def __init__(self, studydir, nthreads=1):
        self.flist = np.array(glob.glob(op.join(studydir, '**/*'),
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

    def getstudyinfo(self):
        """
        Reads off varios DICOM header fields and returns a Pandas
        Dataframe on information discovered in a the class object
        self.dicomprops

        Parameters
        ----------
        (none)

        Returns
        -------
        self.dicomprops:    Pandas Dataframe
                            Contaions DICOM information per subject
        """
        inputs = trange(len(self.flist),
                        desc='Analyzing Files',
                        unit='files',
                        ncols=tqdmwidth)
        infolist = Parallel(self.workers, prefer='processes') \
            (delayed(self.getsubfield)(self.flist[i]) for i in inputs)
        # Nones appear in `infolist` where flist is not a DICOM file.
        # The following line gets rid of these rows so remaining files
        # are only dicoms
        infolist = [x for x in infolist if x is not None]
        self.dicomprops = pd.DataFrame(infolist,
                                      columns=['PatientID',
                                               'AcquisitionDate',
                                               'PatientSex',
                                               'PatientAge',
                                               'SoftwareVersion',
                                               'ProtocolName',
                                               'SequenceName'])

    def subtablehelper(self, subject, protolist):
        """
        This is a helper function to make class method createstudytable()
        compatible with joblib parallel processing. This function outputs
        a list containins sums of dicom files per protocol for a given
        subject.

        Parameters
        ----------
        subject:    string
                    SubjectID of subject to compute sums of
        protolist:  string list
                    list of protocols to query for sum

        Returns
        -------
        protosum:   int list
                    list containing sum of files in queried protocols
        """
        subchunk = self.dicomprops.loc[self.dicomprops.loc[:,
                                       'PatientID'] == subject, :]
        protosum = []
        protosum.append(subchunk.loc[:, 'AcquisitionDate'].iloc[0])
        protosum.append(subchunk.loc[:, 'PatientSex'].iloc[0])
        protosum.append(subchunk.loc[:, 'PatientAge'].iloc[0])
        protosum.append(subchunk.loc[:, 'SoftwareVersion'].iloc[0])
        for i, proto in enumerate(protolist):
            protosum.append(np.sum(
                subchunk.loc[:, 'ProtocolName'] == proto))
        return protosum

    def createstudytable(self):
        """
        Returns a condensed Pandas Dataframe from the master dataframe
        returned by class method getstudyinfo(). The condensed dataframe
        returned here containins sum of all files per protocol per subject

        Parameters
        ----------

        Returns
        -------
        studytable: Pandas Dataframe
                    Contains sum of all files in a protocol, per subject
        """
        sublist = np.sort(self.makeunique('PatientID'))
        protolist = np.sort(self.makeunique('ProtocolName'))[::-1]
        protolist = list(filter(None, protolist))
        inputs = trange(len(sublist),
                        desc='Creating Dataframe',
                        unit='sub',
                        ncols=tqdmwidth)
        studytable = Parallel(n_jobs=self.workers, prefer='processes') \
            (delayed(self.subtablehelper)(sublist[i], protolist) for i in
             inputs)
        newcols = ['AcquisitionDate', 'PatientSex',
                   'PatientAge',
                   'SoftwareVersion']
        newcols.extend(protolist)
        studytable = pd.DataFrame(studytable,
                                  index=sublist,
                                  columns=newcols)
        return studytable

    def writepdtable(self, pdtable, outdir):
        '''
        Writes a Pandas Dataframe onto disk as a CSV file. Include
        filename with .csv extension here.

        Parameters
        ----------
        pdtable:    Pandas Dataframe
                    Table to write
        outdir:     Path to write to
        '''
        if outdir is None:
            raise Exception('Please specify and output directory')
        ext = list(op.splitext(outdir))
        ext[1] = '.csv'
        outdir = ext[0] + ext[1]
        pdtable.to_csv(outdir)
        print('File saved to ' + outdir)

    def getsublist(self):
        '''
        Returns a list of all subjects discovered in a study

        Parameters
        ----------
        (none)

        Returns
        -------
        sublist:    list of strings
                    contains all subjects discovered
        '''
        sublist = pd.unique(self.dicomprops.loc[:, 'PatientID'])
        tqdm.write('Discovered '+ str(len(sublist)) + ' subjects')
        return sublist

    def makeunique(self, colidx=0):
        """
        Makes a numpy array unique based on an input column index

        Parameters
        ----------
        colidx: int or str
                column index according which to make unique. This is a
                Pandas column index, so use either an integer or string

        Returns
        -------
        uniquevec:  Numpy array of strings
                    Numpy array containing unique list
        """
        if not (isinstance(colidx, int) or  isinstance(colidx, str)):
            raise Exception('Column index is not a supported variable '
                            'type. Please use either an integer or '
                            'string and ensure it is a valid Pandas '
                            'dataframe index')

        if isinstance(colidx, int):
            if colidx < 0:
                raise Exception(
                    'Column index needs to be a positive integer')
            else:
                uniquevec = pd.unique(self.dicomprops.iloc[:, colidx])
        elif isinstance(colidx, str):
            uniquevec = pd.unique(self.dicomprops.loc[:, colidx])
        return uniquevec

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
        subinfo:    list of strings
                    List containing subject information
        """
        subinfo = []
        try:
            dcmfile = pyd.dcmread(dcmpath)
        except:
            return
        try:
            subinfo.append(dcmfile.PatientID)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.AcquisitionDate)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.PatientSex)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.PatientAge)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.SoftwareVersions)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.ProtocolName)
        except:
            subinfo.append('N/A')
        try:
            subinfo.append(dcmfile.SequenceName)
        except:
            subinfo.append('N/A')
        return subinfo

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