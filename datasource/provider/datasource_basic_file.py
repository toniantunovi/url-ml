'''
Datasource for plain file.
This requires file in format:
[url] 0 1
[url] 1 0
Where:
"[url] 0 1" means malicious url
"[url] 1 0" means non-malicious url
'''
from datasource_base import BaseDatasource

class BasicFileDatasource(BaseDatasource):
    '''Basic file datasource class.'''

    def _load_data(self, source):
        '''Load data from basic file.'''
        file_in = open(source, 'r')
        content = file_in.read()
        examples = content.splitlines()

        dataset = dict()
        for example in examples:
            if len(example) > 3:
                url, y_1, y_2 = example.split(' ')
                dataset[url.lower()] = [float(y_1), float(y_2)]
        file_in.close()

        data_x = dataset.keys()
        data_y = [dataset[key] for key in data_x]
        return [data_x, data_y]

    def __init__(self, source, priority, active):
        super(BasicFileDatasource, self).__init__(source, priority, active)

        [self.data_x, self.data_y] = self._load_data(source)
        self.size = len(self.data_x)
        self.counter = 0

    def get_next_batch(self, batch_size):
        """Get next batch of dataset samples."""
        if batch_size > self.size:
            raise Exception("Dataset too small for batch size=" + batch_size)

        if batch_size + self.counter > self.size:
            batch_x = self.data_x[self.counter:]
            batch_y = self.data_y[self.counter:]
            remaining = batch_size - (self.size - self.counter)
            self.counter = 0
            [rec_batch_x, rec_batch_y] = self.get_next_batch(remaining)

            batch_x.extend(rec_batch_x)
            batch_y.extend(rec_batch_y)

        else:
            batch_x = self.data_x[self.counter:self.counter + batch_size]
            batch_y = self.data_y[self.counter:self.counter + batch_size]
            self.counter += batch_size

        return [batch_x, batch_y]

    def get_all_data(self):
        return [self.data_x, self.data_y]
