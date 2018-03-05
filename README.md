# Online Handwritten Math Formulas Segmenter
April 21, 2017

This is an academic exercise from a course at **Univeristà degli Studi di Firenze**.

The project is an implementation of a method for segmenting on-line handwritten math formulas. It consists of line of sight stroke graph representation of the formula, feature extraction and training of a random forest classifier.

Based on the paper:

Lei Hu and Richard Zanibbi. Line-of-Sight Stroke Graphs and Parzen Shape Context Features
for Handwritten Math Formula Representation and Symbol Segmentation, Proc. ICFHR, 2016.

## 1) Files
The directory in which this file is present contains also the following files:

  * a folder called "src" containing the files:
    - create_dataset.py
    - dataset_utils.py
    - graphic_segmenter.py
    - los_graph.py
    - mathExpression.py
    - parserXml.py
    - randomForest.py
    - util.py

  * this README file

In order to run the tests you will also need to download [the CROHME package](https://www.isical.ac.in/~crohme/CROHME_data.html)  with the datasets.

## 2) Prerequisites

  * Python 2.7.10
  * numpy
  * scipy
  * matpotlib
  * scikit-learn

## 3) Getting Started

The method is divided in two consecutive phases:
  1. creation of the training and testing set.
  2. training and classification phase.

## 4) Running Tests

### 4.1) Dataset Creation

We have to open the "src" folder. In the `create_dataset.py` file the code is the follower:
```
import dataset_utils as du
DIRECTORY = ’DIRECTORY_PATH’
training, label_s = du.get_training_set(DIRECTORY)
du.write_dataset_on_file(’TRAIN_PATH’, training, label_s)
tests, tlabel_s = du.get_testing_set(DIRECTORY)
du.write_dataset_on_file(’TEST_PATH’, tests, tlabel_s)
```

Here we have to do the following changes:

  * modify the variable `DIRECTORY` and add the directory containig the .inkml files (instead of *DIRECTORY_PATH*) that make your dataset. For example:
    ```
    DIRECTORY = ’/Users/../ICFHR_package/CROHME2012_data/ trainData/trainData’
    ```
    .

  * the inputs of the `du.write_dataset_on_file()` setting as first argument the path of the training set file (instead of *TRAIN_PATH*)that is going to be created. For example:
    ```
    du.write_dataset_on_file(’/Users/../Desktop/trainingset.txt’, training, label_s)’
    ```
    .

  * the inputs of the `du.write_dataset_on_file()` setting as first argument the path of the testing set file (instead of *TEST_PATH*)that we are going to create. For example:
    ```
    du.write_dataset_on_file(’/Users/../Desktop/testset.txt’, tests, label_s)    
    ```
    .


At the end of this phase two files .txt (one for the training and the other
for the testing set) will be created in the specified paths.

### 4.2) Training and Classification

In the second step we have to open the script `random_forest.py`. Here we have to add:
  * the path of the training set that we have created in the first step as input of the function `ds.load_dataset_from_file()` (at line 18).
  For example:
      ```
      training_set, training_labels = ds.load_dataset_from_file(’ /Users/../Desktop/trainingset.txt’)
      ```
  * the path of the test set that we have created in the first step as input of the function `ds.load_dataset_from_file()` (at line 28).
  For example:
      ```
      testing_set, testing_labels = ds.load_dataset_from_file(’ /Users/../Desktop/testset.txt’)
      ```

  * ~~modify the `test_result_file` variable adding the path to the text file in which the test results will be written.~~

After we have done these changes, we can run the `random_forest.py file`. ~~A text file (in the specified path) will be written with all the informations gathered from the tests.~~

## Authors

This academic exercise was implemented by [aurelpjetri](https://github.com/aurelpjetri) and [pietrobongini](https://github.com/pietrobongini)
