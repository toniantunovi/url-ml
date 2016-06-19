"""Model definition for UrlRnn"""
import tensorflow as tf
from tensorflow.models.rnn import rnn

class Model(object):
    """Model to calculate forward pass in UrlRnn."""
    def __init__(self, size, weights, biases, lstm_cell):
        self.size = size
        self.lstm_cell = lstm_cell
        self.istate = self.lstm_cell.zero_state(self.size, tf.float32)
        self.weights = weights
        self.biases = biases

    @staticmethod
    def reshape_data(n_input, n_steps, data):
        """Reshape data to required form for rnn"""
        input_val = tf.transpose(data, [1, 0, 2])
        input_val = tf.reshape(input_val, [-1, n_input])
        return tf.split(0, n_steps, input_val)

    def get_pred(self, n_input, n_steps, input_val):
        """Perform forward pass and return output of UrlRnn."""
        input_val = Model.reshape_data(n_input, n_steps, input_val)

        outputs, _ = rnn.rnn(self.lstm_cell, input_val, initial_state=self.istate)

        return tf.nn.softmax(tf.matmul(outputs[-1], self.weights['out']) + self.biases['out'])
