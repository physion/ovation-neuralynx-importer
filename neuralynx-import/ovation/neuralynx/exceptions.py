# Copyright 2011, Physion Consulting LLC

class ImportException(StandardError):

    def __init__(self, message):
        super(StandardError, self).__init__(message)
