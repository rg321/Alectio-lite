class ActiveStrategy(object):

    def __init__(self, neuralNet, nsteps, clear=True, verbose=True):
        self.clear = clear
        self.verbose = verbose
        self.net = neuralNet
        self.nsteps = nsteps
        self.train_length = len(train_dataset)
        self.test_length = len(test_dataset)
        self.train_lbls = {}
        self.test_lbls = {}
        self.train_ind = {}
        self.test_ind = {}
        self.init_stats()
        self.train_filter = [ i for i in range(self.train_length)]
        self.test_filter = [ i for i in range(self.test_length)]
        self.train_sampler = SubsetSampler(self.train_filter)
        self.test_sampler = SubsetSampler(self.test_filter)
        self.statsloader = torch.utils.data.DataLoader(train_dataset,
                                                       shuffle=True,
                                                       batch_size=16,
                                                       num_workers=2,
                                                       collate_fn=self.generate_batch)
        self.trainloader = torch.utils.data.DataLoader(train_dataset,
                                                       shuffle=True,
                                                       batch_size=16,
                                                       num_workers=2,
                                                       collate_fn=self.generate_batch)
        self.testloader  = torch.utils.data.DataLoader(test_dataset,
                                                       shuffle=False,
                                                       batch_size=16,
                                                       num_workers=1,
                                                       collate_fn=self.generate_batch)
        self._load()
        self.experiments = []

    def init_stats(self):
        self.stats = {}
        empty_dict = {}
        for i in range(self.nsteps + 1):
            empty_dict[i] = 0
        for cl in classes:
            self.stats[cl] = empty_dict.copy()
            self.train_ind[cl] = []
            self.test_ind[cl] = []

    def update_stats(self, cl, sl):
        self.stats[cl][0]    += 1
        self.stats[cl][sl+1] += 1

    def _load(self):
        for i, (text, offsets, cls) in enumerate(self.statsloader,0):
            text, offsets, cls = text.to(device), offsets.to(device), cls.to(device) 
            sl = int(float(i) / self.train_length * self.nsteps)
            self.update_stats(classes[cls[0]], sl)
        for i, (text, offsets, cls) in enumerate(self.trainloader, 0):
            text, offsets, cls = text.to(device), offsets.to(device), cls.to(device) 
            self.train_lbls[i] = classes[cls[0]]
            #self.train_ind[classes[labels[0]]].append(i)
        for i, (text, offsets, cls) in enumerate(self.testloader, 0):
            text, offsets, cls = text.to(device), offsets.to(device), cls.to(device) 
            self.test_lbls[i] = classes[cls[0]]
            #self.test_ind[classes[labels[0]]].append(i)

    def init_loaders(self):
        self.trainloader = torch.utils.data.DataLoader(train_dataset,
                                                       shuffle=True,
                                                       batch_size=16,
                                                       num_workers=2,
                                                       sampler=self.train_sampler,
                                                       collate_fn=self.generate_batch)
        self.testloader = torch.utils.data.DataLoader(test_dataset,
                                                      shuffle=False,
                                                      batch_size=16,
                                                      num_workers=2,
                                                      sampler=self.test_sampler,
                                                      collate_fn=self.generate_batch)
        
    
    def initialize_weights(self):
        initrange = 0.5
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()
        
    def incremental_supervised(self):
        np.random.shuffle(self.train_filter)
        
    def load_strategy(self, selected):
        self.train_filter = selected
        
    def generate_batch(self,batch):
        label = torch.tensor([entry[0] for entry in batch])
        text = [entry[1] for entry in batch]
        offsets = [0] + [len(entry) for entry in text]
        offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
        text = torch.cat(text)
        return text, offsets, label
        
    def train(self):

        if self.clear:
            self.initialize_weights()

        criterion = nn.CrossEntropyLoss().to(device)
        optimizer = optim.SGD(self.net.parameters(), lr=4.0)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 1, gamma=0.9)

        for epoch in range(2):

            running_loss = 0.0
            for i, (text, offsets, cls) in enumerate(self.trainloader, 0):
                # get the inputs
                text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = self.net(text, offsets)
                loss = criterion(outputs, cls)
                loss.backward()
                optimizer.step()

                # print statistics
                if self.verbose:
                    running_loss += loss.item()
                    if i % 2000 == 1999:    # print every 2000 mini-batches
                        print('[%d, %5d] loss: %.3f' %
                            (epoch + 1, i + 1, running_loss / 2000))
                        running_loss = 0.0
            scheduler.step()

        print('Finished Training')
        
    def test(self):

        dataiter = iter(self.testloader)
        text, offsets, cls  = dataiter.next()
        outputs = self.net(text, offsets)
        _, predicted = torch.max(outputs, 1)
        for j in range(16):
            print('GroundTruth: ', ' '.join('%5s' % classes[cls[j]]))
            print('Predicted: ', ' '.join('%5s' % classes[predicted[j]]))           

        soft = torch.nn.Softmax(dim=1)

        ##### Stats below ######

        ground_truth = []
        predictions  = []
        probabilities = []

        correct = 0
        total = 0
        with torch.no_grad():
            for i, (text, offsets, cls) in enumerate(self.testloader, 0):
                text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
                outputs = self.net(text, offsets)
                _, predicted = torch.max(outputs.data, 1)
                ground_truth.append(cls.numpy().tolist())
                predictions.extend(predicted.numpy().tolist())
                probabilities.extend(soft(outputs))
                total += cls.size(0)
                correct += (predicted == cls).sum().item()

        print('Accuracy of the network on the {0} test images: {1}%'
                .format(self.test_length, 100 * correct / total))

        class_correct = {}
        class_total   = {}
        class_pred    = {}
        for cl in classes:
            class_correct[cl] = 0
            class_total[cl]   = 0
            class_pred[cl]    = 0

        with torch.no_grad():
            for text, offsets, cls in self.testloader:
                text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
                outputs = self.net(text, offsets)
                _, predicted = torch.max(outputs, 1)
                c = (predicted == cls).squeeze()
                
                for i in range(cls.size(0)):
                    label = cls[i]
                    class_correct[classes[label]] += c[i].item()
                    class_total[classes[label]] += 1
                    class_pred[classes[predicted[i]]] += 1

        if self.verbose:
            for cl in classes:
                precision = class_correct[cl] / class_total[cl]
                Fscore = -99.0
                if class_pred[cl] > 0:
                    recall = class_correct[cl] / class_pred[cl]
                    Fscore    = 2.0 * precision * recall / (precision + recall)
                print('%5s : \t Accuracy: %2d %% \t F-Score %.2f' % (
                        cl,
                        100.0 * precision,
                        Fscore))

        return correct / total, ground_truth, predictions, probabilities

    def infer(self, sample):
        sampler = SubsetSampler(sample)
        dataloader = torch.utils.data.DataLoader(train_dataset,
                                                 shuffle=False,
                                                 batch_size=1,
                                                 num_workers=4,
                                                 sampler=sampler
                                                 collate_fn=self.generate_batch)
        soft = torch.nn.Softmax(dim=0)
        results = []
        with torch.no_grad():
            for r, (text, offsets, cls) in enumerate(dataloader):
                text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
                outputs = self.net(text, offsets)
                _, predicted = torch.max(outputs.data, 1)
                ground_truth = cls.item()
                prediction   = predicted.item()
                probability  = soft(outputs[0])
                classwiseprobs = probability.numpy()
                results.append([sample[r], classes[ground_truth], classes[prediction], probability[prediction],classwiseprobs])
                #total += labels.size(0)
                #correct += (predicted == labels).sum().item()
        return results
    
    def run_one(self, selected):
        self.load_strategy(selected)
        results = []
        if self.clear:
            self.initialize_weights()
            print("Network's weights reinitialized")
        print("Training for {0} records:".format(len(selected)))
        self.train_sampler = SubsetSampler(self.train_filter)
        self.trainloader = torch.utils.data.DataLoader(train_dataset,
                                                        shuffle=False,
                                                        batch_size=1,
                                                        num_workers=1,
                                                        sampler=self.train_sampler,
                                                        collate_fn=self.generate_batch)
        self.train()
        res, truth, outs, probs = self.test()

        return res
    
    def run_experiment(self, nsteps, maximum):
        results = []
        for n in range(1, nsteps+1):
            if self.clear:
                self.initialize_weights()
                print("Network's weights reinitialized")
            nsamples = int(1.0 / nsteps * n * maximum)
            print("Training for {0} samples:".format(nsamples))
            self.train_sampler = SubsetSampler(self.train_filter[:nsamples])
            self.trainloader = torch.utils.data.DataLoader(train_dataset,
                                                           shuffle=False,
                                                           batch_size=1,
                                                           num_workers=4,
                                                           sampler=self.train_sampler,
                                                           collate_fn=self.generate_batch)
            self.train()
            res, truth, outs, probs = self.test()
            results.append(res)

        return results
    
    def run_ConfidenceAL(self, qStrategy, nsteps, maximum):
    
        results = []
    
        unlabeled = [i for i in range(len(train_dataset))]
        labeled   = []

        to_be_labeled = random.sample(unlabeled, int(nps))
        unlabeled = list(set(unlabeled)-set(to_be_labeled))
        myres = self.run_one(to_be_labeled)
        results.append(myres)
    
        for n in range(1, nsteps):
            myResults = self.infer(unlabeled)
            to_be_labeled.extend( qStrategy(myResults, int(maximum/nsteps)) ) # updating function
            unlabeled = list(set(unlabeled)-set(to_be_labeled))
            myres = self.run_one(to_be_labeled)
            results.append(myres)
        
        return results
    
    def run_StreamingAL(self, qStrategy, nsteps, maximum):
    
        results = []
        stepSizes = []
    
        unlabeled = [i for i in range(len(train_dataset))]
        labeled   = []

        to_be_labeled = random.sample(unlabeled, int(nps))
        unlabeled = list(set(unlabeled)-set(to_be_labeled))
        myres = self.run_one(to_be_labeled)
        results.append(myres)
        stepSizes.append(len(to_be_labeled))
    
        for n in range(1, nsteps):
            myResults = self.infer(unlabeled)
            to_be_labeled.extend( qStrategy(myResults) ) # updating function
            if (len(to_be_labeled) > maximum):
                break
            unlabeled = list(set(unlabeled)-set(to_be_labeled))
            myres = self.run_one(to_be_labeled)
            results.append(myres)
            stepSizes.append(len(to_be_labeled))
        
        return results, stepSizes
