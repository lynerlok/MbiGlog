import os
from abc import abstractmethod
from typing import *
from xml.etree import ElementTree

import imageio
import keras
import numpy as np
import requests
from PIL import Image as PImage
from django.conf import settings as st
from django.core.exceptions import SuspiciousFileOperation
from django.db import models
from django.db.models import QuerySet, Count, Sum
from keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.models import Sequential


class Label(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RankTaxon(Label):
    pass


class Taxon(models.Model):
    tax_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    sup_taxon = models.ForeignKey('Taxon', on_delete=models.SET_NULL, null=True, related_name='inf_taxons')

    rank = models.ForeignKey('RankTaxon', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self.tax_id is None:
            self.set_id_from_name()
        super(Taxon, self).save(*args, **kwargs)

    @property
    def clean_name(self):
        if self.rank.id != 8:
            return self.name.split()[0]
        else:
            return ' '.join(self.name.split()[:2])

    def set_id_from_name(self):
        self.tax_id = self.get_id_from_name(self.clean_name)

    @staticmethod
    def get_id_from_name(name):
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={name}"
        root = ElementTree.fromstring(requests.get(url).content)
        if int(root.find('Count').text) > 0:
            return int(root.find('IdList').find('Id').text)

    def __str__(self):
        if self.sup_taxon is None:
            return self.clean_name
        else:
            return "{} > {}".format(str(self.sup_taxon), self.clean_name)


class Specie(Taxon):
    latin_name = models.CharField(max_length=50)
    vernacular_name = models.CharField(max_length=50)

    def __str__(self):
        return self.latin_name


class PlantOrgan(Label):
    pass


class BackgroundType(Label):
    pass


class Image(models.Model):
    image = models.ImageField(upload_to="images/")
    date = models.DateTimeField(auto_now_add=True)
    plant_organ = models.ForeignKey('PlantOrgan', on_delete=models.PROTECT)
    background_type = models.ForeignKey('BackgroundType', on_delete=models.PROTECT)

    def __str__(self):
        return self.image.name

    def preprocess(self):
        """Preprocess of GoogLeNet for now"""

        img = imageio.imread(self.image.path, pilmode='RGB')
        img = np.array(PImage.fromarray(img).resize((224, 224))).astype(np.float32)
        img[:, :, 0] -= 123.68
        img[:, :, 1] -= 116.779
        img[:, :, 2] -= 103.939
        img[:, :, [0, 1, 2]] = img[:, :, [2, 1, 0]]
        img = img.transpose((2, 0, 1))
        return np.expand_dims(img, axis=0)


class SubmittedImage(Image):
    @property
    def specie(self):
        return self.prediction_set.values('specie').annotate(tot_conf=Sum('confidence')).first()


class GroundTruthImage(Image):
    specie = models.ForeignKey('Specie', on_delete=models.SET_NULL, null=True)


class ImageClassifier(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    accuracy = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    name = models.CharField(max_length=50)

    def classify(self, images: Iterable[Image]) -> Iterable[Specie]:
        raise NotImplementedError("Should implement classify")

    class Meta:
        abstract = True


class CNN(ImageClassifier):
    learning_data = models.FilePathField(allow_folders=True, null=True)
    classes = models.ManyToManyField(Specie, through="Class", related_name='+')
    available = models.BooleanField(default=False)
    nn_model = None
    train_images = None
    train_labels = None
    test_images = None
    test_labels = None

    @abstractmethod
    def set_tf_model(self):
        pass

    def train(self, training_data=None):
        # TODO Deal with training data only if specified, otherwise use all available data
        #  (Maybe use filter kwargs instead of directly give training dataset)

        self.split_images(training_data, test_fraction=0.2)
        self.set_tf_model()
        self.nn_model.fit(self.train_images, self.train_labels, epochs=10, verbose=2)
        _, self.accuracy = self.nn_model.evaluate(self.test_images, self.test_labels)
        self.save_model()
        self.available = True

    def classify(self, images: List[Image]):
        if not self.available:
            raise Exception('The CNN is not available yet')
        if self.nn_model is None:
            self.load_model()
        predictions = self.nn_model.predict(images)
        predictions.argmax()  # TODO extract max p for all given images and get Specie from here
        for cnn_class in self.class_set:
            for i in range(len(images)):
                pred = Prediction(cnn=self, image=images[i], specie=cnn_class.specie,
                                  confidence=predictions[i][cnn_class.pos])
                pred.save()

    def split_images(self, images: QuerySet = None, test_fraction: float = 0.2):
        if images is None:
            images = GroundTruthImage.objects.all()
        species = images.values('specie__name').annotate(nb_image=Count('specie')).filter(nb_image__gte=10)
        specie_to_pos = {}
        self.save()
        for i in range(len(species)):
            specie = Specie.objects.get(latin_name=species[i]['specie__name'])
            Class.objects.get_or_create(cnn=self, specie=specie, pos=i)
            specie_to_pos[specie] = i
        train_images = []
        train_labels = []
        test_images = []
        test_labels = []
        nb_images = len(images)
        for i in range(nb_images):
            if i < (1 - test_fraction) * nb_images:
                train_images.append(images[i].preprocess())
                train_labels.append(specie_to_pos[images[i].specie])
            else:
                test_images.append(images[i].preprocess())
                test_labels.append(specie_to_pos[images[i].specie])

    def save_model(self):
        self.learning_data = os.path.join(st.MEDIA_ROOT, 'training_datas', f'{self.__class__.__name__}_'
                                                                           f'{self.date.year}_'
                                                                           f'{self.date.month}_'
                                                                           f'{self.date.day}_'
                                                                           f'{self.date.hour}')
        os.mkdir(self.learning_data)
        self.nn_model.save(self.learning_data)

    def load_model(self):
        self.set_tf_model()
        self.nn_model.load_weights(self.learning_data)


class Class(models.Model):
    pos = models.IntegerField()
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE, null=True)


class Prediction(models.Model):
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    image = models.ForeignKey(SubmittedImage, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
    confidence = models.DecimalField(max_digits=4, decimal_places=3)





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
