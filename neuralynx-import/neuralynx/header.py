
import re
from datetime import datetime,timedelta

def parse_header(reader):
    """Parses a Neuralynx data file header.

    Parameters:
    reader -- BinaryReader

    Returns:
    dict of header metadata

    """

    # Neuralynx appears to use iso-8859-1 encoding, not ASCII
    header = reader.read_string(16 * 1024, encoding='iso-8859-1')
    result = dict()
    for line in header.splitlines():
        if line.startswith('-'):
            m = re.search(r'^-(?P<key>\S*) (?P<value>.*)$', line)
            if m is not None:
                value = m.groupdict()['value'].strip()

                #Try to convert value to a number (int, then float)
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except:
                        pass

                result[m.groupdict()['key']] = value
        if line.startswith('## '):
            # Jython (2.5) doesn't support microsceconds in strptime, so we have to parse them separately
            m = re.search(r'^## (?P<key>Time (?:Opened|Closed)) \(m/d/y\)\: (?P<date>[\/\d]*)\W+\(h:m:s\.ms\)\W+(?P<time>[\d\:]*)\.(?P<millis>[\d]*)', line)
            if m is not None:
                date = m.groupdict()['date']
                time = m.groupdict()['time']

                d = datetime.strptime('%s %s' % (date,time), '%m/%d/%Y %H:%M:%S')
                fraction = timedelta(milliseconds=int(m.groupdict()['millis']))

                result[m.groupdict()['key']] = d + fraction

    return result
