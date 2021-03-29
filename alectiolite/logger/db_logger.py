import os
import json
import duckdb
import boto3
import numpy as np
import pandas as pd
from ..backend.s3_client import S3Client


__all__ = ["ALDatabaseOps"]

client = S3Client()
from rich.console import Console
console = Console(style="green")


# Note: DB only supports key : value pairs currently
class ALDatabaseOps(object):
	def __init__(self, backend_config , file_format ='parquet'):

		self.backend_config = backend_config
		self.file_format = file_format


	def np_stringify(self, value):
		return np.array2string(value, precision=5, separator=',')


	def _check_conn(self,db_conn):
		if not db_conn:
			raise ConnectionError('Unable to connect to local database !')


	def create_table(self,table_name, db_conn):
		query = "CREATE TABLE IF NOT EXISTS {}(ix INTEGER, val VARCHAR DEFAULT '')".format(table_name)
		db_conn.execute(query)
		db_conn.commit()


	def insert_row(self, table_name , ix , value ,db_conn):
		query = "INSERT INTO {} VALUES (?, ?)".format(table_name)
		db_conn.execute(query,[ix, value])
		db_conn.commit()


	def export_db(self, output_format , db_conn):
		# Only two formats supported in
		if output_format =='csv':
			query = "EXPORT DATABASE '{}' (FORMAT CSV, DELIMITER ',')".format(str(self.backend_config.EXPERIMENT_DIR))
		else:
			query = "EXPORT DATABASE '{}' (FORMAT PARQUET)".format(str(self.backend_config.EXPERIMENT_DIR))
		db_conn.execute(query)


	def update_table(self, table_name, target_table ,db_conn):
		query = "UPDATE {} SET ix = :target_value WHERE ix=:id".format(str(table_name))
		db_conn.executemany(query, target_table)
		db_conn.commit()


	def import_db(self,output_format, db_conn):
		query = "IMPORT DATABASE '{}' ".format(self.backend_config.EXPERIMENT_DIR)
		db_conn.execute(query)
		db_conn.commit()


	def experiment_db_logger(self,monitor, data, config ,alectio_db):
	    """
	    Used by users to log experiment level logs
	    #TODO replace/adapt with framework based callbacks

	    """
	    self._check_conn(alectio_db)
	    if monitor == "datasetstate" and self.backend_config.CUR_LOOP == "":
	        console.print("Setting up database for current loop !")
	        filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "data_map")
	        self._log_duck(monitor, filename, data ,alectio_db , mode ='write')
	        self._log_unlabeled(alectio_db)
	    elif monitor == "datasetstate" and self.backend_config.CUR_LOOP >= 0:
	        filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "data_map_{}".format(self.backend_config.CUR_LOOP))
	        self._log_duck(monitor, filename, data ,alectio_db, mode ='write')
	        self._log_unlabeled(alectio_db)
	    elif (monitor == "meta"):  # TODO when streaming is available people may add classes on the fly
	        filename = os.path.join(self.backend_config.PROJECT_DIR, "meta.json")
	        self._log_json(monitor, filename, data)
	    elif monitor == "selected_indices" and self.backend_config.CUR_LOOP == "": #Not completely fool proof if loop size doesn't exist
	        filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "selected_indices")
	        self._log_duck(monitor, filename, data, db ,mode="read")
	    elif monitor == "selected_indices" and self.backend_config.CUR_LOOP >= 0:
	        for loop in range(int(self.backend_config.CUR_LOOP)+1):
	            filename = os.path.join(
	                self.backend_config.EXPERIMENT_DIR, "selected_indices_{}".format(loop)
	            )
	            self._log_duck(monitor, filename, data,alectio_db, mode="read")

	    elif monitor == "logits" and self.backend_config.CUR_LOOP == "":
	        filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "logits")
	        self._log_duck(monitor, filename, data ,alectio_db, mode ='write')
	        self._remap_outs(data, filename, alectio_db)
	        #self.export_db(self.backend_config.OUT_FORMAT,alectio_db)
	       
	    elif monitor == "logits" and self.backend_config.CUR_LOOP >= 0:
	        filename = os.path.join(
	            self.backend_config.EXPERIMENT_DIR, "logits_{}".format(self.backend_config.CUR_LOOP)
	        )
	        self._log_duck(monitor, filename, data ,alectio_db, mode ='write')
	        #update records 
	        self._remap_outs(data,filename,alectio_db)
	        #self.export_db(self.backend_config.OUT_FORMAT,alectio_db)

	    elif monitor == "boxes" and self.backend_config.CUR_LOOP == "":
	        filename = os.path.join(self.backend_config.EXPERIMENT_DIR, "logits")
	        self._log_duck(monitor, filename, data ,alectio_db, mode ='write')
	        self._remap_outs(data, filename, alectio_db)
	        	       
	    elif monitor == "boxes" and self.backend_config.CUR_LOOP >= 0:
	        filename = os.path.join(
	            self.backend_config.EXPERIMENT_DIR, "boxes_{}".format(self.backend_config.CUR_LOOP)
	        )
	        self._log_duck(monitor, filename, data ,alectio_db, mode ='write')
	        #update records 
	        self._remap_outs(data,filename,alectio_db)	       
	    else:
	        raise ValueError(
	            "Invalid experiment loop and/or monitor value chosen to monitor"
	        )


	def _get_corresponding_ix(self,data,alectio_db):
		query = ""
		table_name = 'unselected_indices_{}'.format(self.backend_config.CUR_LOOP)
		
		for idx , (k, v) in enumerate(data.items()):
			query = query+"SELECT ix FROM {} WHERE rownum={}".format(table_name,k)

			if (idx < (len(data)-1)):
				query = query+" UNION ALL "
			
		alectio_db.execute(query)
		df3 = alectio_db.fetchdf()
		unlabeled_ix =list(df3['ix'])
		return unlabeled_ix


	def _remap_outs(self, data , filename, alectio_db):		
		query = ""
		target_directory , table_name = os.path.split(filename)
		unlabeled_ix = self._get_corresponding_ix(data,alectio_db)
		
		if type(data) ==dict:
			for k, v in data.items():
				curr_ix = unlabeled_ix.pop(0)
				query = query+"UPDATE {} SET ix={} WHERE rowid={};".format(table_name,curr_ix,k)		
		alectio_db.execute(query)
		alectio_db.commit()


	def _log_unlabeled(self,alectio_db):

		# Query Currently selected
		query = ""
		for loop in range(int(self.backend_config.CUR_LOOP)+1):
			table_name = "selected_indices_{}".format(loop)
			query = query +"SELECT ix,val FROM {}".format(table_name)
			if not loop == int(self.backend_config.CUR_LOOP):
				query = query+" UNION ALL "

		alectio_db.execute(query)
		labeled_df = alectio_db.fetchdf()

        # Query all records at current loop
		table_name = "data_map_{}".format(self.backend_config.CUR_LOOP)
		query = "SELECT ix, val FROM {}".format(table_name)
		alectio_db.execute(query)
		all_df = alectio_db.fetchdf()
		
        # Query and register unlabeled  
		unlabeled_df = pd.merge(all_df, labeled_df, how = 'outer' , on='ix', indicator = True).query('_merge=="left_only"')[['ix','val_x']]
		unlabeled_df = unlabeled_df.sort_values(by=['ix'])
		unlabeled_df.columns=['ix','val']
		unlabeled_df['rownum'] = np.arange(len(unlabeled_df))
		alectio_db.register('unselected_indices_{}'.format(self.backend_config.CUR_LOOP), unlabeled_df)

		# Create a persistent table
		alectio_db.execute('CREATE TABLE unlabeled_indices_{} AS SELECT * FROM unselected_indices_{}'.format(self.backend_config.CUR_LOOP,self.backend_config.CUR_LOOP))
		alectio_db.commit()


	def _log_json(self, monitor, filename, data):
	    # Usually read
	    bucket = boto3.resource("s3").Bucket(self.backend_config.BUCKET_NAME)
	    json_load_s3 = lambda f: json.load(bucket.Object(key=f).get()["Body"])
	    meta_data = json_load_s3(filename)
	    with open(filename, "w") as f:
	        json.dump(meta_data, f)

	def df_to_dict(self, df):
		dict_df = {}
		for ix, row in df.iterrows():
			dict_df[row[0]] = row[1]
		return dict_df


	def _log_duck(self, monitor, filename, data ,database_logger , mode):
	    if mode =="write":
	        target_directory , table_name = os.path.split(filename)
	        #Create table 
	        self.create_table(str(table_name) , database_logger)
	        #Insert table 
	        for k, v in data.items():
	        	if type(v) == np.ndarray:
	        		value = self.np_stringify(v)
	        		self.insert_row(table_name ,k,value,database_logger)
	        	elif type(v) == str:
	        		self.insert_row(table_name , k , v, database_logger)
	        	else:
	        		raise ValueError("Invalid values logged , currently we only support logging dictionaries with INTEGER keys and numpy or string values")

	    elif mode == "read":
	    	s3_filename = filename+'.'+self.file_format	    	
	    	selected = client.read(self.backend_config.BUCKET_NAME, object_key=s3_filename, file_format= self.file_format)
	    	df = pd.read_parquet(selected, engine='pyarrow')
	    	dict_converted_df = self.df_to_dict(df)
	    	self._log_duck(monitor, filename, dict_converted_df ,database_logger ,"write")
	    else:
	    	raise ValueError("Invalid read/write mode set")


