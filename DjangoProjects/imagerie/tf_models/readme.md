## GoogLeNet in Keras

Here is a [Keras](http://keras.io/) model of GoogLeNet (a.k.a Inception V1). I created it by converting the GoogLeNet model from Caffe.

GoogLeNet paper:

    Going deeper with convolutions.
    Szegedy, Christian, et al. 
    Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. 2015.


### Requirements

The code now runs with Python `3.6`, Keras `2.2.4`, and either Theano `1.0.4` or Tensorflow `1.14.0`. You will also need to install the following:

```
pip install pillow numpy imageio
```

To switch to the Theano backend, change your `~/.keras/keras.json` file to
```
{"epsilon": 1e-07, "floatx": "float32", "backend": "theano", "image_data_format": "channels_first"}
```
Or for the Tensorflow backend,
```
{"epsilon": 1e-07, "floatx": "float32", "backend": "tensorflow", "image_data_format": "channels_first"}
```
Note that in either case, the code requires the `channels_first` option for `image_data_format`.

### Running the Demo (googlenet.py)

To create a GoogLeNet model, call the following from within Python:
```
from googlenet import create_googlenet
model = create_googlenet()
```
`googlenet.py` also contains a demo image classification. To run the demo, you will need to install the [pre-trained weights](https://drive.google.com/open?id=0B319laiAPjU3RE1maU9MMlh2dnc) and the [class labels](https://drive.google.com/file/d/1kfAYsZ1di5E8ZD7v1zDPTEncSFDnKSmJ/view?usp=sharing). You will also need this [test image](https://drive.google.com/file/d/1LMN6P4IWMJDYXQKTSnDUkBbLxqBz_DqN/view?usp=sharing). Once these are downloaded and moved to the working directory, you can run `googlenet.py` from the terminal:
```
$ python googlenet.py
```
which will output the predicted class label for the image.


