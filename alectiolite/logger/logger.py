import os
import json
import time
import errno
import boto3
import pickle
import duckdb
import requests
import pickletools
from rich.table import Table
from rich.console import Console
from ..config import backend_config
from ..config import update_backend_config
from ..backend.s3_client import S3Client
from .db_logger import ALDatabaseOps
from .pickle_logger import ALPickleOps

console = Console(style="green")
client = S3Client()

__all__ = ["LoggerController"]


class LoggerController(object):
    def __init__(self, monitor, data, config, alectio_db =None):
        if alectio_db:
            console.print(" Logging through a database")

        else:
            console.print(
                " Logging through pickle, Youre in a pickle if your dataset is large !"
            )
        self.experiment_logger(monitor, data, config,alectio_db)
        

    def _setup_logger(self,monitor,config):
        console.print("Getting ready to log your data")
        self._reel_in_configs(config)
        self._check_monitor(monitor)
        self._create_log_dirs()

    def _reel_in_configs(self, config):
        cfglist = []
        for k, v in config.items():
            cfglist.extend([str(k).upper(), v])
        update_backend_config(backend_config, cfglist)

    def _checkdirs(self, dir_, kind="experiment"):
        if not os.path.exists(dir_):
            os.makedirs(dir_, exist_ok=True)
            console.print(
                "All Alectio {} logs will be saved to {}".format(
                    kind, backend_config.EXPERIMENT_ID
                )
            )

    def _check_monitor(self, monitor):
        for f in backend_config.OUTFILES:
            if f in monitor:
                return monitor
        for f in backend_config.INFILES:
            if f in monitor:
                return monitor

        raise ValueError("Invalid monitor value {} ".format(monitor))

    def _create_log_dirs(self):
        directory_list = []
        ##setup logdirs
        # TO DO : A better solution for buckets , API in works
        if backend_config.BUCKET_NAME == backend_config.SANDBOX_BUCKET:
            experiment_dir = os.path.join(
                backend_config.USER_ID,
                backend_config.PROJECT_ID,
                backend_config.EXPERIMENT_ID,
            )
            directory_list.extend(["experiment_dir".upper(), experiment_dir])
            project_dir = os.path.join(
                backend_config.USER_ID, backend_config.PROJECT_ID
            )
            directory_list.extend(["project_dir".upper(), project_dir])

        else:
            experiment_dir = os.path.join(
                backend_config.PROJECT_ID, backend_config.EXPERIMENT_ID
            )
            directory_list.extend(["experiment_dir".upper(), experiment_dir])
            project_dir = os.path.join(backend_config.PROJECT_ID)
            directory_list.extend(["project_dir".upper(), project_dir])

        update_backend_config(backend_config, directory_list)
        self._checkdirs(experiment_dir, "experiment")

    def experiment_logger(self, monitor, data, config, alectio_db):
        self._setup_logger(monitor,config)

        if backend_config.OUT_FORMAT == "pickle":
            console.print(
                " Logging through pickle, Youre in a pickle if your dataset is large !"
            )
            data_log = ALPickleOps(backend_config)
            data_log.experiment_pickle_logger(monitor, data, config)
        elif (
            backend_config.OUT_FORMAT == "parquet" or backend_config.OUT_FORMAT == "csv"
        ):
            console.print(" Logging through a database")
            data_log = ALDatabaseOps(backend_config)
            data_log.experiment_db_logger(monitor, data, config, alectio_db)

        """

        if monitor == "logits":
            self._sweep_experiment()
        """

def _sweep_experiment():

    """
    TO DO : Merge this with complete loop

    """

    for f in os.listdir(backend_config.PROJECT_DIR):
        if "meta" not in f:
            if not os.path.isdir(os.path.join(backend_config.PROJECT_DIR, f)):
                client.multi_part_upload_file(
                    os.path.join(backend_config.PROJECT_DIR, f),
                    backend_config.BUCKET_NAME,
                    os.path.join(backend_config.PROJECT_DIR, f),
                    )

    for f in os.listdir(backend_config.EXPERIMENT_DIR):
        if "meta" not in f:
            if not os.path.isdir(os.path.join(backend_config.EXPERIMENT_DIR, f)):
                client.multi_part_upload_file(
                    os.path.join(backend_config.EXPERIMENT_DIR, f),
                    backend_config.BUCKET_NAME,
                    os.path.join(backend_config.EXPERIMENT_DIR, f),
                    )



def complete_loop(alectio_db , token):
    console.print("Exporting your logs to {}".format(backend_config.EXPERIMENT_DIR))

    if backend_config.OUT_FORMAT =='csv':
        query = "EXPORT DATABASE '{}' (FORMAT CSV, DELIMITER ',')".format(str(backend_config.EXPERIMENT_DIR))
    else:
        query = "EXPORT DATABASE '{}' (FORMAT PARQUET)".format(str(backend_config.EXPERIMENT_DIR))
    alectio_db.execute(query)

    console.print("Exporting complete now transferring logs to the cloud. Hold tight !")

    _sweep_experiment()



    #### Needs to be ported to backend server configs once Backend changes have been made
    url = "".join(
        [
            "http://",
            backend_config.BACKEND_IP,
            ":{}".format(backend_config.PORT),
            "/end_of_task",
        ]
    )
    headers = {"Authorization": "Bearer " + token}
    # console.print("Backend IP =", backend_config.BACKEND_IP)
    # Step to be skipped after Dev backend change

    returned_payload = {"exp_token": token}
    """

    returned_payload = {
        "status": backend_config.STATUS,
        "experiment_id": backend_config.EXPERIMENT_ID,
        "project_id": backend_config.PROJECT_ID,
        "cur_loop": backend_config.CUR_LOOP,
        "user_id": backend_config.USER_ID,
        "bucket_name": backend_config.BUCKET_NAME,
        "type": backend_config.TYPE,
        "n_rec": backend_config.N_REC,
        "n_loop": backend_config.N_LOOP,
    }
    """
    status = requests.post(url=url, json=returned_payload, headers=headers).status_code
    print("The status of next loop = ", status)

    if status == 200:
        console.print(
            "Experiment {} has been triggered .. Requesting Alectio servers to return curation results ... ".format(
                backend_config.EXPERIMENT_ID
            )
        )
        # Need better solution
        check_file = "selected_indices_{}.pkl".format(int(backend_config.CUR_LOOP) + 1)
        object_key = os.path.join(backend_config.EXPERIMENT_DIR, check_file)
        waittime = 40  # wait time approximately 10 minutes
        ping_server = ["Request {}".format(n) for n in range(waittime)]

        while True:
            # Looks for selected indices in the bucket
            ping = ping_server.pop(0)
            experiment_status = client.check_file_exists(
                backend_config.BUCKET_NAME, object_key=object_key
            )
            if experiment_status == "Failed":
                console.print(
                    "Unable to fetch current indices ! your experiment failed due to difficulties in connecting to the cloud servers!"
                )
                return
            elif experiment_status == "Complete":
                console.print(
                    "Experiment complete ! Time to pull your curated list of records that you should label before training again "
                )
                return

            if not ping_server:
                console.print(
                    "Sorry our servers are currently busy, please check back again later for your curated list !"
                )
                break
            console.print("{} Complete, this may take some time ....".format(ping))
            time.sleep(25)

    else:
        console.print(
            "Request timed out , unable to fetch current indices ! Alectio servers seem to be offline"
        )
