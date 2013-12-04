# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import jarray
import binary_reader

from math import floor, ceil
from datetime import timedelta
from ovneuralynx.exceptions import ImportException


def total_microseconds(td):
    """Calculates the total microseconds in the given datetime.timedelta.

    Parameters:
        td      datetime.timedelta

    Returns:
        total microseconds
    """

    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6)

class CscData(object):

    def __init__(self, header, blocks):
        self.header = header
        self.blocks = blocks
        self.sampling_rate_hz = self.header[u'SamplingFrequency']

        self._samples_array = None
        self._loaded = False


    def _load(self):
        if not self._loaded:
            self._samples_array = _collect_samples(self.sampling_rate_hz, self.blocks)
            self._loaded = True

    @property
    def start(self):
        return self.header[u'Time Opened']

    @property
    def end(self):
        if not self._loaded:
            self._load()

        return self.start + timedelta(seconds=len(self._samples_array)/self.sampling_rate_hz)

    def samples_by_date(self, start_date, end_date=None):
        dt = timedelta(seconds=1./self.sampling_rate_hz)
        if start_date < self.start and start_date - self.start > dt:
            raise ImportException("Start date before data start")

        if end_date is not None and end_date < start_date:
            raise ImportException("End date before start date")

        if end_date is not None and end_date > self.end:
            logging.warning("End date after data end")
            end_date = self.end

        start_td = start_date - self.start

        end_td = None if end_date is None else end_date - self.start

        return self.samples(total_microseconds(start_td),
            total_microseconds(end_td) if end_td is not None else None)


    def samples(self, start_us, end_us=None):
        """Returns samples in the given time region.

        If no end time is specified, returns to end of samples.

        Parameters:
            start_us    start time in µs from data start
            end_us      end time in µs from data start. If None, end of data

        Returns:
            Tuple <header, CSC data samples (in µV) for given time range>
        """

        if not self._loaded:
            self._load()

        start_index = calculate_start_index(self.sampling_rate_hz, start_us)
        if end_us is None:
            return self._samples_array[start_index:]

        end_index = calculate_end_index(self.sampling_rate_hz, end_us)

        return self._samples_array[start_index:end_index]


def calculate_start_index(srate_hz, time_us):
    return _calculate_index(srate_hz, time_us, floor)

def calculate_end_index(srate_hz, time_us):
    return _calculate_index(srate_hz, time_us, ceil)

def _calculate_index(srate_hz, time_us, round_fn):
    return int(round_fn(time_us * 1e-6 * srate_hz))

def _collect_samples(sampling_rate_hz, blocks):
    samples = jarray.array([], 'f')
    n = 0
    for block in blocks:
        n += 1
        if n % 10000 == 0:
            logging.debug('Collecting block %d...' % n)

        if block.sample_freq_hz != sampling_rate_hz:
            raise ImportException("Block sampling rate (%f Hz) not equal to channel sampling rate (%f Hz)" % (block.sample_freq_hz, sampling_rate_hz))

        samples.extend(block.samples)

    return samples


class CscBlock(object):
    """Represents a single continuously sampled block.

    Records start time (datetime), channel number, sampling rate (Hz), and samples (in µV)

    """

    def __init__(self, start, channel_number, sample_freq_hz, samples):
        self.start = start
        self.channel_number = channel_number
        self.sample_freq_hz = sample_freq_hz
        self.samples = samples # in µV


def ncs_blocks(reader, header):
    """Returns a generator for CSC blocks from the given reader.

    Parameters:
    reader -- binary.BinaryReader
    header -- dict of header (via header.parse_header)

    """

    start_time = header[u'Time Opened']
    try:
        while(True):
            time_stamp = reader.read('uint64')
            dt = timedelta(microseconds=time_stamp)
            start = start_time + dt
            channel_number = reader.read('uint32')
            sample_freq_hz = reader.read('uint32')
            num_samples = reader.read('uint32')
            samples = [s * header[u'ADBitVolts'] * 1e6 for s in reader.read_array('int16', num_samples)]

            yield CscBlock(start, channel_number, sample_freq_hz, samples)
    except binary_reader.BinaryReaderEOFException:
        return

