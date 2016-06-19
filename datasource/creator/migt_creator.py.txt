'''Datasource for Migt data stream.'''
import sys
import gzip
from base_creator import BaseDatasourceCreator

class MigtDatasourceCreator(BaseDatasourceCreator):
    '''Migt Datasource Creator class.'''
    def __init__(self, source, limit, timestamp_filename):
        super(MigtDatasourceCreator, self).__init__(source, limit, timestamp_filename)

    @staticmethod
    def is_reputation(string):
        '''Check if argument can be considered web reputation.'''
        try:
            rep = int(string)
            return rep >= -127 and rep <= 127
        except ValueError:
            return False

    def _parse_file(self, filename):
        '''Parse one Migt file. Take only lines that have url reputation.'''
        dataset = dict()
        input_file = gzip.open(filename, 'rb')
        content = input_file.read()
        rows = content.split('\n')

        for row in rows:
            data = row.split('\t')
            if len(data) > 2 and MigtDatasourceCreator.is_reputation(data[-2]):
                reputation = int(data[-2])
                url = BaseDatasourceCreator._normalize_url(data[-1])
                if reputation >= 30:
                    dataset[url] = [0.0, 1.0]
                elif reputation < 15:
                    dataset[url] = [1.0, 0.0]
        input_file.close()
        return dataset

def main(args):
    '''Test function for datasource migt creator.'''
    if len(args) != 5:
        print "Please use this script in following way: datasource_migt_creator.py " \
              "<source_dir> <limit> <dest_filename> <timestamp_filename>"
        exit()

    source_dir = args[1]
    limit = long(args[2])
    dest_filename = args[3]
    timestamp_filename = args[4]

    telemetry_creator = MigtDatasourceCreator(source_dir, limit, timestamp_filename)
    telemetry_creator.create_dataset(dest_filename)

if __name__ == '__main__':
    main(sys.argv)
