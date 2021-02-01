import os
import json
import errno
import boto3
import pickle
import pickletools
from rich.table import Table
from rich.console import Console
from ..config import backend_config
from ..config import update_backend_config
from ..backend.s3_client import S3Client

console = Console(style ="green")
client = S3Client()


def _reel_in_configs(config):
	cfglist = []
	for k, v in config.items():
		cfglist.extend([str(k).upper(),v])
	update_backend_config(backend_config, cfglist)

def _checkdirs(dir_ , kind ='experiment'):
	if not os.path.exists(dir_):
		os.makedirs(dir_,exist_ok =True)
		console.print("All Alectio {} logs will be saved to {}".format(kind,backend_config.EXPERIMENT_ID))

def _check_monitor(monitor):
	for f in backend_config.OUTFILES:
		if f in monitor:
			return monitor
	for f in backend_config.INFILES:
		if f in monitor:
			return monitor

	raise ValueError("Invalid monitor value {} ".format(monitor))



def experiment_logger(monitor ,data ,config):
	"""
	Used by users to log experiment level logs 
	#TODO replace/adapt with framework based callbacks

	"""
	_reel_in_configs(config)
	_check_monitor(monitor)
	##setup logdirs
	#TO DO : A better solution for buckets , API in works
	if backend_config.BUCKET_NAME == backend_config.SANDBOX_BUCKET:
		experiment_dir = os.path.join(backend_config.USER_ID,
			                          backend_config.PROJECT_ID ,
                                      backend_config.EXPERIMENT_ID
                                               )
		project_dir = os.path.join(backend_config.USER_ID,
			                       backend_config.PROJECT_ID
                                   )
		_checkdirs(experiment_dir,'experiment')
	else:
		experiment_dir = os.path.join(backend_config.PROJECT_ID ,
                                          backend_config.EXPERIMENT_ID
                                               )
		project_dir = os.path.join(backend_config.PROJECT_ID)
		_checkdirs(experiment_dir,'experiment')
            
	if monitor =='datasetstate' and backend_config.CUR_LOOP == '':
		filename = os.path.join(experiment_dir, 'data_map.pkl')
		_log_pickle(monitor,filename,data)
	elif monitor =='datasetstate' and  backend_config.CUR_LOOP >= 0:
		filename = os.path.join(experiment_dir, 'data_map_{}.pkl'.format(backend_config.CUR_LOOP))
		_log_pickle(monitor,filename,data)

	elif monitor =='meta': #TODO when streaming is available people may add classes on the fly
		filename = os.path.join(project_dir, 'meta.json')
		_log_json(monitor,filename,data)
	elif monitor =='selected_indices' and backend_config.CUR_LOOP == '':
		filename = os.path.join(experiment_dir, 'selected_indices.pkl')
		_log_pickle(monitor,filename,data, mode ='read')
	elif monitor =='selected_indices' and  backend_config.CUR_LOOP >= 0:
		filename = os.path.join(experiment_dir, 'selected_indices_{}.pkl'.format(backend_config.CUR_LOOP))
		_log_pickle(monitor,filename,data , mode ='read')
	elif monitor =='pre_softmax' and backend_config.CUR_LOOP == '':
		filename = os.path.join(experiment_dir, 'pre_softmax.pkl')
		_remap_outs(data)
		_log_pickle(monitor,filename,data)
		_sweep_experiment(monitor)
	elif monitor =='pre_softmax' and  backend_config.CUR_LOOP >= 0:
		filename = os.path.join(experiment_dir, 'pre_softmax_{}.pkl'.format(backend_config.CUR_LOOP))
		remapped_data = _remap_outs(data)
		_log_pickle(monitor,filename,remapped_data)
		_sweep_experiment(monitor)

	else:
		raise ValueError("Invalid experiment loop and/or monitor value chosen to monitor")



def _log_json(monitor,filename,data):
	# Usually read 
	bucket = boto3.resource("s3").Bucket(backend_config.BUCKET_NAME)
	json_load_s3 = lambda f: json.load(bucket.Object(key=f).get()["Body"])
	meta_data = json_load_s3(filename)
	with open(filename,'w') as f:
		json.dump(meta_data,f)

	console.print("Successfully logged {} for your current experiment". format(monitor))


def _log_pickle(monitor, filename,data , mode ='write'):
	if mode =='write':
		with open(filename, 'wb') as f:
			pickled = pickle.dumps(data)
			optimized_pickle = pickletools.optimize(pickled)
			f.write(optimized_pickle)
			console.print("Successfully logged {} for your current loop at {}". format(monitor,filename))
	elif mode =='read':
		selected = client.read(backend_config.BUCKET_NAME, object_key=filename, file_format="pickle")
		_log_pickle(monitor, filename,selected , mode ='write')

	else:
		raise ValueError("Invalid read/write mode set")

def load_pickle(filename):
	pickle_file = pickle.load(open(filename,'rb'))
	return pickle_file

def _remap_outs(data):
	experiment_dir = os.path.join(backend_config.PROJECT_ID,backend_config.EXPERIMENT_ID)
	project_dir = os.path.join(backend_config.PROJECT_ID)
	experiment_meta = json.load(open(os.path.join(project_dir, 'meta.json'),'rb'))  # loopwise meta in future


	selected_file = load_pickle(os.path.join(experiment_dir, 'selected_indices_{}.pkl'.format(backend_config.CUR_LOOP)))
	print("selected_file" , selected_file)

	unselected = sorted(list(set(experiment_meta) - set(selected_file)))

	# Remap to absolute indices
	remap_outputs = {}
	for i, (k, v) in enumerate(data.items()):
		ix = unselected.pop(0)
		remap_outputs[ix] = v
	return remap_outputs




def _sweep_experiment(monitor, filename):
	if not os.path.isfile(filename):
		raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
	

	experiment_dir = os.path.join(backend_config.PROJECT_ID,backend_config.EXPERIMENT_ID)
	project_dir = os.path.join(backend_config.PROJECT_ID)

	for f in os.listdir(project_dir):
		if "meta" not in f:
			client.multi_part_upload_file(os.path.join(project_dir,f), backend_config.BUCKET_NAME, os.path.join(project_dir,f))


	for f in os.listdir(experiment_dir):
		if "meta" not in f:
			client.multi_part_upload_file(os.path.join(experiment_dir,f), backend_config.BUCKET_NAME, os.path.join(experiment_dir,f))











