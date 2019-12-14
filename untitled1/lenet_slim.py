# -*- coding: utf-8 -*-
"""
Created on Thu May 16 11:12:49 2019

@author: lenovo
"""

import tensorflow as tf
from tensorflow.contrib.layers import flatten
import tensorflow.contrib.slim as slim
import numpy as np

#slim = tf.contirb.slim

def lenet5(inputs,keep_prob):
    with slim.arg_scope([slim.conv2d, slim.fully_connected],
                        activation_fn=tf.nn.relu,
                        weights_initializer=tf.truncated_normal_initializer(0.0, 0.1),
                        weights_regularizer=slim.l2_regularizer(0.05)):
        net = slim.conv2d(inputs, 6, [5, 5], padding='VALID', scope='layer1-conv')
        net = slim.max_pool2d(net, 2, stride=2, scope='layer2-max-pool')
        net = slim.conv2d(net, 16, [5, 5], padding='VALID', scope='layer3-conv')
        net = slim.max_pool2d(net, 2, stride=2, scope='layer4-max-pool')
        net = slim.flatten(net, scope='flatten')
        net = slim.fully_connected(net, 120, scope='layer5')
        net = slim.dropout(net, keep_prob, scope='dropout6')
        net = slim.fully_connected(net, 84, scope='layer7')
        net = slim.dropout(net, keep_prob, scope='dropout8')
        net = slim.fully_connected(net, 10, activation_fn=None, scope='output')

    return net
