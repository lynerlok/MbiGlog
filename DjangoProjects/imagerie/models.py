<<<<<<< HEAD
import os
from abc import abstractmethod
from random import shuffle
from typing import *
from xml.etree import ElementTree

import imageio
import numpy as np
import requests
import tensorflow as tf
from PIL import Image as PImage
from django.conf import settings as st
from django.db import models
from django.db.models import QuerySet, Count, Sum
from tensorflow.keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator


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
    plant_organ = models.ForeignKey('PlantOrgan', on_delete=models.PROTECT)
    background_type = models.ForeignKey('BackgroundType', on_delete=models.PROTECT)

    def __str__(self):
        return self.image.name

    def preprocess(self):
        """Preprocess of GoogLeNet for now"""
        img = imageio.imread(self.image.path, pilmode='RGB')
        img = np.array(PImage.fromarray(img).resize((224, 224))) / 255
        return img


class SubmittedImage(Image):
    request = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='submitted_images', null=True)

    @property
    def specie(self):
        return self.prediction_set.values('specie').annotate(tot_conf=Sum('confidence')).first()


class GroundTruthImage(Image):
    specie = models.ForeignKey('Specie', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.specie.name


class ImageClassifier(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    accuracy = models.DecimalField(max_digits=4, decimal_places=3, null=True)
    name = models.CharField(max_length=50)

    def classify(self, images: Iterable[Image]) -> Iterable[Specie]:
        raise NotImplementedError("Should implement classify")

    class Meta:
        abstract = True


class Request(models.Model):
    date = models.DateTimeField(auto_now_add=True)


class CNN(ImageClassifier):
    learning_data = models.FilePathField(allow_folders=True, null=True)
    classes = models.ManyToManyField(Specie, through="Class", related_name='+')
    available = models.BooleanField(default=False)
    specialized_organ = models.ForeignKey('PlantOrgan', on_delete=models.PROTECT, null=True, default=None)
    specialized_background = models.ForeignKey('BackgroundType', on_delete=models.PROTECT, null=True, default=None)
    nn_model = None
    train_images = None
    train_labels = None
    test_images = None
    test_labels = None

    @abstractmethod
    def set_tf_model(self):
        pass

    def train(self, training_data=None):
        # Respect GPU please :) 
        gpus = tf.config.experimental.list_physical_devices('GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)

        self.split_images(training_data, test_fraction=0.2)
        self.set_tf_model()

        #self.nn_model.fit(self.train_images, self.train_labels, batch_size=5, epochs=50, verbose=2)

        aug = ImageDataGenerator(dtype = 'float16')
        self.nn_model.fit_generator(aug.flow(self.train_images,
                                             self.train_labels, batch_size=10),
                                             validation_data=(self.test_images, self.test_labels),
                                             steps_per_epoch=len(self.train_images) // 10,
                                             epochs=50)

        _, accuracy = self.nn_model.evaluate(self.test_images, self.test_labels, verbose=1)
        self.accuracy = float(accuracy)
        print(self.accuracy)
        self.available = True
        self.save_model()

    def classify(self, request: Request):
        if not self.available:
            raise Exception('The CNN is not available yet')
        if self.nn_model is None:
            self.load_model()

        # Respect GPU please :) 
        gpus = tf.config.experimental.list_physical_devices('GPU')
        tf.config.experimental.set_memory_growth(gpus[0], True)

        images = request.submitted_images.all()
        processed_images = np.array([image.preprocess() for image in images])
        predictions = self.nn_model.predict(processed_images)
        original_index_sorted = np.argsort(-predictions, axis=1)

        for i in range(len(images)):
            for j in range(5):
                specie = self.class_set.get(pos=original_index_sorted[i, j]).specie
                try:
                    pred = Prediction.objects.get(cnn=self, image=images[i], specie=specie)
                except Prediction.DoesNotExist:
                    pred = Prediction(cnn=self, image=images[i], specie=specie)
                pred.confidence = float(predictions[i, original_index_sorted[i, j]])
                pred.save()

    def split_images(self, images: QuerySet = None, test_fraction: float = 0.2):
        if images is None:
            images = GroundTruthImage.objects.all()
        if self.specialized_organ:
            images = images.filter(plant_organ=self.specialized_organ)
        if self.specialized_background:
            images = images.filter(background_type=self.specialized_background)
        species = images.values('specie__name').annotate(nb_image=Count('specie')).filter(nb_image__gte=100)

        for specie in species:
            print(specie['specie__name'], specie['nb_image'])
        images = list(images)
        print(len(images))
        shuffle(images)
        specie_to_pos = {}
        self.save()  # allow to create ref to CNN in classes
        for i in range(len(species)):
            specie = Specie.objects.get(latin_name=species[i]['specie__name'])
            Class.objects.get_or_create(cnn=self, specie=specie, pos=i)
            specie_to_pos[specie] = i
        train_images, train_labels, test_images, test_labels = [], [], [], []
        nb_images = len(images)
        for i in range(nb_images):
            if images[i].specie in specie_to_pos:
                if i < (1 - test_fraction) * nb_images:
                    train_images.append(images[i].preprocess())
                    train_labels.append(specie_to_pos[images[i].specie])
                else:
                    test_images.append(images[i].preprocess())
                    test_labels.append(specie_to_pos[images[i].specie])

        self.train_images = np.array(train_images)
        self.train_labels = to_categorical(np.array(train_labels))
        self.test_images = np.array(test_images)
        self.test_labels = to_categorical(np.array(test_labels))

    def save_model(self):
        path = os.path.join(st.MEDIA_ROOT, 'training_datas')
        if not os.path.isdir(path):
            os.mkdir(path)
        path = os.path.join(path, f'{self.name}_'
                                  f'{self.date.year}_'
                                  f'{self.date.month}_'
                                  f'{self.date.day}_'
                                  f'{self.date.hour}.h5')

        self.nn_model.save(path)
        self.learning_data = path
        self.save()

    def load_model(self):
        self.nn_model = tf.keras.models.load_model(self.learning_data)


class Class(models.Model):
    pos = models.IntegerField()
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE, null=True)


class Prediction(models.Model):
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    image = models.ForeignKey(SubmittedImage, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
    confidence = models.DecimalField(max_digits=4, decimal_places=3)

    def __str__(self):
        return "{} guessed {} ({}%) on {} ".format(self.cnn.name, self.specie.name, self.confidence, self.image)


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
        # self.nn_model.add(Dense(len(self.classes.all())))
        self.nn_model.add(Dense(36))
        self.nn_model.add(Activation('softmax'))

        # Compile the self.nn_model

        self.nn_model.compile(loss="categorical_crossentropy",
                              optimizer="adam",
                              metrics=["accuracy"])
=======
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

import imageio
import numpy as np
import requests
from PIL import Image as PImage
from django.db import models
from django.db.models import QuerySet, Count, Sum
from keras.models import Model

from django.conf import settings as st


class Annotation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class RankTaxon(Annotation):
    pass


class Taxon(models.Model):
    tax_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50)
    sup_taxon = models.ForeignKey('Taxon', on_delete=models.SET_NULL, null=True)

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
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={}".format(name)
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


class ContentImage(Annotation):
    pass


class TypeImage(Annotation):
    pass


class Image(models.Model):
    image = models.ImageField(upload_to="images/")
    date = models.DateTimeField(auto_now_add=True)
    content = models.ForeignKey('ContentImage', on_delete=models.PROTECT)
    type = models.ForeignKey('TypeImage', on_delete=models.PROTECT)

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
    accuracy = models.DecimalField(max_digits=4, decimal_places=3)
    name = models.CharField(max_length=50)

    def classify(self, images: Iterable[Image]) -> Iterable[Specie]:
        raise NotImplementedError("Should implement classify")

    class Meta:
        abstract = True


class Optimizer(Annotation):
    pass


class Loss(Annotation):
    pass


sys.path.append(os.path.join(st.MEDIA_ROOT, 'models_scripts'))


class CNNArchitecture(models.Model):
    name = models.CharField(max_length=30)
    optimizer = models.ForeignKey('Optimizer', on_delete=models.PROTECT)
    loss = models.ForeignKey('Loss', on_delete=models.PROTECT)
    model_code = models.FileField(upload_to="models_scripts")

    def __str__(self):
        return self.name

    def _create_model(self) -> Model:
        code = import_module(Path(self.model_code.name).stem)
        return code.create_model()

    def compile(self) -> Model:
        nn_model = self._create_model()
        nn_model.compile(optimizer=self.optimizer.name, loss=self.loss.name, metrics=['accuracy'])
        return nn_model


class CNN(ImageClassifier):
    architecture = models.ForeignKey(CNNArchitecture, on_delete=models.PROTECT)
    learning_data = models.FilePathField(allow_folders=True, null=True)
    classes = models.ManyToManyField(Specie, through="Class", related_name='+')
    available = models.BooleanField(default=False)
    nn_model = None
    train_images = None
    train_labels = None
    test_images = None
    test_labels = None

    def train(self, training_data=None):
        # TODO Deal with training data only if specified, otherwise use all available data
        #  (Maybe use filter kwargs instead of directly give training dataset)

        self.nn_model = self.architecture.compile()
        self.split_images(test_fraction=0.2)
        self.nn_model.fit(self.train_images, self.train_labels, epochs=10)
        _, self.accuracy = self.nn_model.evaluate(self.test_images, self.test_labels)
        self.save_model()
        self.available = True

    # def split_images(self, images: QuerySet = None, test_fraction: float = 0.2):
    #     if images is None:
    #         images = GroundTruthImage.objects.all()
    #
    #     images.values('specie__name').annotate(Count(
    #         'specie'))  # TODO A tester pas sûr du tout que ça marche mais permet de gérer un queryset en entrée à priori
    #     for image in images:
    #         try:
    #             self.classes.get(specie=image.specie)
    #         except DoesNotExist:
    #             if images.filter(specie=image.specie):
    #                 Class.objects.create(pos=id_class, specie=image.specie, cnn=self)
    #     self.train_images = []
    #     self.train_labels = []
    #     self.test_images = []
    #     self.test_labels = []
    #     id_class = 1
    #     for specie in Specie.objects.all():
    #         trustfull_class_images = specie.image_set.filter(trustworthy=True)
    #         nb_image = 0
    #         nb_occurency = trustfull_class_images.count()
    #         if nb_occurency > 10:
    #             Class.objects.create(pos=id_class, specie=specie, cnn=self)
    #             id_class += 1
    #             train_test_limit = nb_occurency * (1 - test_fraction)
    #             for image in trustfull_class_images:
    #                 nb_image += 1
    #                 if nb_image <= train_test_limit:
    #                     self.train_images.append(image)
    #                     self.train_labels.append(id_class)
    #                 else:
    #                     self.test_images.append(image)
    #                     self.test_labels.append(id_class)
    #         else:
    #             pass

    def classify(self, images: Iterable[Image]):
        if not self.available:
            raise Exception('The CNN is not available yet')
        if self.nn_model is None:
            self.nn_model = self.architecture.compile()
            self.nn_model.load_weights(self.learning_data)
        predictions = self.nn_model.predict(images)
        predictions.argmax()  # TODO extract max p for all given images and get Specie from here

    # def save_model(self):
    #     self.learning_data = os.path.join(st.MEDIA_ROOT, 'training_datas', '{}_'.format(self.architecture.name)
    #                                                                        '{self.date.year}_'
    #                                                                        '{self.date.month}_'
    #                                                                        '{self.date.day}_'
    #                                                                        '{self.date.hour}')
    #     os.mkdir(self.learning_data)
    #     self.nn_model.save(self.learning_data)

    def load_model(self):
        pass


class CNNSpeciality(models.Model):
    accuracy = models.DecimalField(max_digits=4, decimal_places=3)

    class Meta:
        abstract = True


class CNNContent(CNNSpeciality):
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE, related_name='contents')
    content = models.ForeignKey(ContentImage, on_delete=models.CASCADE, related_name='cnns_specialiazed_in')


class CNNType(CNNSpeciality):
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE, related_name='types')
    type = models.ForeignKey(TypeImage, on_delete=models.CASCADE, related_name='cnns_specialiazed_in')


class Class(models.Model):
    pos = models.IntegerField()
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE, null=True)


class Prediction(models.Model):
    cnn = models.ForeignKey(CNN, on_delete=models.CASCADE)
    image = models.ForeignKey(SubmittedImage, on_delete=models.CASCADE)
    specie = models.ForeignKey(Specie, on_delete=models.CASCADE)
    confidence = models.DecimalField(max_digits=4, decimal_places=3)
>>>>>>> 88a427e184c0235aedacbbeea24db5bd07400fe8
