# Online Handwritten Math Formulas Segmenter
April 21, 2017

This is an implementation of a method for segmenting on-line handwritten math formulas that consists of line of sight stroke graph representation of the formula, feature extraction and training of a random forest classifier.

## 1) Files
The directory in which this file is present contains also the following files:
  • a folder called "project" containing the files:
    - create_dataset.py
    - dataset_utils.py
    - graphic_segmenter.py
    - los_graph.py
    - mathExpression.py
    - parserXml.py
    - randomForest.py
    - util.py
  • a folder called "ICFHR_package" containing the training and testing sets from the CROHME competition. In this project we use only the training files. 
  • this README file

## 2) Prerequisites
  • Python 2.7.10
  • numpy
  • scipy
  • matpotlib
  • sklearn

## 3) Getting Started
The method is divided in two consecutive phases:
  1. creation of the training and testing set.
  2. training and classification phase.

## 4) Running Tests

### 4.1) Dataset Creation
We have to open the "project" folder. In the create_dataset.py file the code is the follower:
  1. import dataset_utils as du
  2. DIRECTORY = ’DIRECTORY_PATH’
  3. training, label_s = du.get_training_set(DIRECTORY)
  4. du.write_dataset_on_file(’TRAIN_PATH’, training, label_s)
  5. tests, tlabel_s = du.get_testing_set(DIRECTORY)
  6. du.write_dataset_on_file(’TEST_PATH’, tests, tlabel_s)

Here we have to do the following changes:
  • modify the variable DIRECTORY and add the directory containig the .inkml files (instead of ’DIRECTORY_PATH’) that make your dataset. For example:
  DIRECTORY = ’/Users/../ICFHR_package/CROHME2012_data/ trainData/trainData’.
  • the inputs of the du.write_dataset_on_file() setting as first argu- ment the path of the training set file (instead of ’TRAIN_PATH’)that is going to be created. For example: du.write_dataset_on_file(’/Users/../Desktop/trainingset.txt’, training, label_s)’.
  • the inputs of the du.write_dataset_on_file() setting as first argu- ment the path of the testing set file (instead of ’TEST_PATH’)that we are going to create. For example: du.write_dataset_on_file(’/Users/../Desktop/testset.txt’, tests, label_s)’.

At the end of this phase two files .txt (one for the training and the other
for the testing set) will be created in the specified paths.

### 4.2) Training and Classification
In the second step we have to open the script random_forest.py. Here we have to add:
  • the path of the training set that we have created in the first step as input of the function ds.load_dataset_from_file() (at line 18).
  For example:
  training_set, training_labels = ds.load_dataset_from_file(’ /Users/../Desktop/trainingset.txt’)
  • the path of the test set that we have created in the first step as input of the function ds.load_dataset_from_file() (at line 28).
  For example:
  testing_set, testing_labels = ds.load_dataset_from_file(’ /Users/../Desktop/testset.txt’)
  • modify the test_result_file variable adding the path to the text file in which the test results will be written.
After we have done these changes, we can run the random_forest.py file. A text file (in the specified path) will be written with all the informations gathered from the tests.

### prova
