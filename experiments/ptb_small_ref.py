import numpy as np
np.random.seed(0)

from datasets import PennTreebank
from optimizers import *
from model import *
from layers import *

# data params
time_steps = 20
batch_size = 20

# models params
layer_size = 200

# optimizer params
learning_rate = 1
decay_rate = 0.5
decay_epoch = 4
max_norm = 5
epochs = 15

# data
dataset = PennTreebank(batch_size, time_steps)
vocab_size = len(dataset.vocab_map)

# model
model = List([
    Embed(vocab_size, layer_size),
    LSTM(layer_size, layer_size),
    LSTM(layer_size, layer_size),
    Linear(layer_size, vocab_size)])

# optimizer
grad = MaxNorm()
decay = DecayEvery(decay_epoch * len(dataset.X_train.get_value()), decay_rate)
optimizer = SGD(learning_rate, grad, decay)

# train
model.compile(dataset, optimizer)
model.compile(dataset)
model.train(epochs)
