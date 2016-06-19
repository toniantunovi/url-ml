'''
This module combines different datasources to one, and produces training and validation
dataset files. Created dataset is balanced and different datasources priorities
are taken into consideration.
'''
import random
from operator import itemgetter
from datasource.provider.datasource_factory import DatasourceFactory

class DatasourceAggregator(object):
    '''Class that aggregates different datasources.'''
    def __init__(self, datasources_properties):
        self.datasources = []

        datasource_factory = DatasourceFactory()

        datasources_properties = sorted(datasources_properties, key=itemgetter('priority'), reverse=True)
        for ds_property in datasources_properties:
            if ds_property['active']:
                self.datasources.append(datasource_factory.get_new_datasource(ds_property['type'],
                                                                              ds_property['source'],
                                                                              ds_property['priority'],
                                                                              ds_property['active']))

    def get_dataset(self):
        '''Returns balanced combination of datasets.'''
        dataset_class0 = dict()
        dataset_class1 = dict()
        for datasource in self.datasources:
            print "Getting source="+datasource.source+". len([0 1])="\
                  +str(len(dataset_class0))+"len([1 0])="+str(len(dataset_class0))

            [data_x, data_y] = datasource.get_all_data()
            ds_dataset = dict(zip(data_x, data_y))
            ds_dataset0 = dict((k, v) for k, v in ds_dataset.iteritems() if v == [0.0, 1.0])
            ds_dataset1 = dict((k, v) for k, v in ds_dataset.iteritems() if v == [1.0, 0.0])
            dataset_class0.update(ds_dataset0)
            dataset_class1.update(ds_dataset1)

        len0 = len(dataset_class0)
        len1 = len(dataset_class1)

        if len0 < len1:
            dataset_class1 = dict(random.sample(dataset_class1.items(), len0))
        elif len1 < len0:
            dataset_class0 = dict(random.sample(dataset_class0.items(), len1))

        dataset_class1.update(dataset_class0)
        return dataset_class1

    @staticmethod
    def __split_dataset(dataset, n_validation):
        if n_validation >= len(dataset):
            raise Exception("Dataset too small for validation size=" + str(n_validation))

        keys = set(dataset.keys())
        validation_keys = set(random.sample(keys, n_validation))
        training_keys = keys - validation_keys

        training_dataset = dict((k, v) for k, v in dataset.iteritems() if k in training_keys)
        validation_dataset = dict((k, v) for k, v in dataset.iteritems() if k in validation_keys)
        return [training_dataset, validation_dataset]

    @staticmethod
    def __write_dataset(dataset, filename):
        file_out = open(filename, 'w')
        for key in dataset.iterkeys():
            if dataset[key] == [0.0, 1.0]:
                file_out.write(key + " 0 1\n")
            else:
                file_out.write(key + " 1 0\n")
        file_out.close()

    def create_datasource(self, training_filename, validation_filename, n_validation):
        '''Write the result of 'get_dataset' method to file.'''
        [training_dataset, validation_dataset] = \
            DatasourceAggregator.__split_dataset(self.get_dataset(), n_validation)
        DatasourceAggregator.__write_dataset(training_dataset, training_filename)
        DatasourceAggregator.__write_dataset(validation_dataset, validation_filename)
