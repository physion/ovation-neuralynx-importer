# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

import jarray
from math import floor, ceil
from neuralynx.ncs import calculate_start_index, calculate_end_index, CscBlock, CscData

def test_start_index_should_use_floor():
    assert(calculate_start_index(100, .011 * 1e6) == 1)

def test_end_index_should_use_ceil():
    assert(calculate_end_index(100, .011 * 1e6) == 2)

def test_CscData_should_load_samples():
    srate = 32000
    header = { u'SamplingFrequency' : srate }
    def blocks():
        for i in xrange(10):
            start = i*512*1e6 # µs
            yield CscBlock(start, 0, srate, [x for x in xrange(512)])

    data = CscData(header, blocks())

    assert(len(data.samples(0)) == 10 * 512)

def test_CscData_should_calculate_sample_range():
    srate = 32000
    header = { u'SamplingFrequency' : srate }
    def blocks():
        for i in xrange(10):
            start = i*512*1e6 # µs
            yield CscBlock(start, 0, srate, [x*i for x in xrange(512)])

    data = CscData(header, blocks())

    start_us = 100
    end_us = 1200
    start = int(floor(start_us/1e6 * srate))
    end = int(ceil(end_us/1e6 * srate))

    samples = jarray.array([], 'f')
    for block in blocks():
        samples.extend(block.samples)

    expected = samples[start:end]
    assert(data.samples(start_us, end_us) == expected)
