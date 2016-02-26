# test fit_seasons on actual data files
#
import os.path
import pandas as pd
from seasonal.application import read_csv # pylint:disable=import-error
from seasonal import fit_seasons # pylint:disable=import-error
from seasonal.sequences import sine # pylint:disable=import-error

def check_csv(csvpath, split=None):
    try:
        period = int(csvpath.split(".")[-2])
    except ValueError:
        period = None
    _, data, _ = read_csv(csvpath, split=split)
    seasons, trend = fit_seasons(data)
    assert seasons is None  or len(seasons) == period, \
        "expected period {}, got {}".format(
            period, len(seasons) if seasons else None)

def check_dir(datadir, split=None):
    files = os.listdir(datadir)
    for file in files:
        if file.endswith(".csv"):
            check_csv(os.path.join(datadir, file), split=split)

def test_misc():
    if pd:
        check_dir("data/misc")

def test_TSDL():
    if pd:
        check_dir("data/TSDL")

def test_NAB():
    if pd:
        check_dir("data/NAB", split=0.2)
