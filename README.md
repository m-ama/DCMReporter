# DCMReporter 
DCMReporter is a Python-based CLI aimed at testing the integrity of DICOM scans. The output of this tool can be used to analyze
consistency of the number of files per protocol, per subject, in an entire study.

_Disclaimer:_
```
DCMReporter only works with DICOM files. This tool with ignore DICOM files compressed into another
folder such as .zip, .gz or .tar. Please ensure that contents of your DICOM study are completely 
decompressed prior to running DCMReporter.
```

## Dependencies
DCMReporter, being purely Python, depends on `numpy`, `pandas`, `joblib`, `multiprocessing`, and `pydicom`.

For Conda installation of dependencies, run:

```
conda install -c anaconda numpy pandas joblib
conda install -c conda-forge tqdm  multiprocess pydicom
```

For PiPy installation, run:
```
pip install numpy, pandas, joblib, multiprocess, tqdm, pydicom
```

## Usage
DCMReporter is fairly easy to use, with the following run context
```
python dcmreporter.py [options] input output
```

In it's current form, only the `--nthreads` flag works. All other flags are either a work-in-progrees, or intended for integration
with other tools.