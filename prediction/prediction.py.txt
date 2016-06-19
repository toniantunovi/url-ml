'''Prediction for Flask.'''
import sys
import datetime
import numpy as np
import tensorflow as tf
from model.url_rnn import UrlRnn
from configuration.configuration_manager import ConfigurationManager

properties = "/home/toniantunovic/ml-server_test_five/data/properties/dola_properties.qa.json"
configuration_manager = ConfigurationManager(properties)

config = configuration_manager.get_prediction_config()

n_input = int(config["n_input"])
n_steps = int(config["n_steps"])
n_output = int(config["n_output"])
n_char = int(config["n_char"])
n_test = int(config["n_prediction"])
reload_hours = int(config["reload_hours"])
reload_minutes = int(config["reload_minutes"])
reload_seconds = int(config["reload_seconds"])

model_filename = config["model_filename"]

last_reload = datetime.datetime.utcnow()

lookup = None
urlRnn = None
test_pred = None
saver = None
sess = None

def load_model():
    global sess
    global saver
    global model_filename

    saver.restore(sess, model_filename)
    print "Loaded model."

with tf.variable_scope("urlRnn_variables") as scope:
    lookup = tf.placeholder(tf.int32, shape=[None, n_steps])
    urlRnn = UrlRnn(n_input, n_steps, n_output, n_char, n_test=n_test)

    test_pred = urlRnn.get_test_pred(lookup)
    saver = tf.train.Saver()
    sess = tf.InteractiveSession()
    load_model()

def get_lookup(batch_x, batch_size, n_steps, n_char):
    '''Get lookup for batch.'''
    batch_lookup = np.array([[]])
    for x in batch_x:
        url_chars = np.array([])
        for c in x:
            if ord(c) >= n_char:
                continue
            url_chars = np.append(url_chars, ord(c))
        url_chars.resize(n_steps)
        batch_lookup = np.append(batch_lookup, url_chars)

    batch_lookup = batch_lookup.reshape(batch_size, n_steps)

    return batch_lookup

def normalize_url(url):
    url = url.lower()
    url = url.replace(" ", "%20")
    if "//" in url[0:8]:
        url = url[url.find("//")+2:]

    if "www." in url[0:8]:
        url = url[url.find("www.")+4:]

    return url

def predict(urls):
    '''Make prediction of class for urls.'''
    global lookup
    global urlRnn
    global test_pred
    global sess
    global last_reload
    global reload_hours
    global reload_minutes
    global reload_seconds

    for i in range(len(urls)):
        urls[i] = normalize_url(urls[i])

    if datetime.datetime.utcnow() - last_reload > datetime.timedelta(hours=reload_hours,
                                                                     minutes=reload_minutes,
                                                                     seconds=reload_seconds):
        load_model()
        last_reload = datetime.datetime.utcnow()

    with tf.variable_scope("urlRnn_variables") as scope:
        scope.reuse_variables()
        pred_lookup = get_lookup(urls, n_test, n_steps, n_char)
        [[p1, p2]] = test_pred.eval(session=sess, feed_dict={lookup: pred_lookup})
        return [p1, p2]

def main(args):
    '''Test function for predict function.'''
    if len(args) != 2:
        print "Please use this script in following way: prediction.py <url>"
        exit()

    [p1, p2] = predict([args[1]])
    print "%.2f" % round(p1, 2)
    print "%.2f" % round(p2, 2)

if __name__ == '__main__':
    main(sys.argv)
