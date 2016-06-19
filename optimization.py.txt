import sys
from datasource.datasource_manager import DatasourceManager
from configuration.configuration_manager import ConfigurationManager
from optimization.continuous_optimization import ContinuousOptimizer

def main(args):
    '''Entry point to optimization process.'''
    if len(args) != 2:
        print "Please use this script in following way: optimization.py " \
              "<properties_file>"
        exit()
    properties_filename = args[1]
    con_man = ConfigurationManager(properties_filename)
    dat_man = DatasourceManager(con_man)
    opt = ContinuousOptimizer(con_man, dat_man)
    opt.run()

if __name__ == '__main__':
    main(sys.argv)