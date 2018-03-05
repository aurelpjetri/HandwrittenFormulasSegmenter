import cPickle
from sklearn.ensemble import RandomForestClassifier
import dataset_utils as ds
import time
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np

#python principal script for classification with random forest

forest1 = RandomForestClassifier(n_estimators=50, criterion='gini', max_features=105, max_depth=40)

classifiers = []
classifiers.append(forest1)

for classifier in classifiers:
    print 'experiment number: ',classifiers.index(classifier)
    print 'Loading training set...'
    training_set, training_labels = ds.load_dataset_from_file('TRAININGSET_PATH')

    print'Starting to train the classifier...'
    start_training_time = time.time()
    classifier.fit(training_set, training_labels)
    end_training_time = time.time()
    total_training_time = end_training_time - start_training_time
    print 'total training time: ',total_training_time

    print'Loading testing set...'
    testing_set, testing_labels = ds.load_dataset_from_file('TESTSET_PATH')


    print 'Starting tests1...'
    predictions = classifier.predict(testing_set)


    correct_count = 0
    error_in_merge = 0
    error_in_split = 0
    correct_merge = 0
    correct_split = 0
    for i in xrange(len(predictions)):
        if predictions[i] == testing_labels[i]:
            correct_count += 1
        if predictions[i] == '_' and testing_labels[i] == '_':
            correct_split += 1
        if predictions[i] == '*' and testing_labels[i] == '*':
            correct_merge += 1
        else:
            if predictions[i] == '*' and testing_labels[i] == '_':
                error_in_split += 1
            if predictions[i] == '_' and testing_labels[i] == '*':
                error_in_merge += 1

    print correct_count, ' correct predictions out of ', len(testing_labels)
    print 'precision: ', float(correct_count)*100.0/float(len(testing_labels)), '%\n'

    print correct_split, ' split predicions out of ', correct_count, ' correct predictions'
    print 'total correct split: ',float(correct_split*100)/float(correct_count), '% of correct predictions'
    print 'total correct split: ',float(correct_split*100)/float(len(testing_labels)), '% of all predictions\n'

    print correct_merge, ' merge predicitons  out of ', correct_count, ' correct predicions'
    print 'total correct merge: ', float(correct_merge * 100) / float(correct_count), '% of correct predictions'
    print 'total correct merge: ', float(correct_merge * 100) / float(len(testing_labels)), '% of all predictions\n'

    print error_in_split, ' errors in split out of ', len(testing_labels)-correct_count
    print 'error in split: ', float(error_in_split)*100.0/float(len(testing_labels) - correct_count), '% of all errors'
    print 'error in split: ', float(error_in_split) * 100.0 / float(len(testing_labels)), '% of all predictions\n'

    print error_in_merge, ' errors in merge out of ', len(testing_labels) - correct_count
    print 'error in merge: ', float(error_in_merge) * 100.0 / float(len(testing_labels) - correct_count), '% of all errors'
    print 'error in merge: ', float(error_in_merge) * 100.0 / float(len(testing_labels)), '% of all predictions'

    experiment_names = ['correct_merge', 'correct_split', 'merge_errors', 'split_errors']
    experiment_results = [correct_merge*100/float(len(testing_labels)), correct_split*100/float(len(testing_labels)),
                          error_in_merge * 100 / float(len(testing_labels)), error_in_split * 100 / float(len(testing_labels))]


    print 'end experiment\n'
    print '________________________________________________________________________________________\n'


# TO SAVE THE CLASSIFIER
out_file = open('filename.pkl', 'wb')
cPickle.dump(forest1, out_file, cPickle.HIGHEST_PROTOCOL)
out_file.close()
