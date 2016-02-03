# -*- coding: utf-8 -*-
"""Sequences

generate periodic timeseries for testing

"""
import math
import numpy as np

def impulses(wid, period, cycles, partial=0):
    """create a train of n impulses, wid wide, one per period

    Parameters
    ----------
    wid : int
        impulse width (samples)
    period : int
        impulse period (samples)
    cycles : int
        number of cycles to generate
    partial : int
        additional samples to append

    Returns
    -------
    ndarray

    """

    seq = np.tile(np.concatenate((np.ones(wid), np.zeros(period - wid))), cycles)
    seq = np.concatenate((seq, seq[:partial]))
    return  seq

def square(amp, duty, period, cycles, partial=0):
    """create a square wave of given duty cycle"""
    return amp * impulses(int(duty * period), period, cycles, partial)

def staggered(delta, wid, period, cycles, partial=0):
    """create periodic impulses whose starts shift forward and backward by
    delta

    Parameters
    ----------
    delta : int
        periodic shift (samples)
    wid : int
        impulse width (samples)
    period : int
        impulse period (samples)
    cycles : int
        number of cycles to generate
    partial : int
        additional samples to append

    Returns
    -------
    ndarray

    """
    seq = impulses(wid, 2 * period, (cycles + 1) / 2)
    seq = np.concatenate((seq, np.roll(seq, period + delta)))
    seq = np.concatenate((seq, seq[:partial]))
    return  seq

def sawtooth(amp, period, cycles, partial=0):
    """triangle wave

    Parameters
    ----------
    amp : float
        values range from 0..amp
    period : int
        sawtooth period (samples)
    cycles : int
        number of cycles to generate
    partial : int
        additional samples to append

    Returns
    -------
        ndarray

    """
    tooth = np.concatenate((np.arange(0, amp, amp / np.floor(period / 2.0)),
                            np.arange(amp, 0, -amp / np.ceil(period / 2.0))))
    seq = np.tile(tooth, cycles)
    seq = np.concatenate((seq, seq[:partial]))
    return  seq

def sine(amp, period, cycles, partial=0):
    """sine wave

    Parameters
    ----------
    amp : float
        values range from -amp..amp
    period : int
        sine period (samples)
    cycles : int
        number of cycles to generate
    partial : int
        additional samples to append

    Returns
    -------
    ndarray

    """
    cycle = [math.sin(i * 2 * math.pi / period) for i in range(period)]
    seq = np.array(cycle * cycles) * amp
    seq = np.concatenate((seq, seq[:partial]))
    return  seq

def add_noise(seq, scale):
    """return seq + a 0-centered normal noise vector.

    Parameters
    ----------
    seq : ndarray
        base sequence
    scale : float
        stdev of noise

    Returns
    -------
    ndarray

    """
    if scale == 0:
        return seq
    else:
        return seq + np.random.normal(0, scale, len(seq))

def mix(seq, val, prob):
    """randomly mix a value or values into a sequence according to prob"""
    if np.isscalar(val):
        val = np.ones(len(seq)) * val
    return np.where(np.random.random(len(seq)) <= prob, val, seq)

def brownian(scale, samples):
    """brownian motion

    Parameters
    ----------
    scale : float
        stdev of noise
    samples : int
        number of samples to generate

    Returns
    -------
        ndarray

    """
    return np.random.normal(0, scale, samples).cumsum()

def aperiodic(amp, samples):
    """an aperiodic oscillating signal

    Parameters
    ----------
    amp : float
        values range over +-amp
    samples : int
        number of samples to generate

    Returns
    -------
    ndarray

    """
    periods = np.abs(sine(samples, samples, 1)) + samples / 10
    seq = [amp * math.sin(i * 2 * math.pi / periods[i]) for i in range(samples)]
    return np.array(seq)
