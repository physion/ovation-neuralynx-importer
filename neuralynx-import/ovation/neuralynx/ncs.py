__author__ = 'barry'

import binary
from datetime import timedelta

class CscBlock(object):
    def __init__(self, start, channel_number, sample_freq_hz, samples):
        self.start = start
        self.channel_number = channel_number
        self.sample_freq_hz = sample_freq_hz
        self.samples = samples


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
    except binary.BinaryReaderEOFException:
        return

