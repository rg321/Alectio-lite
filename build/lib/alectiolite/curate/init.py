import os
from ..backend.backend_server import BackendServer
from ..backend.s3_client import S3Client



"""
status :Fetched
experiment_id :7015f0b057ad11ebb2e55669c5c150e4
project_id :d62080fe56fa11ebb4815669c5c150e4
cur_loop :0
user_id :d04c7b549f8211ea8af9a20dd2e36662
bucket_name :alectio-demo
type :Image Classification
n_rec :2000.0
n_loop :10.0
"""



__all__ = ['init_classification']

class init_classification:
    def __init__(self,token):
        self.token = token
        self.payload = self._token_controller(token)
        self._experiment_controller()


    @property
    def config(self):
        print("Getting value...")
        return self.payload

    @config.setter
    def config(self, value):
        self.payload = value
    
    def _token_controller(self, token):
        backend = BackendServer(token)
        exp_info = backend.init_backend()
        return exp_info


    def _experiment_controller(self):
    	if bool(self.payload):
    		self.status = self.payload.get('status')
    		self.experiment_id = self.payload.get('experiment_id')
    		self.project_id = self.payload.get('project_id')
    		self.cur_loop = self.payload.get('cur_loop')
    		self.user_id = self.payload.get('user_id')
    		self.bucket_name = self.payload.get('bucket_name')
    		self.type = self.payload.get('type')
    		self.n_rec = self.payload.get('n_rec')
    		self.n_loop = self.payload.get('n_loop')
    	else:
    		raise ValueError("No valid experiment details found for current experiment token, please check your token or try again")

    	if 'classification' not in self.type.lower():
    		raise ValueError("The token seems to be incorrect for the experiment type you are trying to run")

    	self.expt_dir = os.path.join(self.user_id, self.project_id, self.experiment_id)























   