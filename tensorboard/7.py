import os
import tensorflow as tf
import sys
import urllib
# Define a simple convolutional layer
LOGDIR = 'd:/tensorboard/'

### MNIST EMBEDDINGS ###
mnist = tf.contrib.learn.datasets.mnist.read_data_sets(train_dir=LOGDIR + 'mnist', one_hot=True)

def conv_layer(input, channels_in, channels_out, name="conv"):
    with tf.name_scope(name):
        w = tf.Variable(tf.truncated_normal([5, 5, channels_in, channels_out], stddev=0.1), name = "W")
        b = tf.Variable(tf.constant(0.1, shape=[channels_out]), name="B")
        conv = tf.nn.conv2d(input, w, strides=[1, 1, 1, 1], padding="SAME")
        act = tf.nn.relu(conv + b)
        tf.summary.histogram("weights", w)
        tf.summary.histogram("biases", b)
        tf.summary.histogram("activations", act)
        return act

# And a fully connected layer
def fc_layer(input, channels_in, channels_out, name = "fc"):
    with tf.name_scope(name):
        w = tf.Variable(tf.truncated_normal([channels_in, channels_out], stddev=0.1), name="W")
        b = tf.Variable(tf.constant(0.1, shape=[channels_out]), name="B")
        act = tf.nn.relu(tf.matmul(input, w) + b)
        tf.summary.histogram("weights", w)
        tf.summary.histogram("biases", b)
        tf.summary.histogram("activations", act)
        return act

def mnist_training(learning_rate, use_two_conv, hparam):
    tf.reset_default_graph()
    # Setup placeholders, and reshape the data
    x = tf.placeholder(tf.float32, shape=[None, 784])
    y = tf.placeholder(tf.float32, shape=[None, 10])
    x_image = tf.reshape(x, [-1, 28, 28, 1])
    tf.summary.image('input', x_image, 3)

    if use_two_conv:
        # Create the network
        conv1 = conv_layer(x_image, 1, 32, "conv1")
        with tf.name_scope("Pool1"):
            pool1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                   padding="SAME", name = "Pool1")
        conv2 = conv_layer(pool1, 32, 64, "conv2")
        with tf.name_scope("Pool2"):
            pool2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                   padding="SAME")
        flattened = tf.reshape(pool2, [-1, 7 * 7 * 64])

    else:
        conv1 = conv_layer(x_image, 1, 64, "conv1")
        pool1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                   padding="SAME", name="Pool1")
        pool2 = tf.nn.max_pool(pool1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
                                   padding="SAME", name="Pool1")
        flattened = tf.reshape(pool2, [-1, 7 * 7 * 64])

    keep_prob = tf.placeholder("float")
    # fc1_drop = tf.nn.dropout(fc1, keep_prob)
    fc1 = fc_layer(flattened, 7 * 7 * 64, 1024, "fc1")
    # y_predicted = fc_layer(fc1, 1024, 10, "fc2")
    fc2 = fc_layer(fc1, 1024, 10, "fc2")
    y_predicted = tf.nn.softmax(fc2)
    tf.summary.histogram("y_predicted", y_predicted)

    with tf.name_scope("cross_entroy"):
        cross_entropy = -tf.reduce_sum(y * tf.log(y_predicted))
        tf.summary.scalar('cross_entropy', cross_entropy)

    # Compute cross entropy as our loss function
    # cross_entropy = tf.reduce_mean(
    # tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=y))
    # Use an AdamOptimizer to train the network
    train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)
    # compute the accuracy
    with tf.name_scope("accuracy"):
        correct_prediction = tf.equal(tf.argmax(y_predicted, 1), tf.argmax(y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        tf.summary.scalar('accuracy', accuracy)

    merged_summary = tf.summary.merge_all()
    sess = tf.Session()
    writer = tf.summary.FileWriter(LOGDIR + "7/" + hparam)
    writer.add_graph(sess.graph)
    sess.run(tf.global_variables_initializer()) # Initialize all the variables
    # Train for 2000 steps
    for i in range(2001):
        batch = mnist.train.next_batch(100)
        if i % 5 == 0:
            s = sess.run(merged_summary, feed_dict={x: batch[0], y: batch[1], keep_prob: 1.0})
            writer.add_summary(s, i)
        sess.run(train_step, feed_dict={x: batch[0], y: batch[1], keep_prob: 1.0})
        # Occasionally report accuracy
        if i % 100 == 0:
            [train_accuracy] = sess.run([accuracy], feed_dict={x: batch[0], y: batch[1], keep_prob: 1.0})
            print("step %d, training accuracy %g" % (i, train_accuracy))
    # Run the training step

def make_hparam_string(learning_rate, use_two_conv):
  conv_param = "conv=2" if use_two_conv else "conv=1"
  return "lr_%.0E,%s" % (learning_rate, conv_param)

if __name__ == "__main__":
    for learning_rate in [1E-4, 1E-5]:
        for use_two_conv in [True, False]:
                hparam = make_hparam_string(learning_rate, use_two_conv)
                print('Starting run for %s' % hparam)
                mnist_training(learning_rate, use_two_conv, hparam)