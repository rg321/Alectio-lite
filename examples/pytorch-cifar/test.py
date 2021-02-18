import os
import torch
import torchvision
import torchvision.transforms as transforms
from model import Net , SubsetSampler
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import pickle
import alectiolite
from tqdm import tqdm
from alectiolite.callbacks import CurateCallback



TOKEN = "bd4219cccc2c44159725b4fe68ded7bf"
#device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device = torch.device("cuda:0")
print(device)

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                        download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=16,
                                          shuffle=True, num_workers=0)

testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=16,
                                         shuffle=False, num_workers=0)

classes = ('plane', 'car', 'bird', 'cat', 'deer', 
           'dog', 'frog', 'horse', 'ship', 'truck')



net = Net()
net = net.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)


def train_network():
	for epoch in range(2):  # loop over the dataset multiple times

	    running_loss = 0.0
	    for i, data in enumerate(trainloader, 0):
	        # get the inputs; data is a list of [inputs, labels]
	        inputs, labels = data
	        inputs = inputs.to(device)
	        labels = labels.to(device)
	        # zero the parameter gradients
	        optimizer.zero_grad()

	        # forward + backward + optimize
	        outputs = net(inputs)
	        loss = criterion(outputs, labels)
	        loss.backward()
	        optimizer.step()

	        # print statistics
	        running_loss += loss.item()
	        if i % 2000 == 1999:    # print every 2000 mini-batches
	            print('[%d, %5d] loss: %.3f' %
	                  (epoch + 1, i + 1, running_loss / 2000))
	            running_loss = 0.0

	print('Finished Training')




def infer(sample):
    sampler = SubsetSampler(sample)
    dataloader =torch.utils.data.DataLoader(trainset , batch_size =1 , num_workers = 0 , sampler = sampler)
    soft = torch.nn.Softmax(dim=0)
    results = []
    infer_outs = {}
    with torch.no_grad():
        with tqdm(total=len(dataloader), desc="Inferring on unlabeled ...") as tq:
            for r, (data) in enumerate(dataloader):
                inputs , labels = data
                inputs = inputs.to(device)
                labels = labels.to(device)
                outputs = net(inputs)
                _, predicted =torch.max(outputs.data,1)
                GT =labels.item()
                prediction = predicted.item()
                infer_outs[r] = soft(outputs[0]).cpu().numpy().tolist()
                tq.update(1)
            #results.append([sample[r],classes[ground_truth], classes[prediction], probability[prediction],classwiseprobs])
    return infer_outs





if __name__ == "__main__":
    print("Preparing to run CIFAR10")

    # Step 1 Get experiment config
    config = alectiolite.experiment_config(token=TOKEN)
    print(config)
    # Step 2 Initialize your callback
    cb = CurateCallback()
    # Step 3 Tap what type of experiment you want to run
    alectiolite.curate_classification(config=config, callbacks=[cb])
    # Step 4 Tap overrideables
    datasetsize = 40000
    datasetstate = {ix: n for ix, n in enumerate(range(datasetsize))}
    # On ready to start experiment
    cb.on_experiment_start(monitor="datasetstate", data=datasetstate, config=config)

    # Consume Alectio suggestions
    n_loop = config["cur_loop"]
    log_dir = os.path.join(config["project_id"], config["experiment_id"])
    indices = []
    for cur_loop in range(int(n_loop)+1):
        indices_file = "selected_indices_{}.pkl".format(str(cur_loop))
        indices.extend(pickle.load(open(os.path.join(log_dir, indices_file), "rb")))

    print("Number of selected indices are ", len(indices))
    print("Lets start inferring on the unlabeled ")

    infer_outs = infer(indices)

    # On ready to pass unlabeled
    cb.on_infer_end(monitor="logits", data=infer_outs, config=config)

    cb.on_experiment_end(token= TOKEN)
