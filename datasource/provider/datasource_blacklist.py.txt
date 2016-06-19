'''
Datasource for blacklist file.
This requires file in format:
[url1]
[url2]
...
[urln]
'''
from datasource_basic_file import BasicFileDatasource

class BlacklistDatasource(BasicFileDatasource):
    '''Blacklist datasource class.'''

    def _load_data(self, source):
        '''Load data from blacklist file.'''
        file_in = open(source, 'r')
        content = file_in.read()
        examples = content.splitlines()

        dataset = dict()
        for url in examples:
            if len(url) > 3:
                url = url.lower()
                if "//" in url[0:8]:
                    url = url[url.find("//")+2:]
                dataset[url.lower()] = [0.0, 1.0]
        file_in.close()

        data_x = dataset.keys()
        data_y = [dataset[key] for key in data_x]
        return [data_x, data_y]

    def __init__(self, source, priority, active):
        super(BlacklistDatasource, self).__init__(source, priority, active)

