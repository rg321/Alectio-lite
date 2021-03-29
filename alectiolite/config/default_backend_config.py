from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
from yacs.config import CfgNode as CN

_C = CN()

# Backend configs
_C.SANDBOX_BUCKET = ""
_C.BACKEND_IP = "prod-sdk.api.alectio.com"
# _C.BACKEND_IP = "sdk.api.internalalectio.com"
_C.GRPC_BACKEND = "sdk-stream.api.alectio.com"
_C.BACKEND_ROUTE = "127.0.0.1:5000/end_of_task"
_C.PORT = 80

# Experiment configs
_C.STATUS = ""
_C.EXPERIMENT_ID = ""
_C.PROJECT_ID = ""
_C.CUR_LOOP = 0
_C.USER_ID = ""
_C.BUCKET_NAME = ""
_C.TYPE = ""
_C.N_REC = 0.0
_C.N_LOOP = 0.0


# File configs
_C.OUTFILES = (
    "metrics",
    "train_predictions",
    "train_ground_truth",
    "test_predictions",
    "test_ground_truth",
    "datasetstate",
    "logits",
    "boxes"
    "endloop",
)
_C.INFILES = ("meta", "labeled_pool", "selected_indices")
_C.OUT_FORMAT = "parquet"
_C.DB_INIT = False

# Log directories
_C.EXPERIMENT_DIR = ""
_C.PROJECT_DIR = ""


def update_backend_config(cfg, include_cfg):
    cfg.defrost()
    cfg.merge_from_list(include_cfg)
    cfg.freeze()


if __name__ == "__main__":
    import sys

    with open(sys.argv[1], "w") as f:
        print(_C, file=f)
