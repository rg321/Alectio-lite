"""Functional interface"""


import os
import time
import logging
from tqdm import tqdm
from tqdm import trange
from ..backend.s3_client import S3Client
from alectiolite.curate.init import init_classification
from alectiolite.callbacks import DefaultCallback


class operations(DefaultCallback):
    def on_experiment_start():




__all__ = ['UniClassification']




class UniClassification(init_classification):
    """
    A class that consumes and preprocesse's model's logits
    ...
    Attributes
    ----------
    token : str
        Unique token string given for each Active learning experiment
    infer_outputs : dict
        Logit outputs of your model
        
    Methods
    -------
    _printexperimentinfo(payload):
        Prints the payload information of each triggered experiment
    
    _triggertask():
        Triggers an experiment 
    """
    def __init__(self, token , subset = None , callbacks = None , verbose =True, activation = None):
        logging.info('Triggering Alectio jobs to perform curation experiments ')
        logging.info('Sweeping configs')
        super().__init__(token)
        if callbacks is None:
            self.callbacks = []
        else:
            self.callbacks = callbacks
        self.verbose = verbose
        self.subset = subset

        self.client = S3Client()

        self.fit()
   
        
    def _printexperimentinfo(self, payload):
        print('\n')
        print('Details of your experiment ... ')
        for k , v in payload.items():
            print(str(k)+' :'+str(v))


    def fit(self):
        logging.info('Your experiment status :', self.status)
        logging.info('Triggering task ....')
        self.on_experiment_start()  # A Promise
        
        if self.verbose:
            self._printexperimentinfo(self.payload)

        ########### Meta json #############
        key = os.path.join(self.project_dir, "meta.json")
        bucket = boto3.resource("s3").Bucket(self.bucket_name)
        json_load_s3 = lambda f: json.load(bucket.Object(key=f).get()["Body"])
        self.meta_data = json_load_s3(key)

        
        self.on_infer_start()
        #self.on_infer_end()
        

    def on_infer_start(self):

        for cb in self.callbacks:
            self.data_map = cb.on_infer_start()
            object_key = os.path.join(self.expt_dir, "data_map_{}.pkl".format(self.subset))
            self.client.multi_part_upload_with_s3(
                self.data_map, self.bucket_name, object_key, "pickle"
            )











    
    