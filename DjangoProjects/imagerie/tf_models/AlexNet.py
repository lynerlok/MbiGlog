import keras
from keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential

from imagerie.models import CNN


class AlexNet(CNN):

    def set_tf_model(self):
        # Instantiate an empty model
        self.nn_model = Sequential()

        # 1st Convolutional Layer
        self.nn_model.add(
            Conv2D(filters=96, input_shape=(224, 224, 3), kernel_size=(11, 11), strides=(4, 4), padding='valid'))
        self.nn_model.add(Activation('relu'))
        # Max Pooling
        self.nn_model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

        # 2nd Convolutional Layer
        self.nn_model.add(Conv2D(filters=256, kernel_size=(11, 11), strides=(1, 1), padding='valid'))
        self.nn_model.add(Activation('relu'))
        # Max Pooling
        self.nn_model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

        # 3rd Convolutional Layer
        self.nn_model.add(Conv2D(filters=384, kernel_size=(3, 3), strides=(1, 1), padding='valid'))
        self.nn_model.add(Activation('relu'))

        # 4th Convolutional Layer
        self.nn_model.add(Conv2D(filters=384, kernel_size=(3, 3), strides=(1, 1), padding='valid'))
        self.nn_model.add(Activation('relu'))

        # 5th Convolutional Layer
        self.nn_model.add(Conv2D(filters=256, kernel_size=(3, 3), strides=(1, 1), padding='valid'))
        self.nn_model.add(Activation('relu'))
        # Max Pooling
        self.nn_model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))

        # Passing it to a Fully Connected layer
        self.nn_model.add(Flatten())
        # 1st Fully Connected Layer
        self.nn_model.add(Dense(4096, input_shape=(224 * 224 * 3,)))
        self.nn_model.add(Activation('relu'))
        # Add Dropout to prevent overfitting
        self.nn_model.add(Dropout(0.4))

        # 2nd Fully Connected Layer
        self.nn_model.add(Dense(4096))
        self.nn_model.add(Activation('relu'))
        # Add Dropout
        self.nn_model.add(Dropout(0.4))

        # 3rd Fully Connected Layer
        self.nn_model.add(Dense(1000))
        self.nn_model.add(Activation('relu'))
        # Add Dropout
        self.nn_model.add(Dropout(0.4))

        # Output Layer
        self.nn_model.add(Dense(17))
        self.nn_model.add(Activation('softmax'))

        # Compile the self.nn_model
        self.nn_model.compile(loss=keras.losses.categorical_crossentropy, optimizer='adam', metrics=["accuracy"])
