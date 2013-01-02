from __future__ import with_statement
import sys
import binary

def print_header(reader):
    print reader.read_string(16 * 1024)

def list_ncs(path):
    with open(path,'rb') as f:
        reader = binary.BinaryReader(f, '<')
        print_header(reader)
        print "NCS blocks:"
        try:
            for i in range(10):
                print "  Time stamp: " + str(reader.read('uint64'))
                print "  Channel number: " + str(reader.read('uint32'))
                print "  SampleFreq: " + str(reader.read('uint32'))
                num_samples = reader.read('uint32')
                print "  Valid samples: " + str(num_samples)
                print "  Samples: "
                samples = reader.read_array('int16', num_samples)
                print "    " + str(samples)
                print " "
        except binary.BinaryReaderEOFException, e:
            print "Done."

def list_nev(path):
    with open(path, 'rb') as f:
        reader = binary.BinaryReader(f, '<')
        print_header(reader)
        try:
            for i in range(10):
                reader.read('int16') #reserved
                print "  Packet ID: " + str(reader.read('int16'))
                print "  Data size (should be 2): " + str(reader.read('int16'))
                print "  Time stamp: " + str(reader.read('uint64'))
                print "  Event ID: " + str(reader.read('int16'))
                print "  TTL value: " + str(reader.read('int16'))
                print "  CRC: " + str(reader.read('int16'))
                reader.read('int16') #reserved
                reader.read('int16') #reserved
                print "  Extra: " + str(reader.read_array('int32', 8))
                print "  Event string: " + f.read(128)
                print " "
                print " "
        except binary.BinaryReaderEOFException, e:
            print "Done."


if __name__ == '__main__':

    for path in sys.argv[1:]:
        if path.endswith('ncs'):
            list_ncs(path)
        elif path.endswith('nev'):
            list_nev(path)

        print " "
        print " "
