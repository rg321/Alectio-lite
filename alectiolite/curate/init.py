import os
from ..backend.s3_client import S3Client

from ..config import backend_config
from ..config import update_backend_config

from rich.table import Table
from rich.console import Console

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


__all__ = ["init_classification"]
console = Console(style="green")


class init_classification:
    def __init__(self, config):
        self.payload = config
        self._experiment_controller()

    @property
    def config(self):
        console.print("Getting value...")
        return self.payload

    @config.setter
    def config(self, value):
        self.payload = value

    def _update_experiment_config(self):
        cfglist = []
        for k, v in self.payload.items():
            cfglist.extend([str(k).upper(), v])
        update_backend_config(backend_config, cfglist)
        self.experiment_config = backend_config  #### Gets updated for each experiment whenever a call is made to the API

    def _checkdirs(self, dir_, kind=""):
        if not os.path.exists(dir_):
            os.makedirs(dir_, exist_ok=True)
            console.print(
                "All Alectio {} logs will be saved to {}".format(
                    kind, self.experiment_config.EXPERIMENT_ID
                )
            )

    def _experiment_controller(self):
        if bool(self.payload):
            self._update_experiment_config()
        else:
            raise ValueError(
                "No valid experiment details found for current experiment token, please check your token or try again"
            )
        if "classification" not in self.experiment_config.TYPE.lower():
            raise ValueError(
                "The token seems to be incorrect for the experiment type you are trying to run"
            )

        self.experiment_log_dir = self.experiment_config.EXPERIMENT_ID

        # TO DO : A better solution for buckets , API in works
        if self.experiment_config.BUCKET_NAME == self.experiment_config.SANDBOX_BUCKET:
            self.experiment_dir = os.path.join(
                self.experiment_config.USER_ID,
                self.experiment_config.PROJECT_ID,
                self.experiment_config.EXPERIMENT_ID,
            )
            self._checkdirs(self.experiment_dir, "experiment")
            self.project_dir = os.path.join(
                self.experiment_config.USER_ID, self.experiment_config.PROJECT_ID
            )
            self._checkdirs(self.project_dir, "project")

        else:
            self.experiment_dir = os.path.join(
                self.experiment_config.PROJECT_ID, self.experiment_config.EXPERIMENT_ID
            )
            self._checkdirs(self.experiment_dir, "experiment")
            self.project_dir = os.path.join(self.experiment_config.PROJECT_ID)
            self._checkdirs(self.project_dir, "project")
