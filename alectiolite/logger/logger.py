import os
from .backend.backend_server import BackendServer


def pickle_logger(monitor ,data ,config):
	if monitor =='datasetstate' and not subset:
		filename ='data_map.pkl'
	elif monitor =='datasetstate' and  subset:
		filename ='data_map_{}.pkl'
	else:
		raise ValueError("Invalid value chosen to monitor")

	with open(filename, 'wb') as f:
        pickled = pickle.dumps(data)
        optimized_pickle = pickletools.optimize(pickled)
        f.write(optimized_pickle)