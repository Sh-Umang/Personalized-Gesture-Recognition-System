from knn_classifier import kNNClassifier
import numpy as np
import pandas as pd # Read csv
import pickle
import joblib
import os

class train(kNNClassifier):
    def __init__(self, k, model_name):
        super().__init__(k)
        self.model_name = model_name
        self.main()

    def main(self):
    # Load Data
        data_train, label_train, data_test, label_test = self.loadData(f'model/keypoints/{self.model_name}_keypoints.csv')  
        model_sav_path = f'model/models/{self.model_name}.sav'
        print(self.model_name)
                                                                                                                

        # Train Model
        kNN_model = self.trainKNN(data_train, label_train, 3)

        # with open('knn_model.pkl', 'wb') as model_file:
        #     pickle.dump(kNN_model, model_file)
        os.makedirs('model/models', exist_ok=True)
        if os.path.exists(model_sav_path):
             os.remove(model_sav_path)
        joblib.dump(kNN_model, model_sav_path)

        # Test Accuracy
        print('Accuracy:', float(self.testAccuracy(data_test, label_test, kNN_model)))

        # Evaluate Model
        self.evaluateModel(data_test, label_test, kNN_model)

if __name__ == '__main__':
        t = train(3, "GOOGLE")