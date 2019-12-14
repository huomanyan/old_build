import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split 
from tensorflow.python.framework import graph_util 

x = np.linspace((-32)/18, (2*np.pi-32)/18, 2000).reshape(-1, 1)
y = np.cos(18*x+32)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

# y = w1 * x + w2 * x^2 + w3 * x^3 + b
data = tf.placeholder(tf.float32, [None, 1])
label = tf.placeholder(tf.float32, [None, 1])

w1 = tf.Variable(tf.random_normal([1, 1]), dtype=tf.float32, name='weight_1')
w2 = tf.Variable(tf.random_normal([1, 1]), dtype=tf.float32, name='weight_2')
w3 = tf.Variable(tf.random_normal([1, 1]), dtype=tf.float32, name='weight_3')
b = tf.Variable(tf.ones([1]), dtype=tf.float32, name='bias')


label_predict = tf.add(tf.add(tf.add(tf.matmul(data, w1), tf.matmul(tf.multiply(data, data), w2)), 
                          tf.matmul(tf.multiply(tf.multiply(data, data), data), w3)), b, name='predict')
loss = tf.reduce_mean(tf.square(label - label_predict))

train = tf.train.GradientDescentOptimizer(0.0026).minimize(loss)

saver = tf.train.Saver() 

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    
    for i in range(3500000):
        sess.run(train, feed_dict={data: x_train, label: y_train})
        if (i%1000 == 0):
            print(sess.run(loss, feed_dict={data: x_train, label: y_train}))
    
    forecast_set = sess.run(label_predict, feed_dict={data: x})
    plt.figure(figsize=(8,4))
    plt.plot(x, y, label="$cos(18*x+32)$", color="red")
    plt.plot(x, forecast_set, label="predict", color="blue")
    plt.legend()
    plt.show()
    
    save_path = saver.save(sess, './temp/tfregre.ckpt')
    
    constant_graph = graph_util.convert_variables_to_constants(sess, sess.graph_def, ['predict']) 
    with tf.gfile.FastGFile('./temp/pbregre.pb', mode='wb') as f: 
        f.write(constant_graph.SerializeToString())

    