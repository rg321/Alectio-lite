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
        The on_project_start callback function sets up Alectio's backend for you to 
        run your project. In most cases you donot have to use this. DONOT use this
        unless you explicitly want to use this in your project

        Parameters
        ----------
        monitor : str
            ("meta")            
        data : dict
            optional, defaults to None
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value        

        """
        pass

    def on_experiment_start(self, monitor, data, config):

        """
        The on_experiment_start callback function is used to log your entire dataset
        as index to reference filename/identifier pairs. This will be used by 
        Alectio to reference your data when your data is hosted on premise 

        Parameters
        ----------
        monitor : str
            ("datasetstate")            
        data : dict
            key, value pairs of unique index mapping to each record name/id that you want to curate
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know what dataset you are trying to curate. To log dataset state as 
        a dictionary refer below
        >>> from alectiolite.callbacks import CurateCallback
        >>> cb = CurateCallback()
        >>> dataset_size = 120000
        >>> dataset_state = {ix: n for ix, n in enumerate(range(dataset_size))}
        >>> cb.on_experiment_start(monitor="datasetstate", data=datasetstate, config=config)   

        """
        pass

    def on_train_start(self, monitor, data, config):
        """
        The on_train_start callback function is used to log train statistics at the beginning of each train loop

        Parameters
        ----------
        monitor : str
            ("")            
        data : dict
            key, value pairs of unique index mapping to
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know what dataset you are trying to curate. To log dataset state as 
        a dictionary refer below
        
        >>> cb.on_train_start(monitor="", data= , config=config)   

        """
        pass

    def on_train_end(self, monitor, data, config):
        """
        The on_train_end callback function is used to log train statistics at the end of each train loop

        Parameters
        ----------
        monitor : str
            ("")            
        data : dict
            key, value pairs of unique index mapping to
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know what dataset you are trying to curate. To log dataset state as 
        a dictionary refer below
        
        >>> cb.on_experiment_start(monitor="datasetstate", data=datasetstate, config=config)   

        """
        pass

    def on_test_start(self, monitor, data, config):
        pass
    def on_test_end(self, monitor, data, config):
        pass

    def on_infer_start(self, monitor, data, config):
        """
        The on_infer_start callback function is used to log inference statistics at the beginning of each inference loop

        Parameters
        ----------
        monitor : str
            ("")            
        data : dict
            key, value pairs of unique index mapping to
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know what dataset you are trying to curate. To log dataset state as 
        a dictionary refer below
        
        >>> cb.on_infer_start(monitor="datasetstate", data=datasetstate, config=config)   

        """
        pass

    def on_infer_end(self, monitor, data, config):
        """
        The on_infer_end callback function is used to log inference statistics at the end of each inference loop

        Parameters
        ----------
        monitor : str
            ("")            
        data : dict
            key, value pairs of unique index mapping to
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know what dataset you are trying to curate. To log dataset state as 
        a dictionary refer below
        >>> infer_outs = infer(unlabeled_pool)
        >>> cb.on_infer_end(monitor="pre_softmax", data=infer_outs, config=config)

        """
        pass

    def on_experiment_end(self, token):
        """
        The on_experiment_end callback function is used to mark an experiment loop as complete status

        Parameters
        ----------
        monitor : str
            ("")            
        data : dict
            key, value pairs of unique index mapping to
        config : dict
            default configs for your experiment , use alectiolite.experiment_config(token=TOKEN) to get this value

        Examples
        --------

        At each incremental loop Alectio needs to know when you completed a particular loop
        >>> cb.on_experiment_end(token= TOKEN)

        """
        pass
