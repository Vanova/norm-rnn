import numpy as np
np.random.seed(0)

from datasets import PennTreebank
from utils import ProgressBar
from norm_rnn import *
from layers import *

experiments = 10

# hyper parameters
layer_size = 200
time_steps = 20
batch_size = 20
max_norm = 5
decay_rate = 0.5
decay_epoch = 4
learning_rate = 1
epochs = 15

# load data
train_set = PennTreebank(batch_size, time_steps)
valid_set = PennTreebank(batch_size, time_steps,
                         PennTreebank.valid_path, train_set.vocab)
test_set = PennTreebank(2, time_steps,
                        PennTreebank.test_path, train_set.vocab)

# config model
models = {
    'reference':
    List([
        Embed(len(train_set.vocab), layer_size),
        LSTM(layer_size, layer_size),
        LSTM(layer_size, layer_size),
        Linear(layer_size, len(train_set.vocab))
    ]),

    'batch-norm':
    List([
        Embed(len(train_set.vocab), layer_size),
        BN(layer_size, time_steps=time_steps),
        LSTM(layer_size, layer_size),
        BN(layer_size, time_steps=time_steps),
        LSTM(layer_size, layer_size),
        Linear(layer_size, len(train_set.vocab))
    ]),
}

for model_name, model in models.iteritems():

    print 'model({})'.format(experiment)

    # initialize shared memory for lstm states
    # (find a way to push this into the layer)
    for layer in model.layers:
        if isinstance(layer, LSTM):
            layer.set_state(batch_size)

    # initialize optimizer
    grad_norm = MaxNorm(max_norm)
    decay = DecayEvery(decay_epoch * len(train_set), decay_rate)
    optimizer = SGD(learning_rate, grad_norm, decay)

    # compile theano functions
    fit = compile_model(model, train_set, optimizer)
    val = compile_model(model, valid_set)

    # train
    for epoch in range(1, epochs + 1):
        print 'epoch({})'.format(epoch)

        # fit
        perplexity_list = []
        accuracy_list = []
        train_progress = ProgressBar(range(len(train_set)))
        for batch in train_progress:
            perplexity, accuracy = fit(batch)
            perplexity_list.append(perplexity)
            accuracy_list.append(accuracy)
            train_progress.perplexity = np.mean(perplexity_list)
            train_progress.accuracy = np.mean(accuracy_list)

        # validate
        perplexity_list = []
        accuracy_list = []
        valid_progress = ProgressBar(range(len(valid_set)))
        for batch in valid_progress:
            perplexity, accuracy = val(batch)
            perplexity_list.append(perplexity)
            accuracy_list.append(accuracy)
            valid_progress.perplexity = np.mean(perplexity_list)
            valid_progress.accuracy = np.mean(accuracy_list)

        # reset lstm layers
        for layer in model.layers:
            if isinstance(layer, LSTM):
                layer.set_state(batch_size)

    # reset lstm layers
    for layer in model.layers:
        if isinstance(layer, LSTM):
            layer.set_state(2)

    val = compile_model(model, test_set)

    # validate
    perplexity_list = []
    accuracy_list = []
    valid_progress = ProgressBar(range(len(test_set)))
    for batch in valid_progress:
        perplexity, accuracy = val(batch)
        perplexity_list.append(perplexity)
        accuracy_list.append(accuracy)
        valid_progress.perplexity = np.mean(perplexity_list)
        valid_progress.accuracy = np.mean(accuracy_list)