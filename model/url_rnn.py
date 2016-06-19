"""This module contains url recurrent neural network class."""
import tensorflow as tf
from tensorflow.models.rnn import rnn_cell
from model import Model

class UrlRnn(object):
    """UrlRnn class with different setting for train, test and validation, but
    with shared TensorFlow variables."""
    def __init__(self, n_input=None, n_steps=None, n_output=None,
                 n_char=None, n_train_batch=1, n_validation=1, n_test=None):
        # model hyperparametes
        self.n_input = n_input
        self.n_steps = n_steps
        self.n_output = n_output
        self.n_char = n_char

        # model parameters
        self.embeddings = tf.Variable(tf.random_uniform([n_char, n_input], -1.0, 1.0))
        self.lstm_cell = rnn_cell.BasicLSTMCell(n_input, forget_bias=1.0)
        self.weights = {
            'out': tf.Variable(tf.random_normal([n_input, n_output]))
        }
        self.biases = {
            'out': tf.Variable(tf.random_normal([n_output]))
        }

        # train, validation and test models
        self.model_train = Model(n_train_batch, self.weights,
                                 self.biases, self.lstm_cell)
        self.model_validation = Model(n_validation, self.weights,
                                      self.biases, self.lstm_cell)
        self.model_test = Model(n_test, self.weights, self.biases, self.lstm_cell)

    def get_train_pred(self, lookup):
        """Get prediction for training setup."""
        embed = tf.nn.embedding_lookup(self.embeddings, lookup)
        return self.model_train.get_pred(self.n_input, self.n_steps, embed)

    def get_validation_pred(self, lookup):
        """Get prediction for validation setup."""
        embed = tf.nn.embedding_lookup(self.embeddings, lookup)
        return self.model_validation.get_pred(self.n_input, self.n_steps, embed)

    def get_test_pred(self, lookup):
        """Get prediction for testing setup."""
        embed = tf.nn.embedding_lookup(self.embeddings, lookup)
        return self.model_test.get_pred(self.n_input, self.n_steps, embed)
