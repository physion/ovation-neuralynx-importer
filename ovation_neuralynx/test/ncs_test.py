# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-
import datetime

import array
from nose.tools import istest, raises
from math import floor, ceil
from ovation_neuralynx.exceptions import ImportException
from ovation_neuralynx.ncs import calculate_start_index, calculate_end_index, CscBlock, CscData



@istest
def start_index_should_use_floor():
    assert(calculate_start_index(100, .011 * 1e6) == 1)

@istest
def end_index_should_use_ceil():
    assert(calculate_end_index(100, .011 * 1e6) == 2)

@istest
class CscData_spec(object):

    @istest
    def should_load_samples(self):
        srate = 32000
        header = { u'SamplingFrequency' : srate }
        def blocks():
            for i in xrange(10):
                start = i*512*1e6 # µs
                yield CscBlock(start, 0, srate, [x for x in xrange(512)])

        data = CscData(header, blocks())

        assert(len(data.samples(0)) == 10 * 512)

    @istest
    def should_calculate_sample_range(self):
        blocks, data = _csc_data_fixture()

        start_us = 100
        end_us = 1200
        start = int(floor(start_us/1e6 * data.sampling_rate_hz))
        end = int(ceil(end_us/1e6 * data.sampling_rate_hz))

        samples = array.array('f', [])
        for block in blocks():
            samples.extend(block.samples)

        expected = samples[start:end]
        assert(data.samples(start_us, end_us) == expected)

    @istest
    def should_calculate_samples_by_date_range(self):
        blocks, data = _csc_data_fixture()

        start = data.start + datetime.timedelta(microseconds=100)
        end = data.start + datetime.timedelta(microseconds=1200)
        start_idx = int(floor(100/1e6 * data.sampling_rate_hz))
        end_idx = int(ceil(1200/1e6 * data.sampling_rate_hz))

        samples = array.array('f', [])
        for block in blocks():
            samples.extend(block.samples)

        expected = samples[start_idx:end_idx]
        assert data.samples_by_date(start, end) == expected

    @istest
    @raises(ImportException)
    def should_raise_for_start_date_before_data_start(self):
        blocks,data = _csc_data_fixture()

        data.samples_by_date(data.start - datetime.timedelta(days=1))

    @istest
    @raises(ImportException)
    def should_raise_for_end_date_before_start(self):
        blocks,data = _csc_data_fixture()

        data.samples_by_date(data.start, data.start - datetime.timedelta(days=1))


    ## This is only generating a warning but is not raising an exception
    # @istest
    # @raises(ImportException)
    # def should_raise_for_end_date_after_end(self):
    #     blocks,data = _csc_data_fixture()
    # 
    #     data.samples_by_date(data.start, data.start + datetime.timedelta(days=1))


def _csc_data_fixture():
    srate = 32000.
    header = {
        u'SamplingFrequency': srate,
        u'Time Opened' : datetime.datetime.now()
    }

    def blocks():
        for i in xrange(10):
            start = i * 512 * 1e6 # µs
            yield CscBlock(start, 0, srate, [x * i for x in xrange(512)])

    data = CscData(header, blocks())
    return blocks, data
