# -*- coding: utf-8 -*-

__author__ = 'liuyuemaicha'
import os
class disc_config(object):
    batch_size = 256
    lr = 0.2
    lr_decay = 0.9
    vocab_size = 1000
    embed_dim = 16
    steps_per_checkpoint = 200
    hidden_neural_size = 4
    hidden_layer_num = 2
    num_layers = 2
    train_dir = './disc_data/'
    name_model = "disc_model"
    tensorboard_dir = "./tensorboard/disc_log/"
    name_loss = "disc_loss"
    max_len = 50
    piece_size = batch_size * steps_per_checkpoint
    piece_dir = "./disc_data/batch_piece/"
    #query_len = 0
    valid_num = 100
    init_scale = 0.1
    num_class = 2
    keep_prob = 0.5
    #num_epoch = 60
    #max_decay_epoch = 30
    max_grad_norm = 5
    buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]


class gen_config(object):
    beam_size = 5
    learning_rate = 0.5
    learning_rate_decay_factor = 0.99
    max_gradient_norm = 5.0
    batch_size = 4
    emb_dim = 100
    num_layers = 1
    vocab_size = 1000
    name_model = "st_model"
    disc_data_dir = 'disc_data/'
    data_dir = "./gen_data/"
    train_dir = "./gen_data/"
    max_train_data_size = 0
    steps_per_checkpoint = 100
    tensorboard_dir = "./tensorboard/gen_log/"
    name_loss = "gen_loss"
    teacher_loss = "teacher_loss"
    reward_name = "reward"
    buckets = [(5, 10), (10, 15), (20, 25), (40, 50)]

