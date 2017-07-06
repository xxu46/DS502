import numpy as np
from sklearn.utils import shuffle
from random import seed

def sigmoid(x):
    """
    Sigmoid (logistic) function
    :param x: array-like shape(n_sample, n_feature)
    :return: simgoid value (array like)
    """
    return 1.0 / (1 + np.exp(-x))

#
#
def dsigmoid(x):
    """
    Derivative of sigmoid function
    :param x: array-like shape(n_sample, n_feature)
    :return: derivative value (array like)
    """
    return x * (1 - x)


def tanh(x):
    """
    Tanh function
    :param x: array-like shape(n_sample, n_feature)
    :return: tanh value (array like)
    """
    denominator = 1.0 + np.exp(-2 * x)
    return 2 / denominator - 1
#

def dtanh(z):
    """
    Derivative of tanh function
    :param z: array-like shape(n_sample, n_feature)
    :return: derivative value (array like)
    """
    return 1.0 - np.power(tanh(z), 2)

def softmax(X):
    """
    softmax function
    :param X:
    :return:
    """
    # TODO softmax function
    return (np.exp(X).T / np.sum(np.exp(X), axis=1)).T




class MLP:
    def __init__(self, input_size, output_size, hidden_layer_size=[128], batch_size=200, activation="sigmoid",
                 output_layer='softmax', loss='cross_entropy', lr=0.001, reg_lambda=0.0001, momentum=0.9, verbose=1):
        """
        Multilayer perceptron Class
        :param input_size: int, input size (n_feature)
        :param output_size: int,  output node size (n_class)
        :param hidden_layer_size: list of int, each int represents the size of a hidden layer
        :param batch_size: int, batch_size
        :param activation: string, activation function ['sigmoid', 'tanh']
        :param output_layer: string, output layer type ['softmax']
        :param loss: string, loss type ['cross_entropy']
        :param lr: float, learning rate
        :param reg_lambda: float, lambda of regularization
        :param verbose: int, print flag
        :param momentum: float, momentum
        """
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_layer_size = hidden_layer_size
        self.lr = lr
        self.reg_lambda = reg_lambda
        self.momentum = momentum
        self.batch_size = batch_size
        self.n_layers = len(hidden_layer_size)  # only hidden layers
        self.activation = activation
        self.verbose = verbose

        if activation == 'sigmoid':
            self.activation_func = sigmoid
            self.activation_dfunc = dsigmoid
        elif activation == 'tanh':
            self.activation_func = tanh
            self.activation_dfunc = dtanh
        else:
            raise ValueError("Currently only supoort 'sigmoid' or 'tanh' activations func!")

        self.loss = loss
        if output_layer == 'softmax':
            self.output_layer = softmax
        else:
            raise ValueError('Currently only Support softmax output_layer!')

        self.nclass = output_size

        self.weights = []  # store weights
        self.bias = []  # store bias
        self.layers = []  # store forwarding activation values
        self.deltas = []  # store errors for backprop

    def get_weight_bound(self, fan_in, fan_out):
        """
        Generate bound value for random weights initialization
        :param fan_in: layer input size
        :param fan_out: layer output size
        :return: float, bound
        """
        if self.activation == 'sigmoid':
            init_bound = np.sqrt(2. / (fan_in + fan_out))
        elif self.activation == 'tanh':
            init_bound = np.sqrt(6. / (fan_in + fan_out))
        return init_bound

    def fit(self, X, y, max_epochs, shuffle_data):
        """
        fit the model given data X and label y
        :param X: array-like, shape(n_samples, n_features)
        :param y: array-like, shape(n_samples, 1)
        :param max_epochs: int, max iterations
        :param shuffle_data: bool, if shuffle the data.
        :return: MLP model object
        """
        n_samples, n_features = X.shape
        if y.shape[0] != n_samples:
            raise ValueError("Shapes of X and y don't fit!")

        # generate weights
        # Weights and bias connecting input layer and first hidden layer
        seed(1)
        init_bound = self.get_weight_bound(n_features, self.hidden_layer_size[0])
        self.weights.append(np.random.uniform(-init_bound, init_bound, size=(n_features, self.hidden_layer_size[0])))
        self.bias.append(np.random.uniform(-init_bound, init_bound, self.hidden_layer_size[0]))

        # Weights and bias connecting hidden layers
        for i in range(1, len(self.hidden_layer_size)):
            init_bound = self.get_weight_bound(self.hidden_layer_size[i - 1], self.hidden_layer_size[i])
            self.weights.append(np.random.uniform(-init_bound, init_bound,
                                                  size=(self.hidden_layer_size[i - 1], self.hidden_layer_size[i])))
            self.bias.append(np.random.uniform(-init_bound, init_bound, self.hidden_layer_size[i]))

        # Weights and bias connecting last hidden layer and output layer
        init_bound = self.get_weight_bound(self.hidden_layer_size[-1], self.output_size)
        self.weights.append(
            np.random.uniform(-init_bound, init_bound, size=(self.hidden_layer_size[-1], self.output_size)))
        self.bias.append(np.random.uniform(-init_bound, init_bound, self.output_size))

        # pre-allocate memory for both activations and errors
        # for input layer
        self.layers.append(np.empty((self.batch_size, self.input_size)))
        # for hidden layers
        for i in range(0, self.n_layers):
            self.layers.append(np.empty((self.batch_size, self.hidden_layer_size[i])))
            self.deltas.append(np.empty((self.batch_size, self.hidden_layer_size[i])))
        # for output layer
        self.layers.append(np.empty((self.batch_size, self.output_size)))
        self.deltas.append(np.empty((self.batch_size, self.output_size)))

        # main loop
        for i in range(max_epochs):
            if shuffle_data:
                index_set = np.asarray(range(0, X.shape[0]))
                np.random.shuffle(index_set)
                X = X[index_set, :]
                y = y[index_set]

            # iterate every batch
            for batch in range(0, n_samples, self.batch_size):
                # @TODO call forward function
                self.forward(X[batch: batch + self.batch_size, :])

                # @TODO call backward function
                self.backward(X[batch:batch + self.batch_size, :], y[batch:batch + self.batch_size])

            if i % self.verbose == 0:
                # Compute Loss and Training Accuracy
                loss = self.compute_loss(X, y)
                acc = self.score(X, y)
                print('Epoch {}: loss = {}, accuracy = {}'.format(i, loss, acc))

        return self

    def compute_loss(self, X, y):
        """
        Compute loss
        :param X: data, array-like, shape(n_sample, n_feature)
        :param y: label, array-like, shape(n_sample, 1)
        :return: loss value
        """
        n_samples = X.shape[0]
        a = self.forward(X)

        # @TODO  Calculating the loss
        y = y.reshape(1, -1)
        data_loss = np.sum(np.dot(-y, np.log(a)) - np.dot((1 - y), np.log(1 - a)))

        # @TODO Add regularization term to loss
        for i in range(0, self.n_layers + 1):
            data_loss += 0.5 * self.reg_lambda * np.sum( np.power(self.weights[i], 2) )
        return 1. / n_samples * data_loss

    def forward(self, X):
        # input layer
        self.layers[0] = X

        # @TODO hidden layers

        for i in range(1, 1 + self.n_layers):
            W = self.weights[i - 1]
            X = self.layers[i - 1]
            b = self.bias[i - 1]
            net = np.dot(X, W) + b
            self.layers[i] = self.activation_func(net)

        # @TODO output layer (Note here the activation is using output_layer func)

        last = self.n_layers
        W = self.weights[last]
        X = self.layers[last]
        b = self.bias[last]
        net = np.dot(X, W) + b
        self.layers[-1] = self.output_layer(net)

        return self.layers[-1]

    def backward(self, X, y):
        if self.loss == 'cross_entropy':
            self.deltas[-1] = self.layers[-1]
            # cross_entropy loss backprop
            self.deltas[-1][range(X.shape[0]), y] -= 1

        # @TODO update deltas
        for i in range(self.n_layers, 0, -1):
            a = self.layers[i]
            W = self.weights[i]
            self.deltas[i - 1] = np.dot(self.deltas[i], W.T) * self.activation_dfunc(a)


        # @TODO update weights, need to improve performance
        for i in range(self.n_layers, -1, -1):
            a = self.layers[i]
            W = self.weights[i]
            delta = self.deltas[i]
            deltaW = np.dot(a.T, delta)
            self.weights[i] = W - self.lr * deltaW

    def predict(self, X):
        """
        predicting probability outputs
        :param X: array-like, shape(n_samples, n_features)
        :return: array-like, predicted probabilities
        """
        return self.forward(X)

    def score(self, X, y):
        """
        compute accuracy
        :param X: array-like, shape(n_samples, n_features)
        :param y: ground truth labels array-like, shape(n_samples, 1)
        :return: float, accuracy
        """
        n_samples = X.shape[0]

        # @TODO compute accuracy

        pred = self.forward(X)

        result_list = pred.argmax(axis=1) == y

        return np.sum(result_list * 1.0 / n_samples)

def my_mlp():
    # from sklearn.datasets import fetch_mldata
    # mnist = fetch_mldata("MNIST original")
    # X, y = mnist.data / 255., mnist.target
    # X_train, X_test = X[:60000], X[60000:]
    # y_train, y_test = y[:60000], y[60000:]

    import sklearn.datasets
    dataset = sklearn.datasets.load_digits()
    X_train = dataset.data[:1500]
    X_test = dataset.data[1500:]
    y_train = dataset.target[:1500]
    y_test = dataset.target[1500:]

    network = MLP(input_size=64, output_size=10, hidden_layer_size=[128], batch_size=200, activation="sigmoid",
                  output_layer='softmax', loss='cross_entropy', lr=0.001)

    network.fit(X_train, y_train, 100, True)

    acc = network.score(X_test, y_test)
    print('Test Accuracy: {}'.format(acc))


def sklearn_mlp():
    import matplotlib.pyplot as plt
    from sklearn.datasets import fetch_mldata
    from sklearn.neural_network import MLPClassifier

    # mnist =fetch_mldata("MNIST original")
    # X, y = mnist.data / 255., mnist.target
    # X_train, X_test = X[:60000], X[60000:]
    # y_train, y_test = y[:60000], y[60000:]

    import sklearn.datasets
    dataset = sklearn.datasets.load_digits()
    X_train = dataset.data[:1500]
    X_test = dataset.data[1500:]
    y_train = dataset.target[:1500]
    y_test = dataset.target[1500:]

    mlp = MLPClassifier(hidden_layer_sizes=(128), max_iter=100, alpha=1e-4,
                        solver='sgd', activation='logistic', verbose=10, tol=1e-4, random_state=1,
                        learning_rate_init=.001)
    mlp.fit(X_train, y_train)
    print("Training set score: %f" % mlp.score(X_train, y_train))
    print("Test set score: %f" % mlp.score(X_test, y_test))


def main():
    print('Class 2 Multiple Layer Perceptron (MLP) Example')
    my_mlp()

    print('')

    print('Class 2 sklearn MLP Example')
    sklearn_mlp()


if __name__ == "__main__":
    main()