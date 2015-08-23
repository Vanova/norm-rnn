import numpy as np
np.random.seed(0)

from datasets import PennTreebank
from utils import ProgressBar
from norm_rnn import *
from layers import *

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

# config model
model = List([
    Embed(len(train_set.vocab), layer_size),
    LSTM(layer_size, layer_size),
    LSTM(layer_size, layer_size),
    Linear(layer_size, len(train_set.vocab))
])

# initialize shared memory for lstm states
# (find a way to push this into the layer)
for layer in model.layers:
    if isinstance(layer, LSTM):
        layer.set_state(train_set.batch_size)

# initialize optimizer
grad_norm = GradientNorm(max_norm)
decay = DecayEvery(decay_epoch * len(train_set), decay_rate)
sgd = SGD(learning_rate, grad_norm, decay)

# compile theano functions
fit = compile_model(model, train_set, optimizer)
val = compile_model(model, valid_set)

# train
for epoch in range(1, epochs + 1):
    print 'epoch({})'.format(epoch)

    # fit
    train_errors = []
    train_progress = ProgressBar(range(len(train_set)))
    for batch in train_progress:
        error = fit(batch)
        train_errors.append(error)
        train_progress.cost = np.mean(train_errors)

    # validate
    valid_errors = []
    valid_progress = ProgressBar(range(len(valid_set)))
    for batch in valid_progress:
        error = val(batch)
        valid_errors.append(error)
        valid_progress.cost = np.mean(valid_errors)

    # reset lstm layers
    for layer in model.layers:
        if isinstance(layer, LSTM):
            layer.set_state(train_set.batch_size)
