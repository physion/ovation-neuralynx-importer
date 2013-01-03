__author__ = 'barry'

import binary
from datetime import timedelta

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

    except binary.BinaryReaderEOFException:
        return
