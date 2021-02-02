import os
import torch
import torchtext
from torchtext.datasets import text_classification
import pickle
import alectiolite
from alectiolite.callbacks import CurateCallback
import torch.nn as nn
import torch.nn.functional as F
from model import TextSentiment, SubsetSampler
from tqdm import tqdm
import torch.optim as optim


TOKEN = "e4f588d9d6404a34a4f66c7f5cf87aac"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def generate_batch(batch):
    label = torch.tensor([entry[0] for entry in batch])
    text = [entry[1] for entry in batch]
    offsets = [0] + [len(entry) for entry in text]
    offsets = torch.tensor(offsets[:-1]).cumsum(dim=0)
    text = torch.cat(text)
    return text, offsets, label


def get_loaders():

    # Params
    NGRAMS = 2
    BATCH_SIZE = 16
    import os

    if not os.path.isdir("./.data"):
        os.mkdir("./.data")

    # Setup training datasets
    train_dataset, test_dataset = text_classification.DATASETS["AG_NEWS"](
        root="./.data", ngrams=NGRAMS, vocab=None
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    mytrainloader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,
        collate_fn=generate_batch,
    )

    mytestloader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=2,
        collate_fn=generate_batch,
    )

    return train_dataset, test_dataset, mytrainloader, mytestloader


def train_model(sample):
    train_dataset, test_dataset, mytrainloader, mytestloader = get_loaders()
    classes = ("World", "Sports", "Business", "Sci/Tec")


def infer(sample):
    train_dataset, test_dataset, mytrainloader, mytestloader = get_loaders()
    classes = ("World", "Sports", "Business", "Sci/Tec")

    VOCAB_SIZE = len(train_dataset.get_vocab())
    EMBED_DIM = 32
    NUM_CLASS = len(train_dataset.get_labels())
    mynet = TextSentiment(VOCAB_SIZE, EMBED_DIM, NUM_CLASS).to(device)
    mycriterion = nn.CrossEntropyLoss().to(device)
    myoptimizer = optim.SGD(mynet.parameters(), lr=4.0)
    myscheduler = torch.optim.lr_scheduler.StepLR(myoptimizer, 1, gamma=0.9)

    sampler = SubsetSampler(sample)
    dataloader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=1,
        num_workers=4,
        sampler=sampler,
        collate_fn=generate_batch,
    )
    soft = torch.nn.Softmax(dim=0)
    results = []
    infer_outs = {}
    with torch.no_grad():
        with tqdm(total=len(dataloader), desc="Inferring on unlabeled ...") as tq:
            for r, (text, offsets, cls) in enumerate(dataloader):
                text, offsets, cls = text.to(device), offsets.to(device), cls.to(device)
                outputs = mynet(text, offsets)
                _, predicted = torch.max(outputs.data, 1)
                ground_truth = cls.item()
                prediction = predicted.item()
                infer_outs[r] = soft(outputs[0]).numpy().tolist()
                tq.update(1)
            # results.append([sample[r], classes[ground_truth], classes[prediction], probability[prediction],classwiseprobs])

    return infer_outs


if __name__ == "__main__":
    print("Preparing to run AG_NEWS")

    # Step 1 Get experiment config
    config = alectiolite.experiment_config(token=TOKEN)
    # Step 2 Initialize your callback
    cb = CurateCallback()
    # Step 3 Tap what type of experiment you want to run
    alectiolite.curate_classification(config=config, callbacks=[cb])
    # Step 4 Tap overrideables
    datasetsize = 120000
    datasetstate = {ix: n for ix, n in enumerate(range(120000))}
    # On ready to start experiment
    cb.on_experiment_start(monitor="datasetstate", data=datasetstate, config=config)

    # Consume Alectio suggestions
    cur_loop = config["cur_loop"]
    log_dir = os.path.join(config["project_id"], config["experiment_id"])
    indices_file = "selected_indices_{}.pkl".format(cur_loop)
    indices = pickle.load(open(os.path.join(log_dir, indices_file), "rb"))

    print("Number of selected indices are ", len(indices))
    print("Lets start inferring on the unlabeled ")

    infer_outs = infer(indices)

    # On ready to pass unlabeled
    cb.on_infer_end(monitor="pre_softmax", data=infer_outs, config=config)
