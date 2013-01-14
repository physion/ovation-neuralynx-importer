# Copyright 2011, Physion Consulting LLC

import sys
import logging
try:
    import readline
except ImportError:
    pass

from optparse import OptionParser, OptionGroup
from neuralynx.importer import NeuralynxImporter

def main(argv=None):
    if argv is None:
        argv = sys.argv


    logging.basicConfig(level=logging.DEBUG) #TODO

    usage = "usage: %prog [options] <container_uri> <source_uri> <ncs_file1> <ncs_file2> ..."
    version = "%prog BETA"
    description = "Neuralynx NEV/NCS importer for Ovation"

    parser = OptionParser(usage=usage,
        version=version,
        description=description)

    parser.add_option("-c", "--connection", dest="connection_file",
        help="Ovation connection file (required)", metavar="FILE")
    parser.add_option("-u", "--user", dest="user",
        help="Ovation user name")
    parser.add_option("-p", "--password", dest="password",
        help="Ovation user password")
    parser.add_option("-l", "--label", dest="epoch_group_label",
        help="Epoch group label (required)", default="Neuralynx")
    parser.add_option("-e", "--event-file", dest="event_file",
        help="Neuralynx event (.nev) file", metavar="FILE")
    parser.add_option("--protocol", dest="protocol_id",
        help="Ovaiton protocol I.D.")

    event_group = OptionGroup(parser, "Epoch boundaries",
        description="Epoch boundaries may be defined by events. If either start or end boundary events are defined, an event file (.nev) must be provided")

    event_group.add_option("--epoch-start", dest="epoch_start_event",
        help="Epoch start event name")
    event_group.add_option("--epoch-end", dest="epoch_end_event",
        help="Epoch end event name")
    event_group.add_option("--include-interepoch",
        action="store_true",
        dest="include_interepoch")

    parser.add_option_group(event_group)


    (options, args) = parser.parse_args(argv)

    parser.destroy()

    # Check command invariants
    if len(args) < 3:
        parser.error("incorrect number of arguments")

    if options.connection_file is None:
        parser.error("connection file required")

    if options.epoch_group_label is None:
        parser.error("EpochGroup label is required")

    if options.protocol_id is None:
        parser.error("Protocol I.D. is required")

    container_uri = args[0]
    source_uri = args[1]
    ncs_files = args[2:]

    if options.user is not None:
        user = options.user
    else:
        user = raw_input(prompt="Username: ")


    importer = NeuralynxImporter(
        connection_file=options.connection_file,
        username=user,
        password=options.password,
        protocol_id=options.protocol_id)


    importer.import_ncs(container_uri,
        source_uri,
        options.epoch_group_label,
        ncs_files=ncs_files,
        event_file=options.event_file)



if __name__ == '__main__':
    sys.exit(main())
