'''Datasource manager module.'''
from datasource.creator.datasource_aggregator import DatasourceAggregator
from datasource.provider.datasource_factory import DatasourceFactory

class DatasourceManager(object):
    '''Datasource manager class.'''
    def __init__(self, configuration_manager):
        properties = configuration_manager.get_datasources_config()
        training_filename = properties['training_filename']
        validation_filename = properties['validation_filename']
        n_validation = properties['n_validation']

        if properties['create_datasource']:
            aggregator = DatasourceAggregator(properties['aggregator'])
            aggregator.create_datasource(training_filename, validation_filename, n_validation)

        datasource_factory = DatasourceFactory()
        self.training_datasource = datasource_factory.\
            get_new_datasource("basic_file", training_filename, 1, True)
        self.validation_datasource = datasource_factory.\
            get_new_datasource("basic_file", validation_filename, 1, True)

    def get_validation_dataset(self, size):
        '''Return validation set.'''
        return self.validation_datasource.get_next_batch(size)

    def get_next_batch(self, batch_size):
        '''Get next batch of data.'''
        return self.training_datasource.get_next_batch(batch_size)
