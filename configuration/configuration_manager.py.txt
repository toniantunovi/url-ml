'''Configuration manager for ML-Server components'''
import json

class ConfigurationManager(object):
    '''Class for loading and providing configuration to ML-Server components'''
    def __init__(self, properties_filename):
        with open(properties_filename) as properties_file:
            self.properties = json.load(properties_file)

    def get_optimization_config(self):
        '''Getter for optimization component config.'''
        return self.properties["properties_optimization"]

    def get_datasources_config(self):
        '''Getter for datasources component config.'''
        return self.properties["properties_datasources"]

    def get_prediction_config(self):
        '''Getter for prediction component config.'''
        return self.properties["properties_prediction"]
