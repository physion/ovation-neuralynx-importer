# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

from __future__ import with_statement

import logging
import os.path
import ovation

from getpass import getpass
from org.joda.time import LocalDateTime, DateTimeZone

from ovneuralynx.exceptions import ImportException
from ovneuralynx.header import parse_header
from ovneuralynx.nev import EpochBoundaries, nev_events
from ovneuralynx.ncs import CscData, ncs_blocks
from binary_reader import ManagedBinaryReader, BinaryReader, NEURALYNX_ENDIAN

class NeuralynxImporter(object):

    def __init__(self,
                 connection_file=None,
                 username=None,
                 password=None,
                 protocol_id='ovneuralynx',
                 protocol_parameters=None,
                 timezone=DateTimeZone.getDefault()):

        if connection_file is None:
            raise ImportException("Connection file required")

        if username is None:
            raise ImportException("Username is required")

        self.connection_file = connection_file
        self.username = username
        self.password = password
        self.protocol_id = protocol_id
        self.protocol_parameters = protocol_parameters
        self.timezone = timezone



    def import_ncs(self,
               container_uri,
               source_uri,
               label,
               ncs_files=list(),
               event_file=None,
               start_id=None,
               end_id=None,
               include_interepoch=True):


        if self.password is None:
            password = getpass()
        else:
            password = self.password

        logging.info("Connecting to database at " + self.connection_file)
        ctx = ovation.DataStoreCoordinator.coordinatorWithConnectionFile(os.path.expanduser(self.connection_file)).getContext()

        logging.info("Authenticating")
        ctx.authenticateUser(self.username, password)
        self.dsc = ctx.getAuthenticatedDataStoreCoordinator()

        ctx = self.dsc.getContext()
        container = ctx.objectWithURI(container_uri)
        source = ctx.objectWithURI(source_uri)

        logging.info("Reading .ncs headers")
        csc_data = {}
        headers = {}
        readers = []
        for f in ncs_files:
            reader = ManagedBinaryReader(f, NEURALYNX_ENDIAN)
            readers.append(reader)
            header = parse_header(reader)
            headers[f] = header
            csc_data[header["AcqEntName"]] = CscData(header, ncs_blocks(reader, header))

        try:
            open_time = min(h["Time Opened"] for h in headers.itervalues())

            # We assume all times are datetime in given local zone
            start = LocalDateTime(open_time).toDateTime(self.timezone)

            logging.info("Inserting top-level EpochGroup")
            group = container.insertEpochGroup(source, label, start)

            logging.info("Determining Epoch boundaries")
            if event_file is None or start_id is None:
                self.import_epoch(group, csc_data, open_time, None, False)
            else:
                reader = ManagedBinaryReader(event_file, NEURALYNX_ENDIAN)
                readers.append(reader)
                header = parse_header(reader)
                epoch_boundaries = EpochBoundaries(header,
                    nev_events(reader, header),
                    start_id,
                    end_id,
                    include_interepoch)

                self.import_epochs(group, epoch_boundaries.boundaries, csc_data)
        finally:
            for r in readers:
                r.close()

    def import_epoch(self, group, csc_data, start, end, interepoch):
        logging.info("Importing Epoch %s : %s", start, end)

        epoch = group.insertEpoch(
                LocalDateTime(start).toDateTime(self.timezone),
                LocalDateTime(end).toDateTime(self.timezone),
                self.protocol_id if not interepoch else "%s.inter-epoch" % self.protocol_id,
                self.protocol_parameters if self.protocol_parameters is not None else {}
            )

        for (device_name, csc) in csc_data.iteritems():
            device = group.getExperiment().externalDevice(device_name, 'Neuralynx')
            logging.info("  Inserting response: %s", device.getName())
            samples = csc.samples_by_date(start, end)
            if len(samples) > 0:
                numeric_data = ovation.NumericData(samples)
                epoch.insertResponse(device,
                    csc.header,
                    numeric_data,
                    u'µV',
                    'time',
                    csc.sampling_rate_hz,
                    'Hz',
                    ovation.IResponseData.NUMERIC_DATA_UTI)

    def import_epochs(self, group, epoch_boundaries, csc_data):
        current_epoch = None
        for eb in epoch_boundaries:
            epoch = self.import_epoch(group, csc_data, eb.start, eb.end, eb.interepoch)
            if current_epoch is not None:
                epoch.setPreviousEpoch(current_epoch)
            current_epoch = epoch




