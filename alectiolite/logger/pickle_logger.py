import os
import json
import boto3
import pickle


__all__ = ["ALPickleOps"]


class ALPickleOps(object):
    def __init__(self, backend_config):
        self.backend_config = backend_config

    def experiment_pickle_logger(self, monitor, data, config):
        """
        Used by users to log experiment level logs
        #TODO replace/adapt with framework based callbacks

        """

        if monitor == "datasetstate" and self.backend_config.CUR_LOOP == "":
            filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "data_map.pkl")
            self._log_pickle(monitor, filename, data)
        elif monitor == "datasetstate" and self.backend_config.CUR_LOOP >= 0:
            filename = os.path.join(
                self.backend_config.EXPERIMENT_DIR,
                "data_map_{}.pkl".format(self.backend_config.CUR_LOOP),
            )
            self._log_pickle(monitor, filename, data)

        elif (
            monitor == "meta"
        ):  # TODO when streaming is available people may add classes on the fly
            filename = os.path.join(self.backend_config.PROJECT_DIR, "meta.json")
            self._log_json(monitor, filename, data)
        elif monitor == "selected_indices" and self.backend_config.CUR_LOOP == "":
            filename = os.path.join(
                self.backend_config.EXPERIMENT_DIR, "selected_indices.pkl"
            )
            self._log_pickle(monitor, filename, data, mode="read")
        elif monitor == "selected_indices" and self.backend_config.CUR_LOOP >= 0:
            for loop in range(int(self.backend_config.CUR_LOOP) + 1):
                filename = os.path.join(
                    self.backend_config.EXPERIMENT_DIR,
                    "selected_indices_{}.pkl".format(loop),
                )
                self._log_pickle(monitor, filename, data, mode="read")
        elif monitor == "logits" and self.backend_config.CUR_LOOP == "":
            filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "logits.pkl")
            self._remap_outs(data)
            self._log_pickle(monitor, filename, data)
            self._sweep_experiment(monitor, filename)
        elif monitor == "logits" and self.backend_config.CUR_LOOP >= 0:
            filename = os.path.join(
                self.backend_config.EXPERIMENT_DIR,
                "logits_{}.pkl".format(self.backend_config.CUR_LOOP),
            )
            remapped_data = _remap_outs(data)
            log_data = {}
            for k, v in remapped_data.items():
                log_data[k] = {monitor: v}
            self._log_pickle(monitor, filename, log_data)
            self._sweep_experiment(monitor, filename)

        else:
            raise ValueError(
                "Invalid experiment loop and/or monitor value chosen to monitor"
            )

    def _log_pickle(self, monitor, filename, data, mode="write"):
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
                self.backend_config.BUCKET_NAME,
                object_key=filename,
                file_format="pickle",
            )
            _log_pickle(monitor, filename, selected, mode="write")

        else:
            raise ValueError("Invalid read/write mode set")

    def _log_json(self, monitor, filename, data):
        # Usually read
        bucket = boto3.resource("s3").Bucket(self.backend_config.BUCKET_NAME)
        json_load_s3 = lambda f: json.load(bucket.Object(key=f).get()["Body"])
        meta_data = json_load_s3(filename)
        with open(filename, "w") as f:
            json.dump(meta_data, f)

    def _remap_outs(self, data):
        experiment_meta = json.load(
            open(os.path.join(self.backend_config.PROJECT_DIR, "meta.json"), "rb")
        )  # loopwise meta in future
        train_size = list(range(experiment_meta["train_size"]))

        selected_file = load_pickle(
            os.path.join(
                self.backend_config.EXPERIMENT_DIR,
                "selected_indices_{}.pkl".format(self.backend_config.CUR_LOOP),
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

    def _sweep_experiment(self, monitor, filename):
        if not os.path.isfile(filename):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        for f in os.listdir(self.backend_config.PROJECT_DIR):
            if "meta" not in f:
                if not os.path.isdir(os.path.join(self.backend_config.PROJECT_DIR, f)):
                    client.multi_part_upload_file(
                        os.path.join(self.backend_config.PROJECT_DIR, f),
                        self.backend_config.BUCKET_NAME,
                        os.path.join(self.backend_config.PROJECT_DIR, f),
                    )

        for f in os.listdir(self.backend_config.EXPERIMENT_DIR):
            if "meta" not in f:
                if not os.path.isdir(
                    os.path.join(self.backend_config.EXPERIMENT_DIR, f)
                ):
                    client.multi_part_upload_file(
                        os.path.join(self.backend_config.EXPERIMENT_DIR, f),
                        self.backend_config.BUCKET_NAME,
                        os.path.join(self.backend_config.EXPERIMENT_DIR, f),
                    )

    def load_pickle(self, filename):
        pickle_file = pickle.load(open(filename, "rb"))
        return pickle_file
