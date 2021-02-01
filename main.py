import pickle
import alectiolite
from alectiolite.callbacks import CurateCallback



# Steps


# Get token from FE 
token = 'e33aa51443b743d49d71c8dc9de25932'

data = pickle.load(open('data_map.pkl','rb'))
inputrecords = {'1': 1111 ,'2': 11111 , '3' : 838383883}




# Step 1 Get experiment config
config = alectiolite.experiment_config(token = token)
# Step 2 Initialize your callback
cb= CurateCallback()
# Step 3 Tap what type of experiment you want to run
alectiolite.curate_classification(config = config , callbacks = [cb])

# Step 4 Tap overrideables
cb.on_project_start(monitor= 'datasetstate',data = data, config = config)



#Initialize classification
#cb= Alectioreturn()



#alectiolite.curate_classification(token = token , subset = 0, callbacks = [cb])




#print("Lets print my config")

#Getconfig
#alectiolite.curate_classification.config











#print(exp_info)




"""



class Alectioreturn(AlectioCallback):
	def on_infer_start(self,monitor ,data ,config):
		alectiolite.alectio_logger(monitor= monitor,
			               data   = data,
			               config = config)

	def on_infer_end(self, model_outputs):

		return inputrecords


if __name__ == '__main__':
    token ='e33aa51443b743d49d71c8dc9de25932'
    serverresponse = LogitAL(token)
"""
