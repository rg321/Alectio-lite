import abc


class AlectioCallback(abc.ABC):

    """
    Alectio base callback class
    ...
    
    Methods
    -------
    on_project_start(monitor, data, config)
        Used to log meta data on project start
    on_experiment_start(monitor, data, config)
        Used to log meta data on experiment start
    on_train_start(monitor, data, config)
        Used to log meta data on the start of training your model
    on_train_end(monitor, data, config)
        Used to log meta data at the end of training your model
    on_test_start(monitor, data, config)
        Used to log meta data at the start of testing your model
    on_test_end(monitor, data, config)
        Used to log meta data at the end of testing your model
    on_infer_start(monitor, data, config)
        Used to log meta data at the start of inferring your model
    on_infer_end()
        Used to log meta data at the end of inferring your model
    on_experiment_end()
        Used to log meta data at the end of each alectio experiment

    """
    def on_project_start(self, monitor, data, config):
        """
        The on_project_start function sets up Alectio's backend for you to 
        run your experiments. In most cases 

        Parameters
        ----------
        monitor : str
            ("meta")            
        data : dict
            optional, defaults to None
        config :


        Returns
        -------
        bool
            Description of return value

        """
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
