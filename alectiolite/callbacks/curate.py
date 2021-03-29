import alectiolite
import duckdb
from rich.console import Console
from alectiolite.callbacks import AlectioCallback


class CurateCallback(AlectioCallback):
    def __init__(self):
        self.alectio_database = duckdb.connect(database=":memory:", read_only=False)

    def on_project_start(self, monitor, data, config):
        # Alectio controlled
        # Override only if you need to under your circumstance
        alectiolite.LoggerController(
            monitor=monitor, data=None, config=config, alectio_db=self.alectio_database
        )

    def on_experiment_start(self, monitor, data, config):
        alectiolite.LoggerController(
            monitor=monitor, data=data, config=config, alectio_db=self.alectio_database
        )

    def on_train_start(self, monitor, data, config):
        # Alectio controlled
        # Override only if you need to under your circumstance
        alectiolite.LoggerController(
            monitor=monitor, data=None, config=config, alectio_db=self.alectio_database
        )


    def on_train_end(self, monitor, data, config):
        alectiolite.LoggerController(
            monitor=monitor, data=data, config=config, alectio_db=self.alectio_database
        )


    def on_test_start(self, monitor, data, config):
        # Alectio controlled
        # Override only if you need to under your circumstance
        alectiolite.LoggerController(
            monitor=monitor, data=None, config=config, alectio_db=self.alectio_database
        )


    def on_test_end(self, monitor, data, config):
        alectiolite.LoggerController(
            monitor=monitor, data=data, config=config, alectio_db=self.alectio_database
        )

    def on_infer_start(self, monitor, data, config):
        alectiolite.LoggerController(
            monitor=monitor, data=data, config=config, alectio_db=self.alectio_database
        )


    def on_infer_end(self, monitor, data, config):

        alectiolite.LoggerController(
            monitor=monitor, data=data, config=config, alectio_db=self.alectio_database
        )

    def on_experiment_end(self, token):
        alectiolite.complete_loop(alectio_db = self.alectio_database ,token=token)
