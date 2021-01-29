import pickle

import alectiolite

from alectiolite.callbacks import AlectioCallback



# Get token from FE 
token = 'e33aa51443b743d49d71c8dc9de25932'

data = pickle.load(open('data_map.pkl','rb'))
inputrecords = {'1': 1111 ,'2': 11111 , '3' : 838383883}

class Alectioreturn(AlectioCallback):
	def on_infer_start(self):
		return data

	def on_infer_end(self):
		return inputrecords



#Initialize classification
cb= Alectioreturn()



alectiolite.curate_classification(token = token , subset = 0, callbacks = [cb])




#Getconfig
alectiolite.curate_classification.config











#print(exp_info)




"""
if __name__ == '__main__':
    token ='e33aa51443b743d49d71c8dc9de25932'
    serverresponse = LogitAL(token)
"""
