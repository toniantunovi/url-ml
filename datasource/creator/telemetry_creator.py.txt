'''Creating Telemetry Datasource'''
import sys
from base_creator import BaseDatasourceCreator

class TelemetryDatasourceCreator(BaseDatasourceCreator):
    '''Telemetry Datasource Creator class'''
    def __init__(self, source, limit, timestamp_filename):
        super(TelemetryDatasourceCreator, self).__init__(source, limit, timestamp_filename)

    def _parse_file(self, filename):
        '''Parse file and return only green and red urls.'''
        filep = open(filename, 'r')
        content = filep.read().split("\n")
        filep.close()
        dataset = dict()
        for line in content:
            if "reputationColor=WSR_GREEN" in line:
                url = BaseDatasourceCreator._normalize_url(line[line.find('url=')+4:len(line)-2])
                dataset[url] = [1.0, 0.0]
            elif "reputationColor=WSR_RED" in line:
                url = BaseDatasourceCreator._normalize_url(line[line.find('url=')+4:len(line)-2])
                dataset[url] = [0.0, 1.0]
        return dataset

def main(args):
    '''Test function for datasource telemetry creator.'''
    if len(args) != 5:
        print "Please use this script in following way: datasource_telemetry_creator.py " \
              "<source_dir> <limit> <dest_filename> <timestamp_filename>"
        exit()

    source_dir = args[1]
    limit = long(args[2])
    dest_filename = args[3]
    timestamp_filename = args[4]

    telemetry_creator = TelemetryDatasourceCreator(source_dir, limit, timestamp_filename)
    telemetry_creator.create_dataset(dest_filename)

if __name__ == '__main__':
    main(sys.argv)
