import pickle

import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.metrics import ConfusionMatrixDisplay

class ConfusionMatrixTracker:
    MEASURE_TYPE = "confusion-matrix"

    def __init__(self, benchmark):
        self.benchmark = benchmark        

    def track(self, matrix, labels, description):
        """
        Pass an ndarray where axis 0 is predicted and axis 1 is actual.
        """
        serialized = self.serialize(matrix, labels)
        self.benchmark.log(description, self.MEASURE_TYPE, serialized)

    def serialize(self, matrix, labels):
        return pickle.dumps({'matrix': matrix, 'labels': labels})

class HyperparameterTracker:
    MEASURE_TYPE = "hyperparameters"

    def __init__(self, benchmark, description, hyperparameters, target, low_means_good=True):
        self.benchmark = benchmark
        self.description = description
        self.hyperparameters = hyperparameters
        self.target = target
        self.low_means_good = low_means_good

        self.df = pd.DataFrame(columns=hyperparameters + [target])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def track(self, measurement):
        for param in self.hyperparameters:
            assert param in measurement, f"Hyperparameter {param} not found in given measurement."
        assert self.target in measurement, f"Target variable {self.target} not found in given measurement."

        measurement = {k: v for k, v in measurement.items() if k in self.hyperparameters + [self.target]}
        self.df.loc[len(self.df)] = measurement
    
    def close(self):
        serialized = self.serialize()
        self.benchmark.log(self.description, self.MEASURE_TYPE, serialized)

    def serialize(self):
        return pickle.dumps({
            'hyperparameters' : self.hyperparameters,
            'df' : self.df.to_dict(orient='list'),
            'target' : self.target,
            'low_means_good' : self.low_means_good
        })

class TTATracker:
    MEASURE_TYPE = "tta"

    def __init__(self, benchmark):
        self.benchmark = benchmark

    def track(self, accuracies, description):
        serialized = self.serialize(accuracies)
        self.benchmark.log(description, self.MEASURE_TYPE, serialized, unit='accuracy')

    def serialize(self, accuracies):
        return pickle.dumps(accuracies)

class TTAVisualizer:
    def __init__(self, serialized_bytes):
        self.accuracies = []
        for values in serialized_bytes:
            self.accuracies.append(pickle.loads(values)['accuracies'])

    def visualize(self, uuid, description, starts):
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)

        for run in range(len(self.accuracies)):
            x_values = []
            for i in range(len(self.accuracies[run])):
                x_values.append(i + 1)
            plt.xticks(rotation=90)
            ax.plot(['{:.1f}'.format(x) for x in x_values],
                self.accuracies[run],
                label=("Run from " + str(starts[run].isoformat(' ', 'seconds'))))

        plt.legend(loc=2)
        ax.set_ylabel("accuracy")
        ax.set_xlabel("epoch")
        plt.title("Time to accuracy")

        ax.yaxis.set_major_locator(ticker.LinearLocator(12))
        plt.show()

class LossTracker:
    MEASURE_TYPE = "loss"

    def __init__(self, benchmark):
        self.benchmark = benchmark

    def track(self, loss_values, description):
        serialized = self.serialize(loss_values)
        self.benchmark.log(description, self.MEASURE_TYPE, serialized, unit="loss")

    def serialize(self, loss_values):
        return pickle.dumps(loss_values)