import alectiolite
from alectiolite.callbacks import AlectioCallback


class CurateCallback(AlectioCallback):

	def on_project_start(self,monitor ,data ,config):
		# Alectio controlled
		# Override only if you need to under your circumstance
		alectiolite.experiment_logger(monitor= monitor,
			                       data   = None,
			                       config = config)

	def on_experiment_start(self,monitor ,data ,config):
		alectiolite.experiment_logger(monitor= monitor,
			                      data   = data,
			                      config = config)

	def on_train_start(self, monitor ,data ,config):
		# Alectio controlled
		# Override only if you need to under your circumstance
		alectiolite.experiment_logger(monitor= monitor,
			                          data   = None,
			                          config = config)

	def on_infer_end(self, monitor ,data ,config):

		alectiolite.experiment_logger(monitor= monitor,
			                      data   = data,
			                      config = config)

		



