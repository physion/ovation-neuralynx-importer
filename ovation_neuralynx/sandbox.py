# Copyright 2011, Physion Consulting LLC

from __future__ import with_statement
import sys
import binary_reader
import logging
from header import parse_header
from pprint import pprint
from ncs import ncs_blocks, CscData
from nev import nev_events, EpochBoundaries

def print_header(reader):
    header = parse_header(reader)
    pprint(header)
    return header

def collect_ncs_samples(path):
    logging.debug("Collecting samples")
    with open(path,'rb') as f:
        reader = binary_reader.BinaryReader(f, binary_reader.NEURALYNX_ENDIAN)
        header = print_header(reader)
        data = CscData(header, ncs_blocks(reader, header))
        samples = data.samples(0)
        logging.debug("Done. %d samples" % len(samples))

def list_ncs(path):
    with open(path,'rb') as f:
        reader = binary_reader.BinaryReader(f, binary_reader.NEURALYNX_ENDIAN)
        header = print_header(reader)
        print ' '
        print ' '
        print "NCS blocks:"
        total_samples = 0
        n = 0
        for block in ncs_blocks(reader, header):
            n += 1
            if n % 10000 == 0:
                print 'Block %d' % n
            total_samples += len(block.samples)

        print "Done (" + str(total_samples) + " samples)."

def list_nev(path):
    with open(path, 'rb') as f:
        reader = binary_reader.BinaryReader(f, '<')
        header = print_header(reader)
        print ' '
        print ' '
        print 'NEV blocks:'
        for event in nev_events(reader, header):
                print "  Packet ID: " + str(event.event_id)
                print "  Time stamp: " + str(event.event_time)
                print "  Event ID: " + str(event.event_id)
                print "  TTL value: " + str(event.ttl_value)
                print "  CRC: " + str(event.crc)
                print "  Extra: " + str(event.extra)
                print "  Event string: " + event.event_string
                print " "
                print " "
        print "Done."

def list_boundaries(path):
    with open(path, 'rb') as f:
        reader = binary_reader.BinaryReader(f, '<')
        header = print_header(reader)
        print ' '
        print ' '
        eb = EpochBoundaries(header,
            nev_events(reader, header),
            11,
            1,
            False
            )

        for b in eb.boundaries:
            print "[",b.start, "  -  ", b.end, "]"


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    for path in sys.argv[1:]:
        if path.endswith('ncs'):
            #list_ncs(path)
            collect_ncs_samples(path)
        elif path.endswith('nev'):
            list_nev(path)
            #list_boundaries(path)
        print " "
        print " "
