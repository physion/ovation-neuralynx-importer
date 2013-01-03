import struct

class BinaryReaderEOFException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'Not enough bytes in file to satisfy read request'

class BinaryReader:
    # Map well-known type names into struct format characters.
    TYPE_NAMES = {
        'int8'   :'b',
        'uint8'  :'B',
        'int16'  :'h',
        'uint16' :'H',
        'int32'  :'i',
        'uint32' :'I',
        'int64'  :'q',
        'uint64' :'Q',
        'float'  :'f',
        'double' :'d',
        'char'   :'s'}

    def __init__(self, file, endian):
        self.file = file
        self.endian = endian

    def read_string(self, bytes, encoding='utf-8'):
        s = self.file.read(bytes)
        return s.decode(encoding)

    def read(self, type_name):
        return self.read_array(type_name, 1)[0]

    def read_array(self, type_name, num_elements):
        """
        Reads num_elements as an array of type typeName
        """
        type_format = self.endian + str(num_elements) + BinaryReader.TYPE_NAMES[type_name.lower()]
        return self._read(type_format)

    def _read(self, type_format):
        type_size = struct.calcsize(type_format)
        value = self.file.read(type_size)
        if type_size != len(value):
            raise BinaryReaderEOFException
        return struct.unpack(type_format, value)

