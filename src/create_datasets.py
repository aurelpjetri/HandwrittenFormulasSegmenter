#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dataset_utils as du
# python script for the creation of training and testing data-sets

DIRECTORY = 'DATASET_DIRECTORY'

# # uncomment the 2 lines below to create the training set:
training, label_s = du.get_training_set(DIRECTORY)
du.write_dataset_on_file('NAME_OF_TRAIN_PATH', training, label_s)

# uncomment the 2 lines below to create the testing set:
tests, tlabel_s = du.get_testing_set(DIRECTORY)
du.write_dataset_on_file('NAME_OF_TEST_PATH', tests, tlabel_s)