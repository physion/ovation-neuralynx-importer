# Copyright 2011, Physion Consulting LLC
# -*- coding: utf-8 -*-

from __future__ import with_statement

import logging
import os.path
import ovation

from jnius import autoclass
DateTimeFormat = autoclass("org.joda.time.format.DateTimeFormat")

import quantities as pq

from ovation import DateTimeZone
from ovation import Maps
from ovation.core import NumericData
from ovation.data import insert_numeric_measurement
from ovation.conversion import to_map, asclass, to_java_set

from ovation_neuralynx.exceptions import ImportException
from ovation_neuralynx.header import parse_header
from ovation_neuralynx.nev import EpochBoundaries, nev_events
from ovation_neuralynx.ncs import CscData, ncs_blocks
from ovation_neuralynx.binary_reader import ManagedBinaryReader, BinaryReader, NEURALYNX_ENDIAN

class NeuralynxImporter(object):

    def __init__(self,
                 protocol=None,
                 protocol_parameters=None,
                 timezone=None):

        self.protocol_id = None
        if not protocol is None:
            self.protocol_id = protocol.getUuid().toString()

        if timezone is None:
            timezone = DateTimeZone.getDefault()

        self.protocol = protocol
        self.protocol_parameters = protocol_parameters
        self.timezone = timezone
        self.timeFormatter = DateTimeFormat.forPattern('Y-M-d HH:mm:ss.SSSSSS')


    def import_ncs(self,
               container,
               sources,
               label,
               ncs_files=list(),
               event_file=None,
               start_id=None,
               end_id=None,
               include_interepoch=True):

        self.sources = sources
        self.source_map = Maps.newHashMap()
        [self.source_map.put(source.getLabel(), source) for source in sources]

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
                start = self.timeFormatter.parseDateTime(str(open_time)).toDateTime(self.timezone)
                logging.info("Start done")

                if group is None:
                    logging.info("Inserting top-level EpochGroup")
                    group = asclass("us.physion.ovation.domain.mixin.EpochGroupContainer", container).insertEpochGroup(label,
                        start,
                        self.protocol,
                        to_map(self.protocol_parameters),
                        to_map(self.device_parameters)
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
                self.source_map,
                None,
                self.timeFormatter.parseDateTime(str(start)).toDateTime(self.timezone),
                self.timeFormatter.parseDateTime(str(end)).toDateTime(self.timezone) if end else end,
                self.protocol, # self.protocol_id if not interepoch else "%s.inter-epoch" % self.protocol_id,
                to_map(self.protocol_parameters),
                to_map(self.device_parameters)
            )
        return epoch

    def append_response(self, epoch, device_name, csc_data, start, end):
        sources = []
        iterator = epoch.getInputSources().values().iterator()
        while iterator.hasNext():
            sources.append(iterator.next().getLabel())
        devices = { device_name : 'Neuralynx' }

        samples = pq.Quantity(csc_data.samples_by_date(start, end), units='uV')
        samples.labels = [u'Membrane voltage']
        samples.sampling_rates = [csc_data.sampling_rate_hz * pq.Hz]

        devices = { device_name : 'Neuralynx' }
        name = device_name
        data_frame = { name : samples }

        if len(samples) > 0:
           logging.info("  Inserting response %s for Epoch %s", device_name, epoch.getStart().toString())
           insert_numeric_measurement(epoch,
                                      sources,
                                      devices,
                                      name,
                                      data_frame)

        return epoch
