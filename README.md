# Physion Ovation importer for Neuralynx data

This project provides a command-line importer for [Neuralynx](http://neuralynx.com) continuously sampled data. Epochs are optionally bounded by events (NEV) and inter-epoch data is optionally saved.


## Requirements
The Neuralynx importer requres Ovation 1.4 or greater, a 64-bit Java Virtual Machine ([download](http://www.oracle.com/technetwork/java/javase/downloads/index.html)) and Jython 2.5.1 ([download](http://www.jython.org/downloads.html)) or greater.


## Installation
After installing Jython, run `setup.py`:

	$ jython setup.py install


## Usage

After installation, you can run the importer via `osx-neuralynx-import` on OS X, `linux-neuralynx-import` on Linux or `windows-neuralynx-import` on Windows. These scripts are installed in the Jython `bin` directory. If this directory is not on the executable search path, you will need to provide the full path to the scripts to run them at the terminal command line.

In all cases, the usage is the same:
	
	Usage: [osx|linux|windows]-neuralynx-import [options] container_uri source_uri ncs_file1 [ncs_file2 ...]

	Neuralynx NEV+NCS importer for Ovation

	Options:
	  --version             show program's version number and exit
	  -h, --help            show this help message and exit
	  -c FILE, --connection=FILE
	                        Ovation connection file (required)
	  -u USER, --user=USER  Ovation user name
	  -p PASSWORD, --password=PASSWORD
	                        Ovation user password
	  -l EPOCH_GROUP_LABEL, --label=EPOCH_GROUP_LABEL
	                        Epoch group label (required)
	  -e FILE, --event-file=FILE
	                        Neuralynx event (.nev) file
	  --protocol=PROTOCOL_ID
	                        Ovaiton protocol I.D.
	  --tz=TIMEZONE, --timezone=TIMEZONE
	                        Timezone where data was acquired (defaults to local
	                        timezone)
	  --protocol-parameter=PROTOCOL_PARAMETERS
	  -v, --verbose         Verbose logging

	  Epoch boundaries:
	    Epoch boundaries may be defined by events. If either start or end
	    boundary events are defined, an event file (.nev) must be provided

	    --epoch-start=EPOCH_START_EVENT_ID
	                        Epoch start event I.D.
	    --epoch-end=EPOCH_END_EVENT_ID
	                        Epoch end event I.D. (required)
	    --include-interepoch
	                        Import inter-epoch data
