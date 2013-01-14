# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

__author__ = 'barry'

import binary_reader
from datetime import timedelta

class Boundary(object):
    def __init__(self, start, end, interepoch):
        self.start = start
        self.end = end
        self.interepoch = interepoch


class EpochBoundaries(object):
    def __init__(self, header, events, start_event_id, end_event_id, include_interepoch):
        self.header = header
        self._events = events
        self.start_event_id = start_event_id
        self.end_event_id = end_event_id
        self.include_interepoch = include_interepoch
        self._loaded = False

    def _load(self):
        if not self._loaded:
            self.events_list = list(self._events)
            self._loaded = True

    @property
    def boundaries(self):
        if not self._loaded:
            self._load()

        events = self.events_list

        start_events = [e.event_time for e in events if e.event_id == self.start_event_id]
        end_events = None if self.end_event_id is None else [e.event_time for e in events if e.event_id == self.end_event_id]

        has_end_events = end_events is not None and len(end_events) > 0
        start_events.sort()
        if has_end_events:
            end_events.sort()

        for (i,s) in enumerate(start_events[:-1]):
            if has_end_events:
                ends = [e for e in end_events if e > s]
                end = min(ends) if len(ends) > 0 else start_events[i+1]
            else:
                end = start_events[i+1]

            yield Boundary(s,
                end,
                False)

            if self.include_interepoch and end < start_events[i+1]:
                yield Boundary(end,
                    start_events[i+1],
                    True)

        if has_end_events:
            ends = [e for e in end_events if e > start_events[-1]]
            end = min(ends) if len(ends) > 0 else None
        else:
            end = None

        yield Boundary(start_events[-1],
            end,
            False)




class Event(object):
    def __init__(self, event_time, packet_id, event_id, ttl_value, crc, extra, event_string):
        self.event_time = event_time
        self.packed_id = packet_id
        self.event_id = event_id
        self.ttl_value = ttl_value
        self.crc = crc
        self.extra = extra
        self.event_string = event_string


def nev_events(reader, header):
    """Returns a generator for Events from the given reader.

    Parameters:
    reader -- binary.BinaryReader
    header -- dict of header (via header.parse_header)

    """

    start_time = header[u'Time Opened']
    try:
        while(True):
            reader.read('int16') #reserved
            packet_id = reader.read('int16')
            data_size = reader.read('int16') # Should be 2, but isn't

            dt = timedelta(microseconds=reader.read('uint64'))
            event_time = start_time + dt

            event_id = reader.read('int16')
            ttl_value = reader.read('int16')
            crc = reader.read('int16')
            reader.read('int16') #reserved
            reader.read('int16') #reserved
            extra = reader.read_array('int32', 8)

            # Neuralynx appears to use iso-8859-1 encoding, not ASCII
            event_string = reader.read_string(128, encoding='iso-8859-1')

            yield Event(event_time, packet_id, event_id, ttl_value, crc, extra, event_string)

    except binary_reader.BinaryReaderEOFException:
        return
