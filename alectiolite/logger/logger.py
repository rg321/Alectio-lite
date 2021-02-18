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

console = Console(style="green")
client = S3Client()


def _reel_in_configs(config):
    cfglist = []
    for k, v in config.items():
        cfglist.extend([str(k).upper(), v])
    update_backend_config(backend_config, cfglist)


def _checkdirs(dir_, kind="experiment"):
    if not os.path.exists(dir_):
        os.makedirs(dir_, exist_ok=True)
        console.print(
            "All Alectio {} logs will be saved to {}".format(
                kind, backend_config.EXPERIMENT_ID
            )
        )


def _check_monitor(monitor):
    for f in backend_config.OUTFILES:
        if f in monitor:
            return monitor
    for f in backend_config.INFILES:
        if f in monitor:
            return monitor

    raise ValueError("Invalid monitor value {} ".format(monitor))

def _create_log_dirs():
    directory_list = []
    ##setup logdirs
    # TO DO : A better solution for buckets , API in works
    if backend_config.BUCKET_NAME == backend_config.SANDBOX_BUCKET:
        experiment_dir = os.path.join(
            backend_config.USER_ID,
            backend_config.PROJECT_ID,
            backend_config.EXPERIMENT_ID,
        )
        directory_list.extend(["experiment_dir".upper(),experiment_dir])
        project_dir = os.path.join(backend_config.USER_ID, backend_config.PROJECT_ID)
        directory_list.extend(["project_dir".upper(),project_dir])
        
    else:
        experiment_dir = os.path.join(
            backend_config.PROJECT_ID, backend_config.EXPERIMENT_ID
        )
        directory_list.extend(["experiment_dir".upper(),experiment_dir])
        project_dir = os.path.join(backend_config.PROJECT_ID)
        directory_list.extend(["project_dir".upper(),project_dir])

    update_backend_config(backend_config, directory_list)
    _checkdirs(experiment_dir, "experiment")



def experiment_logger(monitor, data, config , format = 'pickle'):
    if format =='pickle':
        experiment_pickle_logger(monitor, data, config)
    elif format == 'parquet':
        experiment_db_logger(monitor, data, config)




def experiment_pickle_logger(monitor, data, config):
    """
    Used by users to log experiment level logs
    #TODO replace/adapt with framework based callbacks

    """
    _reel_in_configs(config)
    _check_monitor(monitor)
    _create_log_dirs()
    
    if monitor == "datasetstate" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "data_map.pkl")
        _log_pickle(monitor, filename, data)
    elif monitor == "datasetstate" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "data_map_{}.pkl".format(backend_config.CUR_LOOP)
        )
        _log_pickle(monitor, filename, data)

    elif (
        monitor == "meta"
    ):  # TODO when streaming is available people may add classes on the fly
        filename = os.path.join(backend_config.PROJECT_DIR, "meta.json")
        _log_json(monitor, filename, data)
    elif monitor == "selected_indices" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "selected_indices.pkl")
        _log_pickle(monitor, filename, data, mode="read")
    elif monitor == "selected_indices" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "selected_indices_{}.pkl".format(backend_config.CUR_LOOP)
        )
        _log_pickle(monitor, filename, data, mode="read")
    elif monitor == "logits" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "logits.pkl")
        _remap_outs(data)
        _log_pickle(monitor, filename, data)
        _sweep_experiment(monitor, filename)
    elif monitor == "logits" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "logits_{}.pkl".format(backend_config.CUR_LOOP)
        )
        remapped_data = _remap_outs(data)
        log_data = {}
        for k ,v in remapped_data.items():
            log_data[k] = {monitor:v}
        _log_pickle(monitor, filename, log_data)
        _sweep_experiment(monitor, filename)

    else:
        raise ValueError(
            "Invalid experiment loop and/or monitor value chosen to monitor"
        )




def experiment_db_logger(monitor, data, config):
    """
    Used by users to log experiment level logs
    #TODO replace/adapt with framework based callbacks

    """
    _reel_in_configs(config)
    _check_monitor(monitor)
    _create_log_dirs()
    
    if monitor == "datasetstate" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "data_map.pkl")
        _log_pickle(monitor, filename, data)
    elif monitor == "datasetstate" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "data_map_{}.pkl".format(backend_config.CUR_LOOP)
        )
        _log_pickle(monitor, filename, data)

    elif (
        monitor == "meta"
    ):  # TODO when streaming is available people may add classes on the fly
        filename = os.path.join(backend_config.PROJECT_DIR, "meta.json")
        _log_json(monitor, filename, data)
    elif monitor == "selected_indices" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "selected_indices.pkl")
        _log_pickle(monitor, filename, data, mode="read")
    elif monitor == "selected_indices" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "selected_indices_{}.pkl".format(backend_config.CUR_LOOP)
        )
        _log_pickle(monitor, filename, data, mode="read")
    elif monitor == "pre_softmax" and backend_config.CUR_LOOP == "":
        filename = os.path.join(backend_config.EXPERIMENT_DIR, "pre_softmax.pkl")
        _remap_outs(data)
        _log_pickle(monitor, filename, data)
        _sweep_experiment(monitor, filename)
    elif monitor == "pre_softmax" and backend_config.CUR_LOOP >= 0:
        filename = os.path.join(
            backend_config.EXPERIMENT_DIR, "pre_softmax_{}.pkl".format(backend_config.CUR_LOOP)
        )
        remapped_data = _remap_outs(data)
        _log_pickle(monitor, filename, remapped_data)
        _sweep_experiment(monitor, filename)

    else:
        raise ValueError(
            "Invalid experiment loop and/or monitor value chosen to monitor"
        )




def _log_json(monitor, filename, data):
    # Usually read
    bucket = boto3.resource("s3").Bucket(backend_config.BUCKET_NAME)
    json_load_s3 = lambda f: json.load(bucket.Object(key=f).get()["Body"])
    meta_data = json_load_s3(filename)
    with open(filename, "w") as f:
        json.dump(meta_data, f)

    console.print("Successfully logged {} for your current experiment".format(monitor))


def _log_pickle(monitor, filename, data, mode="write"):
    if mode == "write":
        with open(filename, "wb") as f:
            pickled = pickle.dumps(data)
            optimized_pickle = pickletools.optimize(pickled)
            f.write(optimized_pickle)
            console.print(
                "Successfully logged {} for your current loop at {}".format(
                    monitor, filename
                )
            )
    elif mode == "read":
        selected = client.read(
            backend_config.BUCKET_NAME, object_key=filename, file_format="pickle"
        )
        _log_pickle(monitor, filename, selected, mode="write")

    else:
        raise ValueError("Invalid read/write mode set")


def load_pickle(filename):
    pickle_file = pickle.load(open(filename, "rb"))
    return pickle_file


def _remap_outs(data):
    experiment_meta = json.load(
        open(os.path.join(backend_config.PROJECT_DIR, "meta.json"), "rb")
    )  # loopwise meta in future
    train_size = list(range(experiment_meta["train_size"]))

    selected_file = load_pickle(
        os.path.join(
            backend_config.EXPERIMENT_DIR, "selected_indices_{}.pkl".format(backend_config.CUR_LOOP)
        )
    )
    # print("selected_file" , selected_file)

    unselected = sorted(list(set(train_size) - set(selected_file)))

    # Remap to absolute indices
    remap_outputs = {}
    for i, (k, v) in enumerate(data.items()):
        ix = unselected.pop(0)
        remap_outputs[ix] = v
    return remap_outputs


def _sweep_experiment(monitor, filename):
    if not os.path.isfile(filename):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

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



def complete_loop(token):
    url = "".join(["http://", backend_config.BACKEND_IP, ":{}".format(backend_config.PORT), "/end_of_task"])
    headers = {"Authorization": "Bearer " + token}
    #console.print("Backend IP =", backend_config.BACKEND_IP)
    # Step to be skipped after Dev backend change
    returned_payload = {"exp_token": "TOKEN"}
    """
    returned_payload = {'status': backend_config.STATUS, 
                        'experiment_id':backend_config.EXPERIMENT_ID, 
                        'project_id':backend_config.PROJECT_ID, 
                        'cur_loop':backend_config.CUR_LOOP,  
                        'user_id':backend_config.USER_ID, 
                        'bucket_name':backend_config.BUCKET_NAME,  
                        'type':backend_config.TYPE, 
                        'n_rec':backend_config.N_REC,  
                        'n_loop': backend_config.N_LOOP}
    """

    status = requests.post(url=url, json=returned_payload, headers=headers).status_code

    if status == 200:
        console.print("Experiment {} has been triggered .. Requesting Alectio servers to return curation results ... ".format(backend_config.EXPERIMENT_ID))
        #Need better solution
        check_file = "selected_indices_{}.pkl".format(int(backend_config.CUR_LOOP)+1)
        object_key = os.path.join(backend_config.EXPERIMENT_DIR , check_file)
        waittime = 40  # wait time approximately 10 minutes
        ping_server = ["Request {}".format(n) for n in range(waittime)]

        while True:
            #Looks for selected indices in the bucket
            ping = ping_server.pop(0)
            experiment_status = client.check_file_exists(backend_config.BUCKET_NAME, object_key=object_key)
            if experiment_status == "Failed":
                console.print("Unable to fetch current indices ! your experiment failed due to difficulties in connecting to the cloud servers!")
                return
            elif experiment_status == "Complete":
                console.print("Experiment complete ! Time to pull your curated list of records that you should label before training again ")
                return

            if not ping_server:
                console.print("Sorry our servers are currently busy, please check back again later for your curated list !")
                break
            console.print("{} Complete, this may take some time ....".format(ping))
            time.sleep(25)
            
    else:
        console.print("Request timed out , unable to fetch current indices ! Alectio servers seem to be offline")

