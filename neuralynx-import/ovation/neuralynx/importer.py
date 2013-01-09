# Copyright 2011, Physion Consulting LLC

import ovation
import logging

from getpass import getpass
from org.joda.time import DateTime, DateTimeZone

from exceptions import ImportException
from header import parse_header
from binary_reader import BinaryReader, NEURALYNX_ENDIAN

class NeuralynxImporter(object):

    def __init__(self,
                 connection_file=None,
                 username=None,
                 password=None):

        if connection_file is None:
            raise ImportException("Connection file required")

        if username is None:
            raise ImportException("Username is required")

        if password is None:
            password = getpass()

        logging.info("Connecting to database at " + connection_file)
        ctx = ovation.DataStoreCoordinator.coordinatorWithConnectionFile(connection_file).getContext()

        logging.info("Authenticating")
        self.dsc = ctx.authenticateUser(username, password).getAuthenticatedDataStoreCoordinator()


    def import_ncs(self,
                   container_uri,
                   source_uri,
                   label,
                   ncs_files=None,
                   events=None):

        ctx = self.dsc.getContext()
        container = ctx.objectWithURI(container_uri)
        source = source_uri

        logging.info("Reading .ncs headers")
        headers = dict()
        for f in ncs_files:
            reader = BinaryReader(file, NEURALYNX_ENDIAN)
            header = parse_header(reader)
            headers[f] = header

        open_time = min(h["Time Opened"] for h in headers.itervalues())
        start = DateTime(open_time).withZone(DateTimeZone.getDefault())

        logging.info("Inserting top-level EpochGroup")
        group = container.insertEpochGroup(source, label, DateTime(start))

        logging.info("Determining Epoch boundaries")
        epoch_boundaries = self._epoch_boundaries(events)


    def _epoch_boundaries(self, events):
        return []


