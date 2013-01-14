# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

__author__ = 'barry'

from datetime import datetime, timedelta
from neuralynx.nev import EpochBoundaries, Event
from nose.tools import istest, eq_

@istest
class EpochBoundaries_spec(object):

    @istest
    def should_order_starts_without_interepochs(self):
        header = {
            u'Time Opened' : datetime.now()
        }

        start_id = 1
        end_id = 2
        start = header[u'Time Opened']
        def events():
            for i in xrange(3):
                yield Event(start + timedelta(microseconds=(i * 103)),
                    0, start_id, 0, 0, 0, "")
                yield Event(start + timedelta(microseconds=(i * 103 + 95)),
                    0, end_id, 0, 0, 0, "")

        eb = EpochBoundaries(header, events(), start_id, end_id, False)


        eq_(len(list(eb.boundaries)), 3)

        for b in eb.boundaries:
            assert b.end is None or b.start < b.end

        boundaries = list(eb.boundaries)
        eq_(sorted(boundaries, key=lambda b: b.start),
            boundaries)

    @istest
    def should_use_next_start_if_no_end_events(self):
        header = {
            u'Time Opened' : datetime.now()
        }

        start_id = 1
        end_id = 2
        start = header[u'Time Opened']
        def events():
            for i in xrange(3):
                yield Event(start + timedelta(microseconds=(i * 103)),
                    0, start_id, 0, 0, 0, "")

        eb = EpochBoundaries(header, events(), start_id, end_id, False)

        boundaries = list(eb.boundaries)

        for (i,b) in enumerate(boundaries[:-1]):
            eq_(b.end, boundaries[i+1].start)

        assert boundaries[-1].end is None

    @istest
    def should_use_end_events(self):
        header = {
            u'Time Opened' : datetime.now()
        }

        start_id = 1
        end_id = 2
        start = header[u'Time Opened']
        def events():
            for i in xrange(3):
                yield Event(start + timedelta(microseconds=(i * 103)),
                    0, start_id, 0, 0, 0, "")
                yield Event(start + timedelta(microseconds=(i * 103 + 95)),
                    0, end_id, 0, 0, 0, "")

        eb = EpochBoundaries(header, events(), start_id, end_id, False)

        for b in eb.boundaries:
            eq_(b.end, b.start + timedelta(microseconds=95))

    @istest
    def should_use_end_events(self):
        header = {
            u'Time Opened' : datetime.now()
        }

        start_id = 1
        end_id = 2
        start = header[u'Time Opened']
        def events():
            for i in xrange(3):
                yield Event(start + timedelta(microseconds=(i * 103)),
                    0, start_id, 0, 0, 0, "")
                yield Event(start + timedelta(microseconds=(i * 103 + 95)),
                    0, end_id, 0, 0, 0, "")
            yield Event(start + timedelta(microseconds=(4 * 103)),
                0, start_id, 0, 0, 0, "")

        eb = EpochBoundaries(header, events(), start_id, end_id, False)

        boundaries = list(eb.boundaries)
        for b in boundaries[:-1]:
            eq_(b.end, b.start + timedelta(microseconds=95))

        assert boundaries[-1].end is None

    @istest
    def should_include_interepochs(self):
        header = {
            u'Time Opened' : datetime.now()
        }

        start_id = 1
        end_id = 2
        start = header[u'Time Opened']
        def events():
            for i in xrange(3):
                yield Event(start + timedelta(microseconds=(i * 103)),
                    0, start_id, 0, 0, 0, "")
                yield Event(start + timedelta(microseconds=(i * 103 + 95)),
                    0, end_id, 0, 0, 0, "")
            yield Event(start + timedelta(microseconds=(4 * 103)),
                0, start_id, 0, 0, 0, "")

        eb = EpochBoundaries(header, events(), start_id, end_id, True)

        boundaries = list(eb.boundaries)

        eq_(len(boundaries), 7)
        eq_(len([b for b in boundaries if b.interepoch == True]), 3)
        eq_(len([b for b in boundaries if b.interepoch == False]), 4)


        for b in boundaries:
            assert b.end is None or b.start < b.end

            eq_(sorted(boundaries, key=lambda b: b.start),
                boundaries)
