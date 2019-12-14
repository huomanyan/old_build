# -*- coding: utf-8 -*-
"""
Created on Tue May 14 12:42:07 2019

@author: lenovo
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets


def X_W(X):
    with tf.variable_scope('scp', reuse=tf.AUTO_REUSE) as scp:
        W = tf.get_variable('w', initializer=tf.zeros([392, 10]))
        return tf.matmul(X, W)


tf.reset_default_graph()

mnist = read_data_sets("mnist_data/", one_hot=True)

X1 = tf.placeholder(dtype='float', shape=[None, 392])
X2 = tf.placeholder(dtype='float', shape=[None, 392])
# w = tf.Variable(tf.zeros([784, 10]), name='weight')
b = tf.Variable(tf.zeros([10]))

y = tf.nn.softmax(X_W(X1)+X_W(X2)+b, name='prediction')

y_ = tf.placeholder(dtype='float', shape=[None, 10], name='label')

cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
train_step = tf.train.GradientDescentOptimizer(learning_rate=0.01).minimize(cross_entropy)

with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    step = 1500
    for i in range(step):
        batch_xs, batch_ys = mnist.train.next_batch(100)  # shape: (100,784) (100,10)
        _, loss, pred = sess.run([train_step, cross_entropy, y],
                                 feed_dict={X1: batch_xs[:, 0:392], X2: batch_xs[:, 392:784], y_: batch_ys})
        if i % 100 == 0:
            correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(batch_ys, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
            print("Step", i, "Training Accuracy", sess.run(accuracy))

    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
    print('[accuracy, loss]]:', sess.run([accuracy, cross_entropy],
                                         feed_dict={X1: mnist.test.images[:, 0:392], X2: mnist.test.images[:, 392:784],
                                                    y_: mnist.test.labels}))
