import numpy as np
import cPickle
from parserXml import ParserXml
import util
import los_graph
from sklearn.ensemble import RandomForestClassifier
import dataset_utils as ds
import matplotlib.pyplot as plt

# lo scopo di questo script e' di visualizzare graficamente la segmentazione effettuata dal classificatore

def get_symbols(graph, math_expression, predictions):
    merge_edges = []
    symbols = []

    # get the merging edges
    for j, pred in enumerate(predictions):
        if pred == '*':
            merge_edges.append(graph[j])

    if len(merge_edges) > 0:
        symbols.append(merge_edges[0])
        for el in merge_edges:
            new_symbol_flag = True
            for s in symbols:
                if el[0] in s:
                    if el[1] in s:
                        new_symbol_flag = False
                    else:
                        s.append(el[1])
                        new_symbol_flag = False
                if el[1] in s:
                    if el[0] in s:
                        new_symbol_flag = False
                    else:
                        s.append(el[0])
                        new_symbol_flag = False
            if new_symbol_flag:
                symbols.append(el)

    print symbols

    if len(symbols) > 0:
        for trace_id in math_expression.get_traces_dictionary().keys():
            gengerate_symbol_flag = True
            for sym in symbols:
                if trace_id in sym:
                    gengerate_symbol_flag = False
            if gengerate_symbol_flag:
                symbols.append([trace_id])
    else:
        for trace_id in math_expression.get_traces_dictionary().keys():
            symbols.append([trace_id])
    return symbols


def get_symbol_bounding_box(symbol, math_expression):
    x_s = []
    y_s = []
    for trace_id in symbol:
        trace = math_expression.get_traces_dictionary()[trace_id]
        for point in trace:
            x_s.append(point[0])
            y_s.append(point[1])
    symbol_bounding_box = [min(x_s), max(x_s), min(y_s), max(y_s)]
    return symbol_bounding_box


def plot_segmentations(symbols, math_expression):
    for symbol in symbols:
        sbb = get_symbol_bounding_box(symbol, expression)
        plt.plot([sbb[0], sbb[0], sbb[1], sbb[1], sbb[0]], [sbb[2], sbb[3], sbb[3], sbb[2], sbb[2]], 'r-', lw=0.2)
        # plt.plot([sbb[0], sbb[0]], [sbb[2], sbb[3]], 'r--')  # vertical left
        # plt.plot([sbb[1], sbb[1]], [sbb[2], sbb[3]], 'r--')  # vertical right
        # plt.plot([sbb[0], sbb[1]], [sbb[2], sbb[2]], 'r--')  # horizontal low
        # plt.plot([sbb[0], sbb[1]], [sbb[3], sbb[3]], 'r--')  # horizontal high



# # to load a pre-trained classifier
classifier_file = open('filename.pkl', 'rb')
forest = cPickle.load(classifier_file)
classifier_file.close()

# forest = RandomForestClassifier(n_estimators=50, criterion='gini', max_features=14, max_depth=40)
#
# print 'Loading training set...'
# training_set, training_labels = ds.load_dataset_from_file('')
#
# print'Starting to train the classifier...'
# forest.fit(training_set, training_labels)


filename = ''

parser = ParserXml()
expression = parser.parse_xml(filename)
expression.preprocess()

graph = los_graph.get_los_graph(expression)

nfeatures = len(expression.get_features(graph[0][0], graph[0][1]))

sample = np.zeros((len(graph), nfeatures))
for i, edge in enumerate(graph):
    sample[i, :] = np.array(expression.get_features(edge[0], edge[1]))

predictions = forest.predict(sample)

symbols = get_symbols(graph, expression, predictions)

print symbols

util.plot_expression(expression.get_traces())
plot_segmentations(symbols, expression)

plt.show()
