'''Abstract datasource to be extended by other datasource classes.'''
import abc

class BaseDatasource(object):
    '''Abstract datasource class.'''
    __metaclass__ = abc.ABCMeta

    def __init__(self, source, priority, active):
        self.source = source
        self.priority = priority
        self.active = active

    @abc.abstractmethod
    def get_next_batch(self, batch_size):
        '''Getting next batch from datasource.'''
        return

    @abc.abstractmethod
    def get_all_data(self):
        '''Getting all data from datasource.'''
        return
