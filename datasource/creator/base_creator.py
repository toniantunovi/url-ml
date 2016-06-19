'''Abstract datasource to be extended by other datasource classes.'''
import abc
import os
import random

class BaseDatasourceCreator(object):
    '''Abstract datasource class.'''
    __metaclass__ = abc.ABCMeta

    def __init__(self, source, limit, timestamp_filename):
        self.source = source
        self.limit = limit
        self.timestamp_filename = timestamp_filename
        self.loaded_domains = dict()
        self.urls_loaded = 0

    def __save_timestamp(self, filename):
        '''Save the date from provided file in timestamp file.'''
        if filename is not None:
            timestamp = os.path.getmtime(filename)
            timestamp_file = self.timestamp_filename
            filep = open(timestamp_file, 'w')
            filep.write(str(timestamp))
            filep.close()

    def __load_timestamp(self):
        '''Load last timestamp from timestamp file.'''
        timestamp_file = self.timestamp_filename
        if os.path.isfile(timestamp_file):
            filep = open(timestamp_file, 'r')
            timestamp = float(filep.read())
            return timestamp
        else:
            return 0

    @staticmethod
    def _normalize_url(url):
        url = url.lower()
        url = url.replace(" ", "%20")
        if "//" in url[0:8]:
            url = url[url.find("//")+2:]

        if "www." in url[0:8]:
            url = url[url.find("www.")+4:]

        return url

    def _filter_parsed_batch(self, data_batch):
        output_batch = dict()
        for url in data_batch.iterkeys():
            if '/' in url:
                domain = url[:url.find('/')]
            else:
                domain = url

            if domain in self.loaded_domains:
                if self.urls_loaded > 100 and \
                                self.loaded_domains[domain] > self.urls_loaded/100.0:
                    continue
                else:
                    self.loaded_domains[domain] += 1
            else:
                self.loaded_domains[domain] = 1

            output_batch[url] = data_batch[url]
            self.urls_loaded += 1

        return output_batch

    def get_dataset(self):
        '''Get dataset by parsing files in source dir until limit is reached.'''
        files = [os.path.join(self.source, f) for f in os.listdir(self.source)
                 if os.path.isfile(os.path.join(self.source, f))]
        files.sort(key=os.path.getctime)
        dataset = dict()

        timestamp = self.__load_timestamp()
        last_file = None
        for filename in files:
            if os.path.getmtime(filename) > timestamp:
                print "Parsing filename=" + filename + ". Current size=" + str(len(dataset))
                data_batch = self._parse_file(filename)
                data_batch = self._filter_parsed_batch(data_batch)
                dataset.update(data_batch)
                last_file = filename
                if len(dataset) >= self.limit:
                    dataset = dict(random.sample(dataset.items(), self.limit))
                    break
        self.__save_timestamp(last_file)

        return dataset

    def create_dataset(self, dest_filename):
        '''Create telemetry dataset.'''
        dataset = self.get_dataset()
        file_out = open(dest_filename, 'w')
        for url in dataset.iterkeys():
            if dataset[url] == [1.0, 0.0]:
                file_out.write(url + " 1 0\n")
            else:
                file_out.write(url + " 0 1\n")
        file_out.close()

    @abc.abstractmethod
    def _parse_file(self, filename):
        '''Parse file.'''
        return
