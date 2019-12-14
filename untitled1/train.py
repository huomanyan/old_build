# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:51:16 2019

@author: lenovo
"""

import tensorflow as tf
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
import numpy as np
from sklearn.utils import shuffle
from lenet_slim import Lenet


tf.reset_default_graph() 

mnist = read_data_sets("data/", one_hot=True)
lenet = Lenet()

with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)
    
    step = 4000
    for i in range(step):
        raw_batch_xs, batch_ys = mnist.train.next_batch(100) #shape: (100,784) (100,10)
        # reshape batch_xs into [None, 32, 32, 1]
        batch_xs = raw_batch_xs.reshape(-1, 28, 28, 1)
        batch_xs = np.pad(batch_xs, ((0,0),(2,2),(2,2),(0,0)), 'constant')
        
        batch_xs, batch_ys = shuffle(batch_xs, batch_ys)
        
        _, loss, acur = sess.run([lenet.train_step, lenet.loss, lenet.accuracy], feed_dict={lenet.x:batch_xs, lenet.y_:batch_ys, lenet.keep_prob:0.5})
        if i%100==0:
            print("Step", i, "Training [accuracy, loss]: [", acur, ",", loss, "]")
        
    raw_test_xs = mnist.test.images
    test_xs = raw_test_xs.reshape(-1, 28, 28, 1)
    test_xs = np.pad(test_xs, ((0,0),(2,2),(2,2),(0,0)), 'constant')
    print('Testing [accuracy, loss]:', sess.run([lenet.accuracy, lenet.loss], feed_dict={lenet.x:test_xs, lenet.y_:mnist.test.labels, lenet.keep_prob:1.0}))   
        