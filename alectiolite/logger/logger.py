import os
import pickle
import pickletools
from rich.table import Table
from rich.console import Console
from ..config import backend_config
from ..config import update_backend_config


console = Console(style ="green")


def _reel_in_configs(config):
	cfglist = []
	for k, v in config.items():
		cfglist.extend([str(k).upper(),v])
	update_backend_config(backend_config, cfglist)

def _checkdirs(dir_ , kind ='experiment'):
	if not os.path.exists(dir_):
		os.makedirs(dir_,exist_ok =True)
		console.print("All Alectio {} logs will be saved to {}".format(kind,backend_config.EXPERIMENT_ID))


def pickle_logger(monitor ,data ,config):
	"""
	Used by users to log experiment level logs 
	#TODO replace/adapt with framework based callbacks

	"""
	_reel_in_configs(config)
	##setup logdirs
	#TO DO : A better solution for buckets , API in works
	if backend_config.BUCKET_NAME == backend_config.SANDBOX_BUCKET:
		experiment_dir = os.path.join(backend_config.USER_ID,
			                          backend_config.PROJECT_ID ,
                                      backend_config.EXPERIMENT_ID
                                               )
		_checkdirs(experiment_dir,'experiment')
	else:
		experiment_dir = os.path.join(backend_config.PROJECT_ID ,
                                          backend_config.EXPERIMENT_ID
                                               )
		_checkdirs(experiment_dir,'experiment')
            
	if monitor =='datasetstate' and backend_config.CUR_LOOP == '':
		filename = os.path.join(experiment_dir, 'data_map.pkl')
	elif monitor =='datasetstate' and  backend_config.CUR_LOOP >= 0:
		filename = os.path.join(experiment_dir, 'data_map_{}.pkl'.format(backend_config.CUR_LOOP))
	else:
		raise ValueError("Invalid value chosen to monitor")

	with open(filename, 'wb') as f:
		pickled = pickle.dumps(data)
		optimized_pickle = pickletools.optimize(pickled)
		f.write(optimized_pickle)
		console.print("Successfully logged {} for your current experiment". format(monitor))