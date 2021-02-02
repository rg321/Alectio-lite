from __future__ import print_function

import grpc

import os
import time
import logging
from tqdm import tqdm
from tqdm import trange
from rich.console import Console
from rich.table import Table

# import bidirectional_pb2_grpc as bidirectional_pb2_grpc
# from .bidirectional_pb2_grpc import Bidirectional, BidirectionalStub , BidirectionalServicer
# import alectiolite.bidirectional_pb2 as bidirectional_pb2

import alectiolite.proto.bidirectional_pb2_grpc as bidirectional_pb2_grpc
import alectiolite.proto.bidirectional_pb2 as bidirectional_pb2


__all__ = [
    "BackendServer",
]


GRPCBACKEND = "50.112.116.244:50051"
console = Console(style="bold yellow")


class BackendServer(object):
    def __init__(self, token):
        logging.info("Triggering Alectio jobs with your experiment token ", token)
        self.token = token

    def make_start_exp_payload(self):
        yield bidirectional_pb2.StartExperiment(exp_token=self.token)

    def make_sdk_response_payload(self):
        yield bidirectional_pb2.GetExperimentResponse(exp_token=self.token)

    def startExperiment(self):
        # project_id = request.get_json()['project_id']
        # user_id = request.get_json()['user_id']
        # experiment_id = request.get_json()['experiment_id']
        with grpc.insecure_channel("50.112.116.244:50051") as channel:
            stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
            responses = stub.GetStartExperimentResponse(self.make_start_exp_payload())
            for response in responses:
                return response.exp_token

    def getSDKResponse(self):
        with grpc.insecure_channel("50.112.116.244:50051") as channel:
            stub = bidirectional_pb2_grpc.BidirectionalStub(channel)
            responses = stub.GetSDKResponse(self.make_sdk_response_payload())
            response_obj = next(responses)
            response = {
                "status": response_obj.status,
                "experiment_id": response_obj.experiment_id,
                "project_id": response_obj.project_id,
                "cur_loop": response_obj.cur_loop,
                "user_id": response_obj.user_id,
                "bucket_name": response_obj.bucket_name,
                "type": response_obj.type,
                "n_rec": response_obj.n_rec,
                "n_loop": response_obj.n_loop,
            }
            return response

    def init_backend(self, verbose=False):
        try:
            experimentResponse = self.startExperiment()
            logging.info("Your experiment status :", experimentResponse)
            if experimentResponse != "Started":
                logging.info("Task failed ... ")
                raise ValueError("Experiment couldnot be started . Token invalid")
        except ValueError as e:
            exit(str(e))

        logging.info("Triggering task ....")
        self.payload = self._triggertask()
        if verbose:
            self._printexperimentinfo(self.payload)

        return self.payload

    def _printexperimentinfo(self, payload):

        table = Table(show_header=True, header_style="bold magenta")
        console.print("\n")
        console.print("Details of your experiment ... ")
        rowstrings = ""

        for k, v in payload.items():
            table.add_column(str(k), justify="center")
            rowstrings + str(v) + ","

        table.add_row(rowstrings)
        console.print(table)

    def _triggertask(self):
        currtime = 0
        waittime = 40  # wait time approximately 10 minutes
        ping_server = ["Request {}".format(n) for n in range(waittime)]

        with console.status("[bold green] Triggering Alectio servers ...") as status:
            while True:
                # Calling Backend Servers
                response_child = self.getSDKResponse()
                if response_child["status"] == "Fetched":
                    ping = ping_server.pop(0)
                    console.print("{} succeeded".format(ping))
                    console.print(
                        "Setting up curation , hold tight while we crunch some numbers"
                    )
                    return response_child
                if response_child["status"] == "Failed":
                    ping = ping_server.pop(0)
                    time.sleep(10)
                    console.print("{} failed. Retrying ...".format(ping))
                if not ping_server:
                    console.print("Sorry out servers are offline, try again later !")
