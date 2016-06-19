'''This module contains Optimizer class for UrlRnn.'''
import os.path
import numpy as np
import tensorflow as tf
from model.url_rnn import UrlRnn

class ContinuousOptimizer(object):
    '''Optimizer class for UrlRnn.'''
    def __init__(self, configuration_manager, datasource_manager):
        self.config = configuration_manager.get_optimization_config()
        self.datasource = datasource_manager

    @staticmethod
    def _normalize_url(url):
        url = url.lower()
        url = url.replace(" ", "%20")
        if "//" in url[0:8]:
            url = url[url.find("//")+2:]

        if "www." in url[0:8]:
            url = url[url.find("www.")+4:]

        return url

    def get_data(self, batch, batch_size, n_char):
        '''Get data for training or testing. Return lookup-label pairs.'''
        # Get batch urls and labels
        batch_x = batch[0]
        batch_y = batch[1]

        batch_lookup = np.array([[]])
        batch_y = np.array(batch_y).reshape(batch_size, int(self.config['n_output']))

        for i in range(len(batch_x)):
            batch_x[i] = ContinuousOptimizer._normalize_url(batch_x[i])

        for b_x in batch_x:
            url_chars = np.array([])
            for x_c in b_x:
                if ord(x_c) >= n_char:
                    continue
                url_chars = np.append(url_chars, ord(x_c))
            url_chars.resize(int(self.config['n_steps']))
            batch_lookup = np.append(batch_lookup, url_chars)

        batch_lookup = batch_lookup.reshape(batch_size, int(self.config['n_steps']))

        return [batch_lookup, batch_y]

    def load_model(self, sess, saver):
        '''Load previously saved model.'''
        model_filename = self.config["model_filename"]
        saver.restore(sess, model_filename)
        print "Loaded model."

    def save_model(self, sess, saver):
        '''Check if models should be saved. If so, save the model.'''
        model_filename = self.config["model_filename"]
        save_path = saver.save(sess, model_filename)
        print "Model saved to: " + save_path

    def run(self):
        '''Perform optimization based on properties file.'''
        # optimization parameters
        optimizer_name = self.config["optimizer"]
        learning_rate = float(self.config["learning_rate"])
        batch_size = int(self.config["batch_size"])

        # model hyperparameters
        n_input = int(self.config["n_input"])
        n_steps = int(self.config["n_steps"])
        n_output = int(self.config["n_output"])
        n_char = int(self.config["n_char"])

        display_step = int(self.config["display_step"])

        save_threshold = float(self.config["save_threshold"])

        n_validation = int(self.config["n_validation"])

        # parameter not currently used
        n_test = 1000

        with tf.variable_scope("urlRnn_variables") as scope:
            # placeholders
            label_y = tf.placeholder("float", [None, n_output])
            lookup = tf.placeholder(tf.int32, shape=[None, n_steps])

            # ml algorithm defition
            url_rnn = UrlRnn(n_input, n_steps, n_output, n_char, batch_size,
                             n_validation, n_test)
            train_pred = url_rnn.get_train_pred(lookup)
            train_cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits
                                        (train_pred, label_y))

            if optimizer_name == "GradientDescentOptimizer":
                optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(train_cost)
            elif optimizer_name == "AdamOptimizer":
                optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(train_cost)
            else:
                raise Exception("Unsupported optimizer name=" + optimizer_name)

            # enables reuse of model parameters for different settings
            scope.reuse_variables()

            validation_pred = url_rnn.get_validation_pred(lookup)
            validation_correct_prediction = tf.equal(tf.argmax(label_y, 1),
                                                     tf.argmax(validation_pred, 1))
            validation_accuracy = tf.reduce_mean(tf.cast(validation_correct_prediction, "float"))

            # saving learned model parameters
            saver = tf.train.Saver()

            # initializing the variables
            init = tf.initialize_all_variables()
            iterations = 0
            acc_no_imp = 0
            best_acc = 0

            # Launch the graph
            with tf.Session() as sess:
                sess.run(init)

                if os.path.isfile(self.config["model_filename"]):
                    self.load_model(sess, saver)

                validation_lookup, validation_ys = self.get_data(self.datasource.get_validation_dataset(n_validation),
                                                                 n_validation, n_char)

                # Keep training indefinitely
                while iterations < self.config["max_iterations"]:
                    batch_lookup, batch_ys = self.get_data(self.datasource.get_next_batch(batch_size), batch_size, n_char)

                    # Fit training using batch data
                    sess.run(optimizer, feed_dict={lookup: batch_lookup,
                                                   label_y: batch_ys})

                    if iterations % display_step == 0:
                        accuracy = validation_accuracy.eval(feed_dict={lookup: validation_lookup,
                                                                       label_y: validation_ys})

                        print "Iteration: " + str(iterations) + ". Validation set accuracy: " + str(accuracy)

                        if accuracy > best_acc:
                            best_acc = accuracy
                            acc_no_imp = 0
                            if accuracy >= save_threshold:
                                self.save_model(sess, saver)
                        else:
                            acc_no_imp += 1

                        if acc_no_imp > self.config["acc_no_imp_limit"]:
                            break

                    iterations += 1
