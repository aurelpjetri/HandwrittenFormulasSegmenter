import os
import fnmatch
import numpy as np

import util
from parserXml import ParserXml
import los_graph
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt



# Ground truth is a dictionary:: key='id symbol': value='list of traces IDs'
def extract_ground_truth(filename):
    INKML_NAMESPACE = '{http://www.w3.org/2003/InkML}'
    tree = ET.parse(filename)
    root = tree.getroot()
    groups_root = root.find(INKML_NAMESPACE + 'traceGroup')
    trace_groups = groups_root.findall(INKML_NAMESPACE + 'traceGroup')
    ground_truth = {}
    i = 0
    for symbol in trace_groups:
        trace_list = []
        for traceView in symbol.findall(INKML_NAMESPACE + 'traceView'):
            trace_id = int(traceView.get('traceDataRef'))
            trace_list.append(trace_id)
        ground_truth[i] = trace_list
        i += 1
    return ground_truth


# extracts the features (as an array) and labels from the training file
def parse_file(filename):
    parser = ParserXml()
    math_expression = parser.parse_xml(filename)

    # pre-processing...
    math_expression.preprocess()
    # interpolated_expression = math_expression.interpolate_traces()

    # build the line of sight graph
    edges = los_graph.get_los_graph(math_expression)

    # extract the ground truth
    ground_truth = extract_ground_truth(filename)

    # get the features and labels for the training set
    n_features = len(math_expression.get_features(edges[0][0], edges[0][1]))
    features_matrix = np.zeros((len(edges), n_features))
    labels_array = np.zeros((len(edges), 1), dtype=np.str_)
    for k in range(len(edges)):
        features_matrix[k, :] = np.array(math_expression.get_features(edges[k][0], edges[k][1]))
        tmp_label = '_'
        for symbol, group in ground_truth.items():
            # check if the strokes of the edge are in the same symbol
            if all(stroke in group for stroke in edges[k]):
                tmp_label = '*'
                labels_array[k, 0] = '*'  # merge
        labels_array[k, 0] = tmp_label
    return features_matrix, labels_array

# given the directory of the files extracts the training set for the classifier
def get_training_set(directory_path):
    files_list = os.listdir(directory_path)
    interest_list = []
    for f in files_list:
        if fnmatch.fnmatch(f, '*.inkml'):
            interest_list.append(f)

    n_samples = 1000

    filename = directory_path + '/' + interest_list[0]
    training_set, training_labels = parse_file(filename)
    #training_set = normalize_set(training_set)

    for i in range(1, n_samples):
        print (float(i)*100.0/float(n_samples)), '%', '    ', '( ', interest_list[i], ' )'
        filename = directory_path + '/' + interest_list[i]
        features_matrix, labels_array = parse_file(filename)
        training_set = np.concatenate((training_set, features_matrix))
        #training_set = normalize_set(training_set)
        training_labels = np.concatenate((training_labels, labels_array))
    return training_set, training_labels


# exstracts the remaining files from the directoy to test the classifier
def get_testing_set(directory_path):
    files_list = os.listdir(directory_path)
    interest_list = []
    for f in files_list:
        if fnmatch.fnmatch(f, '*.inkml'):
            interest_list.append(f)

    # we use the remaining 338 files of the directory
    n_samples = len(interest_list) - 1000

    filename = directory_path + '/' + interest_list[1000]
    test_set, test_labels = parse_file(filename)
    #test_set = normalize_set(test_set)

    for i in range(1000, 1000 + n_samples):
        print (float(i - 1000)*100.0/float(n_samples)), '%', '    ', '( ', interest_list[i], ' )'
        filename = directory_path + '/' + interest_list[i]
        features_matrix, labels_array = parse_file(filename)
        test_set = np.concatenate((test_set, features_matrix))
        #test_set = normalize_set(test_set)
        test_labels = np.concatenate((test_labels, labels_array))
    return test_set, test_labels


# FOR DEBUGGING
def plot_expression_from_filename(filename):
    parser = ParserXml()
    math_expression = parser.parse_xml(filename)

    # pre-processing...
    math_expression.preprocess()
    util.plot_expression(math_expression.get_traces())
    # edges = los_graph.get_los_graph(math_expression)

    plt.show()


# write the dataset on a text file
def write_dataset_on_file(file_path, training, labels):
    print "Saving main .... "
    # now that all the samples have been collected, write them all
    # in the output file
    try:
        file = open(file_path, 'w')
    except:
        print("File <" + file_path + "> could not be created")
        return

    content = ''
    # print as headers the types for each feature...
    # content += '\r\n'
    for k, sample in enumerate(training):
        line = ''
        for i, v in enumerate(sample):
            if i > 0:
                line += '; '
            if v.__class__.__name__ == "list":
                # multiple values...
                for j, sv in enumerate(v):
                    if j > 0:
                        line += '; '
                    line += str(sv)
            else:
                # single value...
                line += str(v)
        line += '; '
        line += str(labels[k, 0])
        line += '\r\n'
        content += line
        if len(content) >= 50000:
            file.write(content)
            content = ''
    file.write(content)
    file.close()


# parse the text file containing the dataset
def load_dataset_from_file(filename):
    data_file = open(filename, 'r')
    lines = data_file.readlines()
    data_file.close()

    feature_s = lines[0].split(';')
    feature_s = [s.strip() for s in feature_s]

    n_features = len(feature_s) - 1
    n_samples = len(lines)

    samples = np.zeros((n_samples, n_features))
    labels = []

    count_samples = 0
    for i in xrange(0, n_samples):
        values_s = lines[i].split(';')
        if len(values_s) == 1:
            if values_s[0].strip() == "":
                # skip empty line
                continue
        # last value is edge's label
        label = values_s[-1].strip()
        del values_s[-1]

        # read values...
        values = []
        for idx in range(n_features):
            values.append(float(values_s[idx].strip()))

        # validate number of attributes on the sample
        if len(values) != n_features:
            print("Number of values is different to number of attributes")
            print("Atts: " + str(n_features))
            print("Values: " + str(len(values)))
            return None, None, None

        # add sample
        for ft in xrange(n_features):
            samples[count_samples, ft] = values[ft]

        count_samples += 1

        labels.append(label)
    return samples, labels


