# -*- coding: utf-8 -*-

import os

import tensorflow as tf
import numpy as np
import time
import gen.generator as gens
import disc.hier_disc as h_disc
import random
import sys
import utils.conf as conf
import utils.data_utils as data_utils
from six.moves import xrange  # pylint: disable=redefined-builtin

gen_config = conf.gen_config
disc_config = conf.disc_config
evl_config = conf.disc_config
steps_per_checkpoint = 100

# pre train discriminator
def disc_pre_train():
    #discs.train_step(disc_config, evl_config)
    h_disc.hier_train(disc_config, evl_config)


# pre train generator
def gen_pre_train():
    gens.train(gen_config)


# gen data for disc training
def gen_disc():
    gens.decoder(gen_config)


# test gen model
def gen_test():
    gens.test_decoder(gen_config)
# pre train discriminator


# prepare disc_data for discriminator and generator
def disc_train_data(sess, gen_model, vocab, source_inputs, source_outputs,
                    encoder_inputs, decoder_inputs, target_weights, bucket_id, mc_search=False ,default_labels= 1):

    train_query, train_answer = [], []
    query_len = gen_config.buckets[bucket_id][0]
    answer_len = gen_config.buckets[bucket_id][1]

    for query, answer in zip(source_inputs, source_outputs):
        query = query[:query_len] + [int(data_utils.PAD_ID)] * (query_len - len(query) if query_len > len(query) else 0)
        train_query.append(query)
        answer = answer[:answer_len] + [int(data_utils.PAD_ID)] * (answer_len - len(answer) if answer_len > len(answer) else 0)
        train_answer.append(answer)
        train_labels = [default_labels for _ in source_inputs]


    def decoder(num_roll):
        for _ in xrange(num_roll):
            _, _, output_logits = gen_model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket_id,
                                                 forward_only=True, mc_search=mc_search)

            seq_tokens = []
            resps = []
            for seq in output_logits:
                row_token = []
                for t in seq:
                    row_token.append(int(np.argmax(t, axis=0)))
                seq_tokens.append(row_token)

            seq_tokens_t = []
            for col in range(len(seq_tokens[0])):
                seq_tokens_t.append([seq_tokens[row][col] for row in range(len(seq_tokens))])

            for seq in seq_tokens_t:
                if data_utils.EOS_ID in seq:
                    resps.append(seq[:seq.index(data_utils.EOS_ID)][:gen_config.buckets[bucket_id][1]])
                else:
                    resps.append(seq[:gen_config.buckets[bucket_id][1]])

            for i, output in enumerate(resps):
                output = output[:answer_len] + [data_utils.PAD_ID] * (answer_len - len(output) if answer_len > len(output) else 0)
                train_query.append(train_query[i])
                train_answer.append(output)
                train_labels.append(0)


        return train_query, train_answer, train_labels

    if mc_search:
        train_query, train_answer, train_labels = decoder(disc_config.beam_size)
    else:
        train_query, train_answer, train_labels = decoder(1)

    print("disc_train_data, mc_search: ", mc_search)
    for query, answer, label in zip(train_query, train_answer, train_labels):
         print(str(label) + "\t" + str(query) + ":\t" + str(answer))

    return train_query, train_answer, train_labels

# prepare disc_data for discriminator and generator
def disc_neg_train_data(sess, gen_model, vocab, source_inputs, source_outputs,
                        encoder_inputs, decoder_inputs,
                        target_weights, bucket_id, mc_search=False ,default_labels= 0):

    train_query, train_answer = [], []
    query_len = gen_config.buckets[bucket_id][0]
    answer_len = gen_config.buckets[bucket_id][1]
    
    random.suffle(source_inputs)
    random.suffle(source_outputs)
    random.suffle(encoder_inputs)
    random.suffle(decoder_inputs)
    

    for query, answer in zip(source_inputs, source_outputs):
        query = query[:query_len] + [int(data_utils.PAD_ID)] * (query_len - len(query) if query_len > len(query) else 0)
        train_query.append(query)
        answer = answer[:answer_len] + [int(data_utils.PAD_ID)] * (answer_len - len(answer) if answer_len > len(answer) else 0)
        train_answer.append(answer)
        train_labels = [default_labels for _ in source_inputs]


    def decoder(num_roll):
        for _ in xrange(num_roll):
            _, _, output_logits = gen_model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket_id,
                                                 forward_only=True, mc_search=mc_search)

            seq_tokens = []
            resps = []
            for seq in output_logits:
                row_token = []
                for t in seq:
                    row_token.append(int(np.argmax(t, axis=0)))
                seq_tokens.append(row_token)

            seq_tokens_t = []
            for col in range(len(seq_tokens[0])):
                seq_tokens_t.append([seq_tokens[row][col] for row in range(len(seq_tokens))])

            for seq in seq_tokens_t:
                if data_utils.EOS_ID in seq:
                    resps.append(seq[:seq.index(data_utils.EOS_ID)][:gen_config.buckets[bucket_id][1]])
                else:
                    resps.append(seq[:gen_config.buckets[bucket_id][1]])

            for i, output in enumerate(resps):
                output = output[:answer_len] + [data_utils.PAD_ID] * (answer_len - len(output) if answer_len > len(output) else 0)
                train_query.append(train_query[i])
                train_answer.append(output)
                train_labels.append(0)


        return train_query, train_answer, train_labels

    if mc_search:
        train_query, train_answer, train_labels = decoder(disc_config.beam_size)
    else:
        train_query, train_answer, train_labels = decoder(1)

    print("disc_train_data, mc_search: ", mc_search)
    for query, answer, label in zip(train_query, train_answer, train_labels):
         print(str(label) + "\t" + str(query) + ":\t" + str(answer))

    return train_query, train_answer, train_labels

def softmax(x):
    prob = np.exp(x) / np.sum(np.exp(x), axis=0)
    return prob

# discriminator api
def disc_step(sess, bucket_id, disc_model, train_query, train_answer, train_labels, forward_only=False):
    feed_dict={}

    for i in xrange(len(train_query)):

        feed_dict[disc_model.query[i].name] = train_query[i]

    for i in xrange(len(train_answer)):
        feed_dict[disc_model.answer[i].name] = train_answer[i]

    feed_dict[disc_model.target.name]=train_labels

    loss = 0.0
    if forward_only:
        fetches = [disc_model.b_logits[bucket_id]]
        logits = sess.run(fetches, feed_dict)
        logits = logits[0]
    else:
        fetches = [disc_model.b_train_op[bucket_id], disc_model.b_loss[bucket_id], disc_model.b_logits[bucket_id]]
        train_op, loss, logits = sess.run(fetches,feed_dict)

    # softmax operation
    logits = np.transpose(softmax(np.transpose(logits)))

    reward, gen_num = 0.0, 0
    for logit, label in zip(logits, train_labels):
        if int(label) == 0:
            reward += logit[1]
            gen_num += 1
    reward = reward / gen_num

    return reward, loss, gen_num

# Adversarial Learning for Neural Dialogue Generation
def al_train():
    with tf.Session() as sess:

        vocab, rev_vocab, dev_set, train_set, negative_train_set, null_train_set = gens.prepare_data(gen_config)
        for set in train_set:
            print("train len: ", len(set))

        train_bucket_sizes = [len(train_set[b]) for b in xrange(len(gen_config.buckets))]
        train_total_size = float(sum(train_bucket_sizes))
        train_buckets_scale = [sum(train_bucket_sizes[:i + 1]) / train_total_size
                               for i in xrange(len(train_bucket_sizes))]

        disc_model = h_disc.create_model(sess, disc_config, disc_config.name_model)
        gen_model = gens.create_model(sess, gen_config, forward_only=False, name_scope=gen_config.name_model)

        current_step = 0

        step_time, disc_loss, gen_loss, t_loss, batch_reward = 0.0, 0.0, 0.0, 0.0, 0.0
        gen_loss_summary = tf.Summary()
        disc_loss_summary = tf.Summary()

        gen_writer = tf.summary.FileWriter(gen_config.tensorboard_dir, sess.graph)
        disc_writer = tf.summary.FileWriter(disc_config.tensorboard_dir, sess.graph)

        while True:

            current_step += 1
            start_time = time.time()
            random_number_01 = np.random.random_sample()
            bucket_id = min([i for i in xrange(len(train_buckets_scale))
                         if train_buckets_scale[i] > random_number_01])
            disc_config.max_len = disc_config.buckets[bucket_id][0] + disc_config.buckets[bucket_id][1]
            print("===========================Update Discriminator================================")
            # 1.Sample (X,Y) from real disc_data
            print("bucket_id: %d" %bucket_id)
            encoder_inputs, decoder_inputs, target_weights, source_inputs, source_outputs = gen_model.get_batch(train_set, bucket_id, gen_config.batch_size)

            # 1.1.Sample (X,^Y) from generated disc_data
            neg_encoder_inputs, neg_decoder_inputs, neg_target_weights, neg_source_inputs, neg_source_outputs = gen_model.neg_get_batch(negative_train_set, bucket_id, gen_config.batch_size)

            # 1.2.Sample (null,^Y) from generated disc_data
            null_encoder_inputs, null_decoder_inputs, null_target_weights, null_source_inputs, null_source_outputs = gen_model.get_batch(null_train_set, bucket_id, gen_config.batch_size)

            print ("encoder_inputs: ", len(encoder_inputs))
            print ("decoder_inputs: ", len(decoder_inputs))
            print ("source_inputs: ", len(source_inputs))
            print ("source_outputs: ", len(source_outputs))
            print ("null_encoder_inputs: ", len(encoder_inputs))
            print ("null_decoder_inputs: ", len(decoder_inputs))
            print ("null_source_inputs: ", len(source_inputs))
            print ("null_source_outputs: ", len(source_outputs))
            # 2.Sample (X,Y) and (X, ^Y) through ^Y ~ G(*|X)
            train_query, train_answer, train_labels = disc_train_data(sess, gen_model, vocab, source_inputs, source_outputs,
                                                        encoder_inputs, decoder_inputs, target_weights, bucket_id, mc_search=False)
            # 2.Sample (X, ^Y) through ^Y ~ G(*|X)
            neg_train_query, neg_train_answer, neg_train_labels = disc_neg_train_data(sess, gen_model, vocab, neg_source_inputs, neg_source_outputs,
                                                                                  neg_encoder_inputs, neg_decoder_inputs, target_weights, bucket_id, mc_search=False,default_labels= 0)

            # 2.Sample (null, ^Y) through ^Y ~ G(*|null)
            null_train_query, null_train_answer, null_train_labels = disc_train_data(sess, gen_model, vocab, null_source_inputs, null_source_outputs,
                                                        null_encoder_inputs, null_decoder_inputs, target_weights, bucket_id, mc_search=False, default_label = 0)

            print("==============================mc_search: False===================================")
            if current_step % 200 == 0:
                print("train_query: ", len(train_query))
                print("train_answer: ", len(train_answer))
                print("train_labels: ", len(train_labels))
                for i in xrange(len(train_query)):
                    print("lable: ", train_labels[i])
                    print("train_answer_sentence: ", train_answer[i])
                    print(" ".join([tf.compat.as_str(rev_vocab[output]) for output in train_answer[i]]))

            train_query = np.transpose(train_query)
            train_answer = np.transpose(train_answer)
            neg_train_query = np.transpose(neg_train_query)
            neg_train_answer = np.transpose(neg_train_answer)
            null_train_query = np.transpose(null_train_query)
            null_train_answer = np.transpose(null_train_answer)

            # 3.Update D using (X, Y ) as positive examples and(X, ^Y) as negative examples
            _, disc_step_loss, _ = disc_step(sess, bucket_id, disc_model, train_query, train_answer, train_labels, forward_only=False)
            disc_loss += disc_step_loss / disc_config.steps_per_checkpoint
            # 3.1.Update D using (X, ^Y) as negative examples
            _, disc_step_loss, _ = disc_step(sess, bucket_id, disc_model, neg_train_query, neg_train_answer, neg_train_labels, forward_only=False)
            disc_loss += disc_step_loss / disc_config.steps_per_checkpoint
            # 3.2.Update D using (null, ^Y) as negative examples
            _, disc_step_loss, _ = disc_step(sess, bucket_id, disc_model, null_train_query, null_train_answer, null_train_labels, forward_only=False)
            disc_loss += disc_step_loss / disc_config.steps_per_checkpoint

            print("==================Update Generator: %d=========================" % current_step)
            # 1.Sample (X,Y) from real disc_data
            update_gen_data = gen_model.get_batch(train_set, bucket_id, gen_config.batch_size)
            encoder, decoder, weights, source_inputs, source_outputs = update_gen_data

            # 2.0.Sample (X,Y) and (X, ^Y) through ^Y ~ G(*|X) with Monte Carlo search
            train_query, train_answer, train_labels = disc_train_data(sess, gen_model, vocab, source_inputs, source_outputs,
                                                                encoder, decoder, weights, bucket_id, mc_search=True)
            # 2.1.Sample (X, ^Y) through ^Y ~ G(*|X)
            neg_train_query, neg_train_answer, neg_train_labels = disc_neg_train_data(sess, gen_model, vocab, neg_source_inputs, neg_source_outputs,
                                                                                  encoder, decoder, weights, bucket_id, mc_search=True,default_labels= 0)

            # 2.2.Sample (null, ^Y) through ^Y ~ G(*|null)
            null_train_query, null_train_answer, null_train_labels = disc_train_data(sess, gen_model, vocab, null_source_inputs, null_source_outputs,
                                                                                     encoder, decoder, weights, bucket_id, mc_search=True, default_label = 0)

            print("=============================mc_search: True====================================")
            if current_step % 200 == 0:
                for i in xrange(len(train_query)):
                    print("lable: ", train_labels[i])
                    print(" ".join([tf.compat.as_str(rev_vocab[output]) for output in train_answer[i]]))

            train_query = np.transpose(train_query)
            train_answer = np.transpose(train_answer)
            neg_train_query = np.transpose(neg_train_query)
            neg_train_answer = np.transpose(neg_train_answer)
            null_train_query = np.transpose(null_train_query)
            null_train_answer = np.transpose(null_train_answer)

            #it is unable to run disc_step
#            t_query = np.concatenate((train_query, neg_train_query, null_train_query),axis=0)
#            t_answer = np.concatenate((train_answer, neg_train_answer, null_train_answer),axis=0)
#            t_labels = np.concatenate((train_labels, neg_train_labels, null_train_labels),axis=0)
            
            # 3.Compute Reward r for (X, ^Y ) using D.---based on Monte Carlo search
            reward, _, gen_num  = disc_step(sess, bucket_id, disc_model, train_query, train_answer, train_labels, forward_only=True)
            neg_reward, _, neg_gen_num  = disc_step(sess, bucket_id, disc_model, neg_train_query, neg_train_answer, neg_train_labels, forward_only=True)
            null_reward, _, null_gen_num  = disc_step(sess, bucket_id, disc_model, null_train_query, null_train_answer, null_train_labels, forward_only=True)
            
            total_gen_num = gen_num + neg_gen_num + null_gen_num
            
            per_gen_num = gen_num / total_gen_num
            per_neg_gen_num = neg_gen_num /total_gen_num
            per_null_gen_num = null_gen_num / total_gen_num
            
            reward = (reward * per_gen_num + neg_reward * per_neg_gen_num + null_reward * per_null_gen_num) 
            batch_reward += reward / gen_config.steps_per_checkpoint

            # 4.Update G on (X, ^Y ) using reward r
            gan_adjusted_loss, gen_step_loss, _ =gen_model.step(sess, encoder, decoder, weights, bucket_id, forward_only=False,
                                           reward=reward, up_reward=True, debug=True)
            gen_loss += gen_step_loss / gen_config.steps_per_checkpoint
            print("gen_step_loss: ", gen_step_loss)
            print("gen_step_adjusted_loss: ", gan_adjusted_loss)

            # 5.Teacher-Forcing: Update G on (X, Y )
            t_adjusted_loss, t_step_loss, a = gen_model.step(sess, encoder, decoder, weights, bucket_id, forward_only=False)
            t_loss += t_step_loss / gen_config.steps_per_checkpoint
           
            print("t_step_loss: ", t_step_loss)
            print("t_adjusted_loss", t_adjusted_loss)           # print("normal: ", a)

            if current_step % gen_config.steps_per_checkpoint == 0:

                step_time += (time.time() - start_time) / gen_config.steps_per_checkpoint

                print("current_steps: %d, step time: %.4f, disc_loss: %.3f, gen_loss: %.3f, t_loss: %.3f, reward: %.3f"
                      %(current_step, step_time, disc_loss, gen_loss, t_loss, batch_reward))

                disc_loss_value = disc_loss_summary.value.add()
                disc_loss_value.tag = disc_config.name_loss
                disc_loss_value.simple_value = float(disc_loss)
                disc_writer.add_summary(disc_loss_summary, int(sess.run(disc_model.global_step)))

                gen_global_steps = sess.run(gen_model.global_step)
                gen_loss_value = gen_loss_summary.value.add()
                gen_loss_value.tag = gen_config.name_loss
                gen_loss_value.simple_value = float(gen_loss)
                t_loss_value = gen_loss_summary.value.add()
                t_loss_value.tag = gen_config.teacher_loss
                t_loss_value.simple_value = float(t_loss)
                batch_reward_value = gen_loss_summary.value.add()
                batch_reward_value.tag = gen_config.reward_name
                batch_reward_value.simple_value = float(batch_reward)
                gen_writer.add_summary(gen_loss_summary, int(gen_global_steps))

                if current_step % (gen_config.steps_per_checkpoint * 2) == 0:
                    print("current_steps: %d, save disc model" % current_step)
                    disc_ckpt_dir = os.path.abspath(os.path.join(disc_config.train_dir, "checkpoints"))
                    if not os.path.exists(disc_ckpt_dir):
                        os.makedirs(disc_ckpt_dir)
                    disc_model_path = os.path.join(disc_ckpt_dir, "disc.model")
                    disc_model.saver.save(sess, disc_model_path, global_step=disc_model.global_step)

                    print("current_steps: %d, save gen model" % current_step)
                    gen_ckpt_dir = os.path.abspath(os.path.join(gen_config.train_dir, "checkpoints"))
                    if not os.path.exists(gen_ckpt_dir):
                        os.makedirs(gen_ckpt_dir)
                    gen_model_path = os.path.join(gen_ckpt_dir, "gen.model")
                    gen_model.saver.save(sess, gen_model_path, global_step=gen_model.global_step)

                step_time, disc_loss, gen_loss, t_loss, batch_reward = 0.0, 0.0, 0.0, 0.0, 0.0
                sys.stdout.flush()



def main(_):
    # step_1 training gen model
    #gen_pre_train()

    # model test
    #gen_test()

    # step_2 gen training data for disc
    #gen_disc()

    # step_3 training disc model
    #disc_pre_train()

    # step_4 training al model
    al_train()

    # model test
    # gen_test()
if __name__ == "__main__":
    tf.app.run()
