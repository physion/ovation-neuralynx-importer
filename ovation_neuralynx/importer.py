# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

from __future__ import with_statement

import logging
import os.path
import ovation

from jnius import autoclass
LocalDateTime = autoclass("org.joda.time.LocalDateTime")

from getpass import getpass
from ovation import DateTimeZone
from ovation.connection import connect
from ovation import Maps
from ovation.conversion import to_map, asclass

from ovation_neuralynx.exceptions import ImportException
from ovation_neuralynx.header import parse_header
from ovation_neuralynx.nev import EpochBoundaries, nev_events
from ovation_neuralynx.ncs import CscData, ncs_blocks
from ovation_neuralynx.binary_reader import ManagedBinaryReader, BinaryReader, NEURALYNX_ENDIAN

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

        logging.info("Authenticating")
        self.dsc = ovation.connect(self.username, self.pasword)

        ctx = self.dsc.getContext()
        container = asclass('us.physion.ovation.domain.mixin.EpochGroupContainer', ctx.getObjectWithURI(container_uri))
        source = asclass('Source', ctx.getObjectWithURI(source_uri)) # ovation://<uuid>
        self.protocol = asclass('Protocol', None) # TODO how do we get object from protocol_id,; is protocol_id == uuid ?
        self.sources = Maps.newHashMap()
        self.sources.put(source.getLabel(), source)

        # TODO figure out what should go into device params
        # device parameters
        self.device_parameters = {}

        epochs = {}
        epoch_boundaries = None
        group = None
        for f in ncs_files:
            logging.info("Reading %s", f)
            with open(f, 'rb') as ncs_file:
                reader = BinaryReader(ncs_file, NEURALYNX_ENDIAN)
                header = parse_header(reader)
                device_name = header["AcqEntName"]
                csc_data = CscData(header, ncs_blocks(reader, header))

                open_time = header["Time Opened"]

                # We assume all times are datetime in given local zone
                start = LocalDateTime(open_time).toDateTime(self.timezone)

                if group is None:
                    logging.info("Inserting top-level EpochGroup")
                    group = container.insertEpochGroup(label,
                        start,
                        to_map(self.protocol_parameters),
                        to_map(device_parameters)
                    )

                if event_file is None or start_id is None:
                    if not None in epochs:
                        epochs[None] = self.insert_epoch(group, open_time, None, False)

                    self.append_response(epochs[None], device_name, csc_data, open_time, None)

                else:
                    if epoch_boundaries is None:
                        logging.info("Determining Epoch boundaries")
                        with open(event_file, 'rb') as ef:
                            reader = BinaryReader(ef, NEURALYNX_ENDIAN)
                            header = parse_header(reader)
                            epoch_boundaries = list(EpochBoundaries(header,
                                nev_events(reader, header),
                                start_id,
                                end_id,
                                include_interepoch).boundaries)

                    current_epoch = None
                    for epoch_boundary in epoch_boundaries:
                        if not epoch_boundaries in epochs:
                            epochs[epoch_boundary] = self.insert_epoch(group,
                                epoch_boundary.start,
                                epoch_boundary.end,
                                epoch_boundary.interepoch)

                        epoch = epochs[epoch_boundary]
                        if current_epoch is not None and epoch.getPreviousEpoch() is None:
                            epoch.setPreviousEpoch(current_epoch)

                        self.append_response(epoch, device_name, csc_data, epoch_boundary.start, epoch_boundary.end)

                        current_epoch = epoch



    def insert_epoch(self, group, start, end, interepoch):
        logging.info("Importing Epoch %s : %s", start, end)

        epoch = group.insertEpoch(
                self.sources,
                None,
                LocalDateTime(start).toDateTime(self.timezone),
                LocalDateTime(end).toDateTime(self.timezone),
                self.protocol, # self.protocol_id if not interepoch else "%s.inter-epoch" % self.protocol_id,
                to_map(self.protocol_parameters),
                to_map(self.device_parameters)
            )
        return epoch

    def append_response(self, epoch, device_name, csc_data, start, end):

        devices = Maps.newHashMap()
        devices.put(device_name, 'Neuralynx')
        epoch.getParent().getExperiment().setEquipmentSetupFromMap(devices)

        samples = csc_data.samples_by_date(start, end)
        if len(samples) > 0:
            logging.info("  Inserting response %s for Epoch %s", device_name, epoch.getStartTime().toString())
            numeric_data = ovation.NumericData(samples)
            epoch.insertNumericMeasurement(     # epoch.insertResponse(device,
                String name,                    #     csc_data.header,
                self.sources.keySet(),          #     numeric_data,
                devices.keySet(),               #     u'µV',
                numeric_data                    #     'time',
            )                                   #     csc_data.sampling_rate_hz,
                                                #     'Hz',
                                                #     ovation.IResponseData.NUMERIC_DATA_UTI)

        return epoch





