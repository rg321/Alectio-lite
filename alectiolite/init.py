import os
from .backend.backend_server import BackendServer



def init_experiment_(token):
    backend = BackendServer(token)
    exp_info = backend.init_backend()
    print("printing payload below")
    return exp_info

#def extract_config(token)




