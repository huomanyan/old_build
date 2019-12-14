import os
import tensorflow as tf
import sys
import urllib
# Define a simple convolutional layer
LOGDIR = 'd:/tensorboard/'

### MNIST EMBEDDINGS ###
mnist = tf.contrib.learn.datasets.mnist.read_data_sets(train_dir=LOGDIR + 'mnist', one_hot=True)

def conv_layer(input, channels_in, channels_out):
    w = tf.Variable(tf.zeros([5, 5, channels_in, channels_out]))
    b = tf.Variable(tf.zeros([channels_out]))
    conv = tf.nn.conv2d(input, w, strides=[1, 1, 1, 1], padding="SAME")
    act = tf.nn.relu(conv + b)
    return act

# And a fully connected layer
def fc_layer(input, channels_in, channels_out):
    w = tf.Variable(tf.zeros([channels_in, channels_out]))
    b = tf.Variable(tf.zeros([channels_out]))
    act = tf.nn.relu(tf.matmul(input, w) + b)
    return act

# Setup placeholders, and reshape the data
x = tf.placeholder(tf.float32, shape=[None, 784])
y = tf.placeholder(tf.float32, shape=[None, 10])
x_image = tf.reshape(x, [-1, 28, 28, 1])
# Create the network
conv1 = conv_layer(x_image, 1, 32)
pool1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
conv2 = conv_layer(pool1, 32, 64)
pool2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")
flattened = tf.reshape(pool2, [-1, 7 * 7 * 64])
fc1 = fc_layer(flattened, 7 * 7 * 64, 1024)
y_predicted = fc_layer(fc1, 1024, 10)

cross_entropy = -tf.reduce_sum(y*tf.log(y_predicted))
# Compute cross entropy as our loss function
# cross_entropy = tf.reduce_mean(
# tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y))
# Use an AdamOptimizer to train the network
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
# compute the accuracy
correct_prediction = tf.equal(tf.argmax(y_predicted, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# tf.reset_default_graph()
sess = tf.Session()
writer = tf.summary.FileWriter(LOGDIR + "2")
writer.add_graph(sess.graph)

# Initialize all the variables
sess.run(tf.global_variables_initializer())
# Train for 2000 steps
for i in range(2001):
    batch = mnist.train.next_batch(100)
    # Occasionally report accuracy
    if i % 100 == 0:
        [train_accuracy] = sess.run([accuracy], feed_dict={x: batch[0], y: batch[1]})
        print("step %d, training accuracy %g" % (i, train_accuracy))
    # Run the training step
    sess.run(train_step, feed_dict={x: batch[0], y: batch[1]})