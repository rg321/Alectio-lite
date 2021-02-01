"""Functional interface"""


import os
import time
import json
import boto3
import pickle
import logging
from rich.table import Table
from rich.console import Console
from ..backend.s3_client import S3Client
from alectiolite.curate.init import init_classification
from alectiolite.callbacks import CurateCallback


"""
class operations(DefaultCallback):
    def on_experiment_start():


"""

__all__ = ['UniClassification']
console = Console(style ="green")

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
    def __init__(self, config , subset = None , callbacks = None , verbose =True, activation = None):
        logging.info('Triggering Alectio jobs to perform curation experiments ')
        logging.info('Sweeping configs')
        super().__init__(config)
        self.payload = config
        if callbacks is None:
            self.callbacks = []
        else:
            self.callbacks = callbacks
        self.verbose = verbose
        self.subset = subset

        self.client = S3Client()

        self.fit()
   
        
    def _printexperimentinfo(self, payload):
        #console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        console.print('\n')
        console.print('Details of your experiment ... ')
        row_values = []
        
        for k , v in payload.items():
            table.add_column(str(k), justify ="center")
            row_values.append(str(v))

        table.add_row(row_values[0],row_values[1],row_values[2],row_values[3],row_values[4],row_values[5],row_values[6],row_values[7],row_values[8])
        console.print(table)


    def fit(self):
        logging.info('Your experiment status :', self.experiment_config.STATUS)
        logging.info('Triggering task ....')
             
        if self.verbose:
            self._printexperimentinfo(self.payload)

        ##### Call necessary deterministic callbacks
        for cb in self.callbacks:
            cb.on_project_start(monitor= "meta",
                                data = None,
                                config = self.config)
            cb.on_train_start(monitor= "selected_indices",
                              data = None,
                              config = self.config)

        if self.experiment_config.CUR_LOOP =='':
            self.selected_file = os.path.join(self.experiment_dir, 'selected_indices.pkl')
        elif self.experiment_config.CUR_LOOP >= 0:
            self.selected_file = os.path.join(self.experiment_dir, 'selected_indices_{}.pkl'.format(self.experiment_config.CUR_LOOP))
        else:
            raise ValueError("Invalid experiment loop value chosen to monitor / you must pass previous loops output to Alectio for this operatio")





        #selected = self._read_pickle(selected_file)

        #return selected

        
        #self.on_infer_start()
        #self.on_infer_end()
        

    def on_infer_start(self):
        pass
        """


        for cb in self.callbacks:
            cb.on_infer_start()
            
            object_key = os.path.join(self.experiment_dir, "data_map_{}.pkl".format(self.subset))
            self.client.multi_part_upload_with_s3(
                self.data_map, self.experiment_config.BUCKET_NAME, object_key, "pickle"
            )
        """











    
    