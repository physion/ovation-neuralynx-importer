# Copyright 2011, Physion Consulting LLC

import logging
import os.path
import ovation

from getpass import getpass
from org.joda.time import DateTime, DateTimeZone

from neuralynx.exceptions import ImportException
from neuralynx.header import parse_header
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

        self.connection_file = connection_file
        self.username = username
        self.password = password



    def import_ncs(self,
               container_uri,
               source_uri,
               label,
               ncs_files=[],
               event_file=None):


        if self.password is None:
            password = getpass()

        logging.info("Connecting to database at " + self.connection_file)
        ctx = ovation.DataStoreCoordinator.coordinatorWithConnectionFile(os.path.expanduser(self.connection_file)).getContext()

        logging.info("Authenticating")
        self.dsc = ctx.authenticateUser(self.username, password).getAuthenticatedDataStoreCoordinator()

        ctx = self.dsc.getContext()
        container = ctx.objectWithURI(container_uri)
        source = source_uri

        logging.info("Reading .ncs headers")
        headers = dict()
        ncs_readers = dict()
        for f in ncs_files:
            reader = BinaryReader(file, NEURALYNX_ENDIAN)
            header = parse_header(reader)
            headers[f] = header
            ncs_readers[header["AcqEntName"]] = reader

        open_time = min(h["Time Opened"] for h in headers.itervalues())
        start = DateTime(open_time).withZone(DateTimeZone.getDefault())

        logging.info("Inserting top-level EpochGroup")
        group = container.insertEpochGroup(source, label, DateTime(start))

        logging.info("Determining Epoch boundaries")
        epoch_boundaries = self._epoch_boundaries(event_file)

        self.import_epochs(group, epoch_boundaries, ncs_readers)

    def import_epochs(self, group, epoch_boundaries, ncs_readers):
        for (start,end) in epoch_boundaries:
            logging.info("Importing Epoch %f-%f ms" % (start,end))

    def _epoch_boundaries(self, event_path):
        """Returns a sequnce of ordered tuple Epoch boundaries (start,end).

        Times in microseconds.

        end = [] indicates the Epoch end is the next Epoch start boundary

        Parameters
            event_path -- .nev file path

        """

        if event_path is None:
            return ((0,[]),)



