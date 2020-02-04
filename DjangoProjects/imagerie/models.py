import os
from abc import abstractmethod
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
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical


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
        img = np.array(PImage.fromarray(img).resize((224, 224)))
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
    checkpoint_dir = models.FilePathField(allow_folders=True, null=True)
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
        # gpus = tf.config.experimental.list_physical_devices('GPU')
        # tf.config.experimental.set_memory_growth(gpus[0], True)

        self.split_images(training_data, test_fraction=0.2)
        self.set_tf_model()

        # Create a callback that saves the model's weights
        checkpoint_dir = self.checkpoint_dir_path
        checkpoint_path = os.path.join(checkpoint_dir, f'{self.name}_cp_{{epoch:04d}}.ckpt')
        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                         save_weights_only=False,
                                                         verbose=1, period=5)

        self.nn_model.fit(self.train_images, self.train_labels, batch_size=50, epochs=50, verbose=2)

        aug = ImageDataGenerator(dtype='float16')
        aug.fit(self.train_images)
        self.nn_model.save_weights(checkpoint_path.format(epoch=0))
        # self.nn_model.fit_generator(aug.flow(self.train_images, self.train_labels, batch_size=10),
        #                             validation_data=(self.test_images, self.test_labels),
        #                             steps_per_epoch=len(self.train_images) // 10,
        #                             epochs=50, callbacks=[cp_callback])
        _, accuracy = self.nn_model.evaluate(self.test_images, self.test_labels, verbose=1)
        self.accuracy = float(accuracy)
        print(self.accuracy)
        self.available = True
        self.save()

    def classify(self, images: List[Image]):
        if not self.available:
            raise Exception('The CNN is not available yet')
        if self.nn_model is None:
            self.load_model()

        # Respect GPU please :) 
        # gpus = tf.config.experimental.list_physical_devices('GPU')
        # tf.config.experimental.set_memory_growth(gpus[0], True)

        # images = request.submitted_images.all()
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
        images = self.filter_images(images)
        species = self.count_species(images)
        specie_to_pos, specie_counter = self.create_classes(species)

        images = list(images)
        print("Nb of images : ", len(images))

        train_images, train_labels, test_images, test_labels = [], [], [], []
        for image in images:
            specie = image.specie
            if specie in specie_to_pos:
                counter = specie_counter[specie]
                nb_images = counter['n']
                i = counter['i']
                counter['i'] += 1
                if i < (1 - test_fraction) * nb_images:
                    train_images.append(image.preprocess())
                    train_labels.append(specie_to_pos[specie])
                else:
                    test_images.append(image.preprocess())
                    test_labels.append(specie_to_pos[specie])

        self.train_images = np.array(train_images)
        self.train_labels = to_categorical(np.array(train_labels))
        self.test_images = np.array(test_images)
        self.test_labels = to_categorical(np.array(test_labels))

    def filter_images(self, images: QuerySet = None) -> QuerySet:
        if images is None:
            images = GroundTruthImage.objects.all()
        if self.specialized_organ:
            images = images.filter(plant_organ=self.specialized_organ)
        if self.specialized_background:
            images = images.filter(background_type=self.specialized_background)
        return images

    def count_species(self, images: QuerySet, min_images=5):
        species = images.values('specie__name').annotate(nb_image=Count('specie')).filter(nb_image__gte=min_images)
        for specie in species:
            print(specie['specie__name'], specie['nb_image'])
        return species

    def create_classes(self, species: QuerySet) -> Tuple[Dict, Dict]:
        self.save()  # allow to create ref to CNN in classes
        specie_to_pos = {}
        specie_counter = {}
        for i in range(len(species)):
            specie = Specie.objects.get(latin_name=species[i]['specie__name'])
            Class.objects.get_or_create(cnn=self, specie=specie, pos=i)
            specie_to_pos[specie] = i
            specie_counter[specie] = {'i': 0, 'n': species[i]['nb_image']}
        return specie_to_pos, specie_counter

    @property
    def checkpoint_dir_path(self):
        path = os.path.join(st.MEDIA_ROOT, 'training_datas')
        if not os.path.isdir(path):
            os.mkdir(path)
        path = os.path.join(path, f'{self.name}_{self.specialized_background.name}_{self.specialized_organ.name}')
        if not os.path.isdir(path):
            os.mkdir(path)
            self.checkpoint_dir = path
            self.save()
        return path

    def load_model(self):
        latest = tf.train.latest_checkpoint(self.checkpoint_dir)
        self.set_tf_model()
        self.nn_model.load_weights(latest)


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
        self.nn_model.add(Dense(len(self.classes.all())))
        self.nn_model.add(Activation('softmax'))

        # Compile the self.nn_model

        self.nn_model.compile(loss="categorical_crossentropy",
                              optimizer="adam",
                              metrics=["accuracy"])
