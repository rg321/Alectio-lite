import abc


class AlectioCallback(abc.ABC):



	def on_infer_start(self):
		pass


	def on_infer_end(self):
		pass