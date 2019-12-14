# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:51:16 2019

@author: lenovo
"""

import tensorflow as tf
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
import numpy as np
from sklearn.utils import shuffle
from lenet_slim import lenet5


tf.reset_default_graph()

mnist = read_data_sets("data/", one_hot=True)

x = tf.placeholder(tf.float32, shape=[None, 32, 32, 1], name='x')
y_ = tf.placeholder(tf.float32, shape=[None, 10], name='y_')
keep_prob = tf.placeholder(tf.float32, name='keep_prob')

logits = lenet5(x, keep_prob)
y_predicted = tf.nn.softmax(logits)

loss = tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=logits)
loss = tf.reduce_mean(loss)

correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))

train_step = tf.train.GradientDescentOptimizer(learning_rate=0.01).minimize(loss)

with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    step = 4000
    for i in range(step):
        raw_batch_xs, batch_ys = mnist.train.next_batch(100)  # shape: (100,784) (100,10)
        # reshape batch_xs into [None, 32, 32, 1]
        batch_xs = raw_batch_xs.reshape(-1, 28, 28, 1)
        batch_xs = np.pad(batch_xs, ((0, 0), (2, 2), (2, 2), (0, 0)), 'constant')

        batch_xs, batch_ys = shuffle(batch_xs, batch_ys)

        _, ls, acur = sess.run([train_step, loss, accuracy], feed_dict={x: batch_xs, y_: batch_ys, keep_prob: 0.5})
        if i % 100 == 0:
            print("Step", i, "Training [accuracy, loss]: [", acur, ",", ls, "]")
            
    raw_test_xs = mnist.test.images
    test_xs = raw_test_xs.reshape(-1, 28, 28, 1)
    test_xs = np.pad(test_xs, ((0,0),(2,2),(2,2),(0,0)), 'constant')
    print('Testing [accuracy, loss]:', sess.run([accuracy, loss], feed_dict={x:test_xs, y_:mnist.test.labels, keep_prob:1.0}))
