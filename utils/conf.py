# -*- coding: utf-8 -*-

__author__ = 'liuyuemaicha'
import os
class disc_config(object):
    batch_size = 12
    learning_rate = 0.1
    learning_rate_decay_factor = 0.6
    vocab_size = 1000
    emb_dim = 16
    hidden_neural_size = 16
    hidden_layer_num = 2
    disc_data_dir = 'disc_data/'
    data_dir = 'disc_data/'
    max_len = 50
    num_layers = 1
    #query_len = 0
    beam_size = 12

    valid_num = 100
    checkpoint_num = 1000
    init_scale = 0.1
    class_num = 2
    keep_prob = 0.5
    num_epoch = 60
    max_decay_epoch = 30
    max_gradient_norm = 5
    out_dir = os.path.abspath(os.path.join(os.path.curdir,"runs"))
    steps_per_checkpoint = 100
    buckets = [(5, 10), (10, 15), (20, 25), (40, 50), (50, 50)]

class gen_config(object):
    beam_size = 5
    learning_rate = 0.5
    learning_rate_decay_factor = 0.99
    max_gradient_norm = 5.0
    batch_size = 4
    emb_dim = 100
    num_layers = 1
    vocab_size = 1000
    disc_data_dir = 'disc_data/'
    data_dir = "./gen_data/"
    train_dir = "./gen_data/"
    max_train_data_size = 0
    steps_per_checkpoint = 100
    buckets = [(5, 10), (10, 15), (20, 25), (40, 50), (50, 50)]

