from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import os
from yacs.config import CfgNode as CN

_C = CN()

# Backend configs
_C.SANDBOX_BUCKET = ''
_C.BACKEND_IP =  'prod-sdk.api.alectio.com'
_C.GRPC_BACKEND = 'sdk-stream.api.alectio.com'
_C.BACKEND_ROUTE = '127.0.0.1:5000/end_of_task'

# Experiment configs
_C.STATUS = ''
_C.EXPERIMENT_ID = ''
_C.PROJECT_ID = ''
_C.CUR_LOOP = 0
_C.USER_ID = ''
_C.BUCKET_NAME = ''
_C.TYPE = ''
_C.N_REC = 0.0
_C.N_LOOP = 0.0


# File configs
_C.OUTFILES = ('metrics' ,'test_predictions','datasetstate','pre_softmax')
_C.INFILES = ('meta' , 'labeled_pool' ,'selected_indices')




def update_backend_config(cfg, include_cfg):
    cfg.defrost()
    cfg.merge_from_list(include_cfg)
    cfg.freeze()


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'w') as f:
        print(_C, file=f)

