import pickle
import alectiolite
from alectiolite.callbacks import AlectioCallback



# Steps


# Get token from FE 
token = 'e33aa51443b743d49d71c8dc9de25932'

data = pickle.load(open('data_map.pkl','rb'))
inputrecords = {'1': 1111 ,'2': 11111 , '3' : 838383883}

class Alectioreturn(AlectioCallback):
	def on_infer_start(self,monitor ,data ,config):
		alectiolite.alectio_logger(monitor= monitor,
			               data   = data,
			               config = config)

	def on_infer_end(self, model_outputs):

		return inputrecords






config = alectiolite.experiment_config(token = token)
cb= Alectioreturn()
cb.on_infer_start(monitor= 'datasetstate',data = data, config = config)
print(" I am passing things now ")
alectiolite.curate_classification(config = config , subset = 0, callbacks = [cb])

#Initialize classification
#cb= Alectioreturn()



#alectiolite.curate_classification(token = token , subset = 0, callbacks = [cb])




#print("Lets print my config")

#Getconfig
#alectiolite.curate_classification.config











#print(exp_info)




"""
if __name__ == '__main__':
    token ='e33aa51443b743d49d71c8dc9de25932'
    serverresponse = LogitAL(token)
"""
