import abc


class AlectioCallback(abc.ABC):
    def on_project_start(self, monitor, data, config):
        pass

    def on_experiment_start(self, monitor, data, config):
        pass

    def on_train_start(self, monitor, data, config):
        pass

    def on_train_end(self, monitor, data, config):
        pass

    def on_test_start(self, monitor, data, config):
        pass
    def on_test_end(self, monitor, data, config):
        pass

    def on_infer_start(self, monitor, data, config):
        pass

    def on_infer_end(self):
        pass

    def on_experiment_end(self):
        pass
