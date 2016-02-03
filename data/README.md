Timeseries Data
============

Each timeseries file consists of an index column and a value column in
CSV format. The index may be an ISO datetime, or simply an integer if
time information has been lost. Many sequences include level-shift
anomalies -- see their respective READMEs for a headsup. In our
testing with these sequences, the anomaly-free initial portion is
generally given to seasonal rather than the entire series (though
seasonal does well with many entire series, warts and all).

The sample periodicity is indicated in each filename before the .csv suffix.

Excerpts from specific online collections are filed in their own subdirectories,
with additional details in their README.md files.

`TSDL`

    A selection of timeseries from the Time Series Data Library
    (http://robjhyndman.com/TSDL/).

`NAB`

    A selection of pre-anomaly timeseries from the Numenta Anomaly Benchmark
    (https://github.com/numenta/NAB)

`misc`

    synthetic and classic timeseries.
