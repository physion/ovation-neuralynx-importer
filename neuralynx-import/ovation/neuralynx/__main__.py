# Copyright 2011, Physion Consulting LLC

import sys
import platform
try:
    import readline
except ImportError:
    pass

from optparse import OptionParser
from ovation.neuralynx.importer import NeuralynxImporter
from getpass import getpass

_OVATION_CLASSPATH = {
    "Darwin" : ["/opt/ovation/ovation.jar","/opt/ovation/lib/ovation-ui.jar"],
    "Linux" : ["/usr/ovation/ovation.jar","/usr/ovation/lib/ovation-ui.jar"],
    "Windows" : ["C:\Program Files\Physion\Ovation\ovation.jar","C:\Program Files\Physion\Ovation\lib\ovation-ui.jar"]
}

def main(argv=None):
    if argv is None:
        argv = sys.argv



    usage = "usage: %prog [options] <container_uri> <source_uri> <ncs_file1> <ncs_file2> ..."
    version = "%prog BETA"
    description = "Neuralynx NEV/NCS importer for Ovation"

    parser = OptionParser(usage=usage,
        version=version,
        description=description)

    parser.add_option("-c", "--connection", dest="connection_file",
        help="Ovation connection file", metavar="FILE")
    parser.add_option("-u", "--user", dest="user",
        help="Ovation user name")
    parser.add_option("-l", "--label", dest="epoch_group_label",
        help="Epoch group label", default="Neuralynx")
    parser.add_option("-e", "--event-file", dest="event_file",
        help="Neuralynx event (.nev) file", metavar="FILE")

    (options, args) = parser.parse_args(argv)

    # Check command invariants
    if len(args) < 3:
        parser.error("incorrect number of arguments")

    if "connection_file" not in options:
        parser.error("connection file required")

    container_uri = args[0]
    source_uri = args[1]
    ncs_files = args[2:]

    if "user" in options:
        user = options.user
    else:
        user = raw_input(prompt="Username: ")

    os_name = platform.system()
    for path in _OVATION_CLASSPATH[os_name]:
        sys.path.append(path)



    importer = NeuralynxImporter(
        connection_file=options.connection_file,
        username=user,
        password=getpass())

    importer.import_ncs(container_uri,
        source_uri,
        options.label,
        ncs_files=ncs_files,
        events=options["event_file"])



if __name__ == '__main__':
    sys.exit(main())
