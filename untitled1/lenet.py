# -*- coding: utf-8 -*-
"""
Created on Thu May 16 11:12:49 2019

@author: lenovo
"""

import tensorflow as tf
from tensorflow.contrib.layers import flatten
import numpy as np

class Lenet(object):
    def __init__(self, mu=0, sigma=0.1):
        # Arguments used for tf.truncated_normal, randomly defines variables for the weights and biases for each layer 
        self.mu=mu
        self.sigma = sigma
        self._build_graph() 

    def _build_graph(self, network_name='Lenet'):
        self._setup_placeholders_graph()
        self._build_network_graph(network_name)
        self._compute_loss_graph()
        self._compute_acc_graph()
        self._create_train_op_graph()  
    
    def _setup_placeholders_graph(self): 
        self.x = tf.placeholder(tf.float32, shape=[None, 32, 32, 1], name='x') 
        self.y_ = tf.placeholder(tf.float32, shape=[None, 10], name='y_') 
        self.keep_prob = tf.placeholder(tf.float32, name='keep_prob') 
    
    def _cnn_layer(self, scope_name, W_name, b_name, x, filter_shape, conv_strides, padding_tag='VALID'): 
        with tf.variable_scope(scope_name): 
            conv_W = tf.get_variable(W_name, dtype=tf.float32, initializer=tf.truncated_normal(shape=filter_shape, mean= self.mu, stddev=self.sigma))
            conv_b = tf.get_variable(b_name, dtype=tf.float32, initializer=tf.zeros(filter_shape[3])) 
            conv = tf.nn.conv2d(x, conv_W, strides=conv_strides, padding=padding_tag) + conv_b 
            return conv
    
    def _pooling_layer(self, scope_name, x, pool_ksize, pool_strides, padding_tag='VALID'): 
        with tf.variable_scope(scope_name): 
            conv = tf.nn.max_pool(x, ksize=pool_ksize, strides=pool_strides, padding=padding_tag)
            return conv
        
    def _fully_connected_layer(self, scope_name, W_name, b_name, x , W_shape): 
        with tf.variable_scope(scope_name): 
            fc_W = tf.get_variable(W_name, dtype=tf.float32, initializer=tf.truncated_normal(shape=W_shape, mean= self.mu, stddev=self.sigma))
            fc_b = tf.get_variable(b_name, dtype=tf.float32, initializer=tf.zeros(W_shape[1]))
            fc = tf.matmul(x, fc_W) + fc_b 
            return fc
    
    def _build_network_graph(self, scope_name): 
        with tf.variable_scope(scope_name): 
            # SOLUTION: Layer 1: Convolutional. Input = 32x32x1. Output = 28x28x6.
            conv1 = self._cnn_layer('layer_1_conv', 'conv1_w', 'conv1_b', self.x, (5, 5, 1, 6), [1, 1, 1, 1]) 
            # SOLUTION: Activation. 
            self.conv1 = tf.nn.relu(conv1) 
            # SOLUTION: Pooling. Input = 28x28x6. Output = 14x14x6. 
            self.pool1 = self._pooling_layer('layer_1_pooling', self.conv1, [1, 2, 2, 1], [1, 2, 2, 1])
            
            # SOLUTION: Layer 2: Convolutional. Output = 10x10x16. 
            conv2 = self._cnn_layer('layer_2_conv', 'conv2_w', 'conv2_b', self.pool1, (5, 5, 6, 16), [1, 1, 1, 1]) 
            # SOLUTION: Activation. 
            self.conv2 = tf.nn.relu(conv2) 
            # SOLUTION: Pooling. Input = 10x10x16. Output = 5x5x16. 
            self.pool2 = self._pooling_layer('layer_2_pooling', self.conv2, [1, 2, 2, 1], [1, 2, 2, 1])
            
            # SOLUTION: Flatten. Input = 5x5x16. Output = 400. 
            self.fc0 = flatten(self.pool2)
            # SOLUTION: Layer 3: Fully Connected. Input = 400. Output = 120. 
            fc1 = self._fully_connected_layer('layer_3_fc', 'fc1_w', 'fc1_b', self.fc0, (400, 120))
            # SOLUTION: Activation. 
            self.fc1 = tf.nn.relu(fc1)
            self.fc1_drop = tf.nn.dropout(self.fc1, self.keep_prob)
            
            # SOLUTION: Layer 4: Fully Connected. Input = 120. Output = 84.
            fc2 = self._fully_connected_layer('layer_4_fc', 'fc2_w', 'fc2_b', self.fc1_drop, (120, 84))
            # SOLUTION: Activation. 
            self.fc2 = tf.nn.relu(fc2) 
            self.fc2_drop = tf.nn.dropout(self.fc2, self.keep_prob)
            
            # SOLUTION: Layer 5: Fully Connected. Input = 84. Output = 10. 
            self.logits = self._fully_connected_layer('layer_5_fc', 'fc3_w', 'fc3_b', self.fc2_drop, (84, 10))
            self.y_predicted = tf.nn.softmax(self.logits) 
            #tf.summary.histogram("y_predicted", self.y_predicted)
    
    def _compute_loss_graph(self): 
        with tf.name_scope("loss_function"): 
            loss = tf.nn.softmax_cross_entropy_with_logits(labels=self.y_, logits=self.logits) 
            self.loss = tf.reduce_mean(loss) 
            #tf.summary.scalar("cross_entropy", self.loss)
    
    def _compute_acc_graph(self):
        with tf.name_scope("accuracy_function"): 
            correct_prediction = tf.equal(tf.argmax(self.logits, 1), tf.argmax(self.y_, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
            #tf.summary.scalar("accuracy", self.accuracy)
    
    def _create_train_op_graph(self):
        with tf.name_scope("training_option"):
            self.train_step = tf.train.GradientDescentOptimizer(learning_rate=0.01).minimize(self.loss)
            