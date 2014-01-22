# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

import sys
from ovation.conversion import asclass
from ovation.importer import import_main
from ovation_neuralynx.importer import NeuralynxImporter

DESCRIPTION="""Neuralynx NEV+NCS importer for Ovation"""

def main(argv=sys.argv, dsc=None):
    def import_wrapper(data_context,
                  container=None,
                  protocol=None,
                  files=None,
                  sources=None,
                  event_file=None,
                  protocol_parameters=None,
                  epoch_start_event_id=None,
                  epoch_end_event_id=None,
                  include_interepoch=False,
                  **args):

        container = data_context.getObjectWithURI(container)
        protocol_entity = data_context.getObjectWithURI(protocol)
        if protocol_entity:
            protocol = asclass("Protocol", protocol_entity)
        else:
            protocol = None

        if protocol_parameters is None:
            protocol_parameters = {}
        else:
            protocol_parameters = dict(protocol_parameters)

        if not sources is None:
            sources = [data_context.getObjectWithURI(source) for source in sources]

        # do something with the files...
        # importer = NeuralynxImporter(
        #     connection_file=options.connection_file,
        #     username=user,
        #     password=options.password,
        #     protocol_id=options.protocol_id,
        #     protocol_parameters=protocol_parameters,
        #     timezone=tz)
        # 
        # 
        # importer.import_ncs(container_uri,
        #     source_uri,
        #     options.epoch_group_label,
        #     ncs_files=ncs_files,
        #     event_file=options.event_file,
        #     start_id=options.epoch_start_event_id,
        #     end_id=options.epoch_end_event_id,
        #     include_interepoch=options.include_interepoch)

        return 0

    def parse_wrapper(parser):
        parser.add_argument("-e", "--event-file", dest="event_file",
            help="Neuralynx event (.nev) file", metavar="FILE")
        parser.add_argument("--protocol-parameter", dest="protocol_parameters",
            nargs=2, action="append")

        event_group = parser.add_argument_group("epoch boundaries",
            description="Epoch boundaries may be defined by events. If either start or end boundary events are defined, an event file (.nev) must be provided")

        event_group.add_argument("--epoch-start", dest="epoch_start_event_id",
            help="Epoch start event I.D.", type=int)
        event_group.add_argument("--epoch-end", dest="epoch_end_event_id",
            help="Epoch end event I.D.", type=int)
        event_group.add_argument("--include-interepoch",
            action="store_true",
            dest="include_interepoch",
            help="Import inter-epoch data")

        return parser

    return import_main(argv=argv,
                       name='neuralynx_import',
                       description=DESCRIPTION,
                       file_ext='ncs',
                       import_fn=import_wrapper,
                       parser_callback=parse_wrapper,
                       dsc=dsc)


if __name__ == '__main__':
    sys.exit(main())
