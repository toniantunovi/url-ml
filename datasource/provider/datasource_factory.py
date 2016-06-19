'''Factory for datasource class objects.'''
from datasource.provider.datasource_basic_file import BasicFileDatasource
from datasource.provider.datasource_blacklist import BlacklistDatasource
from datasource.provider.datasource_whitelist import WhitelistDatasource


class DatasourceFactory(object):
    '''Datasource factory class.'''
    def get_new_datasource(self, datasource_type, source, priority, active):
        if datasource_type == "basic_file":
            return BasicFileDatasource(source, priority, active)
        elif datasource_type == "blacklist":
            return BlacklistDatasource(source, priority, active)
        elif datasource_type == "whitelist":
            return WhitelistDatasource(source, priority, active)
        else:
            raise Exception("Datasource with type=" + datasource_type + " is not implemented.")
