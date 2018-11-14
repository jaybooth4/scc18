!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
try:
    import cPickle as pickle
except ImportError:
    import pickle
import keras
import argparse
import os
os.environ['LD_LIBRARY_PATH'] = os.getcwd()
from six.moves import range
import sys
import glob
import h5py
import numpy as np
import time
import math
import argparse
import random
import psutil
import socket
import time
from keras.callbacks import CallbackList
import analysis.utils.GANutils as gan # some common functions for gan

#import setGPU #if Caltech
def safe_mkdir(path):
   #Safe mkdir (i.e., don't create if already exists,and no violation of race conditions)
    from os import makedirs
    from errno import EEXIST
    try:
        makedirs(path)
    except OSError as exception:
        if exception.errno != EEXIST:
            raise exception


def BitFlip(x, prob=0.05):
    """ flips a int array's values with some probability """
    x = np.array(x)
    selection = np.random.uniform(0, 1, x.shape) < prob
    x[selection] = 1 * np.logical_not(x[selection])
    return x

def DivideFiles(FileSearch="/data/LCD/*/*.h5", nEvents=200000, EventsperFile = 10000, Fractions=[.9,.1],datasetnames=["ECAL","HCAL"],Particles=[],MaxFiles=-1):

    Files =sorted( glob.glob(FileSearch))
    Filesused = int(math.ceil(nEvents/EventsperFile))
    FileCount=0

    Samples={}
    for F in Files:
        FileCount+=1
        basename=os.path.basename(F)
        ParticleName=basename.split("_")[0].replace("Escan","")

        if ParticleName in Particles:
            try:
                Samples[ParticleName].append(F)
            except:
                Samples[ParticleName]=[(F)]

        if MaxFiles>0:
            if FileCount>MaxFiles:
                break
    out=[]
    for j in range(len(Fractions)):
        out.append([])
       if exception.errno != EEXIST:
            raise exception


def BitFlip(x, prob=0.05):
    """ flips a int array's values with some probability """
    x = np.array(x)
    selection = np.random.uniform(0, 1, x.shape) < prob
    x[selection] = 1 * np.logical_not(x[selection])
    return x

def DivideFiles(FileSearch="/data/LCD/*/*.h5", nEvents=200000, EventsperFile = 10000, Fractions=[.9,.1],datasetnames=["ECAL","HCAL"],Particles=[],MaxFiles=-1):

    Files =sorted( glob.glob(FileSearch))
    Filesused = int(math.ceil(nEvents/EventsperFile))
    FileCount=0

    Samples={}
    for F in Files:
        FileCount+=1
        basename=os.path.basename(F)
        ParticleName=basename.split("_")[0].replace("Escan","")

        if ParticleName in Particles:
            try:
                Samples[ParticleName].append(F)
            except:
                Samples[ParticleName]=[(F)]

        if MaxFiles>0:
            if FileCount>MaxFiles:
                break
    out=[]
    for j in range(len(Fractions)):
        out.append([])

    SampleI=len(Samples.keys())*[int(0)]

    for i,SampleName in enumerate(Samples):
        Sample=Samples[SampleName][:Filesused]
        NFiles=len(Sample)

        for j,Frac in enumerate(Fractions):
            EndI=int(SampleI[i]+ round(NFiles*Frac))
            out[j]+=Sample[SampleI[i]:EndI]
            SampleI[i]=EndI
    return out

# This functions loads data from a file and also does any pre processing
def GetData(datafile, xscale =1, yscale = 100, dimensions = 3, keras_dformat="channels_last"):
    #get data for training                                                                                         
    if hvd.rank()==0:
        print('Loading Data from .....', datafile)
    f=h5py.File(datafile,'r')

    X=np.array(f.get('ECAL'))

    Y=f.get('target')
    Y=(np.array(Y[:,1]))

    X[X < 1e-6] = 0
    X = np.expand_dims(X, axis=-1)
    X = X.astype(np.float32)
    if dimensions == 2:
        X = np.sum(X, axis=(1))
        X = xscale * X

    Y = Y.astype(np.float32)
    Y = Y/yscale
    if keras_dformat !='channels_last':
       X =np.moveaxis(X, -1, 1)
       ecal = np.sum(X, axis=(2, 3, 4))
 SampleI=len(Samples.keys())*[int(0)]

    for i,SampleName in enumerate(Samples):
        Sample=Samples[SampleName][:Filesused]
        NFiles=len(Sample)

        for j,Frac in enumerate(Fractions):
            EndI=int(SampleI[i]+ round(NFiles*Frac))
            out[j]+=Sample[SampleI[i]:EndI]
            SampleI[i]=EndI
    return out

# This functions loads data from a file and also does any pre processing
def GetData(datafile, xscale =1, yscale = 100, dimensions = 3, keras_dformat="channels_last"):
    #get data for training                                                                                         
    if hvd.rank()==0:
        print('Loading Data from .....', datafile)
    f=h5py.File(datafile,'r')

    X=np.array(f.get('ECAL'))

    Y=f.get('target')
    Y=(np.array(Y[:,1]))

    X[X < 1e-6] = 0
    X = np.expand_dims(X, axis=-1)
    X = X.astype(np.float32)
    if dimensions == 2:
        X = np.sum(X, axis=(1))
        X = xscale * X

    Y = Y.astype(np.float32)
    Y = Y/yscale
    if keras_dformat !='channels_last':
       X =np.moveaxis(X, -1, 1)
       ecal = np.sum(X, axis=(2, 3, 4))
    else:
       ecal = np.sum(X, axis=(1, 2, 3))
    return X, Y, ecal


def GetEcalFit(sampled_energies, mod=1, xscale=1):
    if mod==0:
      return np.multiply(2, sampled_energies)
    elif mod==1:
      root_fit = [0.0018, -0.023, 0.11, -0.28, 2.21]
      ratio = np.polyval(root_fit, sampled_energies)
      return np.multiply(ratio, sampled_energies) * xscale


def genbatches(a,n):
    for i in range(0, len(a), n):
        # Create an index range for l of n items:
        yield a[i:i+n]


def randomize(a, b, c):
    assert a.shape[0] == b.shape[0]
    # Generate the permutation index array.
    permutation = np.random.permutation(a.shape[0])
    # Shuffle the arrays by giving the permutation in the square brackets.
    shuffled_a = a[permutation]
    shuffled_b = b[permutation]
    shuffled_c = c[permutation]
    return shuffled_a, shuffled_b, shuffled_c


def GanTrain(discriminator, generator, opt, global_batch_size, warmup_epochs, datapath, EventsperFile, nEvents, WeightsDir, resultfile, energies,mod=0, nb_epochs=30, batch_size=128, latent_size=128, gen_weight=6, aux_weight=0.2, ecal_weig
ht=0.1, lr=0.001, rho=0.9, decay=0.0, g_weights='params_generator_epoch_', d_weights='params_generator_epoch_', xscale=1, verbose=True, keras_dformat='channels_last', analysis=True):
    start_init = time.time()
    # verbose = False
    if hvd.rank()==0:
else:
       ecal = np.sum(X, axis=(1, 2, 3))
    return X, Y, ecal


def GetEcalFit(sampled_energies, mod=1, xscale=1):
    if mod==0:
      return np.multiply(2, sampled_energies)
    elif mod==1:
      root_fit = [0.0018, -0.023, 0.11, -0.28, 2.21]
      ratio = np.polyval(root_fit, sampled_energies)
      return np.multiply(ratio, sampled_energies) * xscale


def genbatches(a,n):
    for i in range(0, len(a), n):
        # Create an index range for l of n items:
        yield a[i:i+n]


def randomize(a, b, c):
    assert a.shape[0] == b.shape[0]
    # Generate the permutation index array.
    permutation = np.random.permutation(a.shape[0])
    # Shuffle the arrays by giving the permutation in the square brackets.
    shuffled_a = a[permutation]
    shuffled_b = b[permutation]
    shuffled_c = c[permutation]
    return shuffled_a, shuffled_b, shuffled_c


def GanTrain(discriminator, generator, opt, global_batch_size, warmup_epochs, datapath, EventsperFile, nEvents, WeightsDir, resultfile, energies,mod=0, nb_epochs=30, batch_size=128, latent_size=128, gen_weight=6, aux_weight=0.2, ecal_weig
ht=0.1, lr=0.001, rho=0.9, decay=0.0, g_weights='params_generator_epoch_', d_weights='params_generator_epoch_', xscale=1, verbose=True, keras_dformat='channels_last', analysis=True):
    start_init = time.time()
    # verbose = False
    if hvd.rank()==0:
        print('[INFO] Building discriminator')
    #discriminator.summary()
    discriminator.compile(
        optimizer=opt,
        loss=['binary_crossentropy', 'mean_absolute_percentage_error', 'mean_absolute_percentage_error'],
        loss_weights=[gen_weight, aux_weight, ecal_weight]
    )

    # build the generator
    if hvd.rank()==0:
        print('[INFO] Building generator')
    #generator.summary()
    generator.compile(
        optimizer=opt,
        loss='binary_crossentropy'
    )

    # build combined Model
    latent = Input(shape=(latent_size, ), name='combined_z')
    fake_image = generator( latent)
    discriminator.trainable = False
    fake, aux, ecal = discriminator(fake_image)
    combined = Model(
        input=[latent],
        output=[fake, aux, ecal],
        name='combined_model'
    )

    combined.compile(
        #optimizer=Adam(lr=adam_lr, beta_1=adam_beta_1),
        optimizer=opt,
        loss=['binary_crossentropy', 'mean_absolute_percentage_error', 'mean_absolute_percentage_error'],
        loss_weights=[gen_weight, aux_weight, ecal_weight]
    )

    gcb = CallbackList( \
print('[INFO] Building discriminator')
    #discriminator.summary()
    discriminator.compile(
        optimizer=opt,
        loss=['binary_crossentropy', 'mean_absolute_percentage_error', 'mean_absolute_percentage_error'],
        loss_weights=[gen_weight, aux_weight, ecal_weight]
    )

    # build the generator
    if hvd.rank()==0:
        print('[INFO] Building generator')
    #generator.summary()
    generator.compile(
        optimizer=opt,
        loss='binary_crossentropy'
    )

    # build combined Model
    latent = Input(shape=(latent_size, ), name='combined_z')
    fake_image = generator( latent)
    discriminator.trainable = False
    fake, aux, ecal = discriminator(fake_image)
    combined = Model(
        input=[latent],
        output=[fake, aux, ecal],
        name='combined_model'
    )

    combined.compile(
        #optimizer=Adam(lr=adam_lr, beta_1=adam_beta_1),
        optimizer=opt,
        loss=['binary_crossentropy', 'mean_absolute_percentage_error', 'mean_absolute_percentage_error'],
        loss_weights=[gen_weight, aux_weight, ecal_weight]
    )

    gcb = CallbackList( \
        callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    dcb = CallbackList( \
        callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    ccb = CallbackList( \
        callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    gcb.set_model( generator )
    dcb.set_model( discriminator )
    ccb.set_model( combined )

    gcb.on_train_begin()
    dcb.on_train_begin()
    ccb.on_train_begin()

    # Getting Data
    Trainfiles, Testfiles = DivideFiles(datapath, nEvents=nEvents, EventsperFile = EventsperFile, datasetnames=["ECAL"], Particles =["Ele"])
    callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    dcb = CallbackList( \
        callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    ccb = CallbackList( \
        callbacks=[ \
        hvd.callbacks.BroadcastGlobalVariablesCallback(0), \
        hvd.callbacks.MetricAverageCallback(), \
        # hvd.callbacks.LearningRateWarmupCallback(warmup_epochs=warmup_epochs, verbose=1), \
        hvd.callbacks.LearningRateScheduleCallback(start_epoch=warmup_epochs, end_epoch=nb_epochs, multiplier=1.), \
        keras.callbacks.ReduceLROnPlateau(patience=10, verbose=1) \
        ])

    gcb.set_model( generator )
    dcb.set_model( discriminator )
    ccb.set_model( combined )

    gcb.on_train_begin()
    dcb.on_train_begin()
    ccb.on_train_begin()

    # Getting Data
    Trainfiles, Testfiles = DivideFiles(datapath, nEvents=nEvents, EventsperFile = EventsperFile, datasetnames=["ECAL"], Particles =["Ele"])

    if hvd.rank()==0:
        print("Train files: {0} \nTest files: {1}".format(Trainfiles, Testfiles))

    #Read test data into a single array
    for index, dtest in enumerate(Testfiles):
       if index == 0:
           X_test, Y_test, ecal_test = GetData(dtest, keras_dformat=keras_dformat)
       else:
           X_temp, Y_temp, ecal_temp = GetData(dtest, keras_dformat=keras_dformat)
           X_test = np.concatenate((X_test, X_temp))
           Y_test = np.concatenate((Y_test, Y_temp))
           ecal_test = np.concatenate((ecal_test, ecal_temp))

    for index, dtrain in enumerate(Trainfiles):
        if index == 0:
            X_train, Y_train, ecal_train = GetData(dtrain, keras_dformat=keras_dformat)
        else:
            X_temp, Y_temp, ecal_temp = GetData(dtrain, keras_dformat=keras_dformat)
            X_train = np.concatenate((X_train, X_temp))
            Y_train = np.concatenate((Y_train, Y_temp))
            ecal_train = np.concatenate((ecal_train, ecal_temp))

    print("On hostname {0} - After init using {1} memory".format(socket.gethostname(), psutil.Process(os.getpid()).memory_info()[0]))

    nb_test = X_test.shape[0]
    assert X_train.shape[0] == EventsperFile * len(Trainfiles), "# Total events in training files"
    nb_train = X_train.shape[0]# Total events in training files
    total_batches = nb_train / global_batch_size
    if hvd.rank()==0:
        print('Total Training batches = {} with {} events'.format(total_batches, nb_train))

    train_history = defaultdict(list)
    test_history = defaultdict(list)

    if hvd.rank()==0:
if hvd.rank()==0:
        print("Train files: {0} \nTest files: {1}".format(Trainfiles, Testfiles))

    #Read test data into a single array
    for index, dtest in enumerate(Testfiles):
       if index == 0:
           X_test, Y_test, ecal_test = GetData(dtest, keras_dformat=keras_dformat)
       else:
           X_temp, Y_temp, ecal_temp = GetData(dtest, keras_dformat=keras_dformat)
           X_test = np.concatenate((X_test, X_temp))
           Y_test = np.concatenate((Y_test, Y_temp))
           ecal_test = np.concatenate((ecal_test, ecal_temp))

    for index, dtrain in enumerate(Trainfiles):
        if index == 0:
            X_train, Y_train, ecal_train = GetData(dtrain, keras_dformat=keras_dformat)
        else:
            X_temp, Y_temp, ecal_temp = GetData(dtrain, keras_dformat=keras_dformat)
            X_train = np.concatenate((X_train, X_temp))
            Y_train = np.concatenate((Y_train, Y_temp))
            ecal_train = np.concatenate((ecal_train, ecal_temp))

    print("On hostname {0} - After init using {1} memory".format(socket.gethostname(), psutil.Process(os.getpid()).memory_info()[0]))

    nb_test = X_test.shape[0]
    assert X_train.shape[0] == EventsperFile * len(Trainfiles), "# Total events in training files"
    nb_train = X_train.shape[0]# Total events in training files
    total_batches = nb_train / global_batch_size
    if hvd.rank()==0:
        print('Total Training batches = {} with {} events'.format(total_batches, nb_train))

    train_history = defaultdict(list)
    test_history = defaultdict(list)

    if hvd.rank()==0:
        print('Initialization time was {} seconds'.format(time.time() - start_init))

    for epoch in range(nb_epochs):
        epoch_start = time.time()
        if hvd.rank()==0:
            print('Epoch {} of {}'.format(epoch + 1, nb_epochs))

        randomize(X_train, Y_train, ecal_train)

        epoch_gen_loss = []
        epoch_disc_loss = []

        image_batches = genbatches(X_train, batch_size)
        energy_batches = genbatches(Y_train, batch_size)
        ecal_batches = genbatches(ecal_train, batch_size)


        for index in range(total_batches):
            start = time.time()
            image_batch = image_batches.next()
            energy_batch = energy_batches.next()
            ecal_batch = ecal_batches.next()

            noise = np.random.normal(0, 1, (batch_size, latent_size))
            sampled_energies = np.random.uniform(0.1, 5,( batch_size, 1))
            generator_ip = np.multiply(sampled_energies, noise)
            # ecal sum from fit
            ecal_ip = GetEcalFit(sampled_energies, mod, xscale)
            generated_images = generator.predict(generator_ip, verbose=0)
            real_batch_loss = discriminator.train_on_batch(image_batch, [BitFlip(np.ones(batch_size)), energy_batch, ecal_batch])
            fake_batch_loss = discriminator.train_on_batch(generated_images, [BitFlip(np.zeros(batch_size)), sampled_energies, ecal_ip])
            epoch_disc_loss.append([
                (a + b) / 2 for a, b in zip(real_batch_loss, fake_batch_loss)
            ])

            trick = np.ones(batch_size)
print('Initialization time was {} seconds'.format(time.time() - start_init))

    for epoch in range(nb_epochs):
        epoch_start = time.time()
        if hvd.rank()==0:
            print('Epoch {} of {}'.format(epoch + 1, nb_epochs))

        randomize(X_train, Y_train, ecal_train)

        epoch_gen_loss = []
        epoch_disc_loss = []

        image_batches = genbatches(X_train, batch_size)
        energy_batches = genbatches(Y_train, batch_size)
        ecal_batches = genbatches(ecal_train, batch_size)


        for index in range(total_batches):
            start = time.time()
            image_batch = image_batches.next()
            energy_batch = energy_batches.next()
            ecal_batch = ecal_batches.next()

            noise = np.random.normal(0, 1, (batch_size, latent_size))
            sampled_energies = np.random.uniform(0.1, 5,( batch_size, 1))
            generator_ip = np.multiply(sampled_energies, noise)
            # ecal sum from fit
            ecal_ip = GetEcalFit(sampled_energies, mod, xscale)
            generated_images = generator.predict(generator_ip, verbose=0)
            real_batch_loss = discriminator.train_on_batch(image_batch, [BitFlip(np.ones(batch_size)), energy_batch, ecal_batch])
            fake_batch_loss = discriminator.train_on_batch(generated_images, [BitFlip(np.zeros(batch_size)), sampled_energies, ecal_ip])
            epoch_disc_loss.append([
                (a + b) / 2 for a, b in zip(real_batch_loss, fake_batch_loss)
            ])

            trick = np.ones(batch_size)
            gen_losses = []
            for _ in range(2):
                noise = np.random.normal(0, 1, (batch_size, latent_size))
                sampled_energies = np.random.uniform(0.1, 5, ( batch_size,1 ))
                generator_ip = np.multiply(sampled_energies, noise)
                ecal_ip = GetEcalFit(sampled_energies, mod, xscale)
                gen_losses.append(combined.train_on_batch(
                    [generator_ip],
                    [trick, sampled_energies.reshape((-1, 1)), ecal_ip]))
            epoch_gen_loss.append([
                (a + b) / 2 for a, b in zip(*gen_losses)
            ])

            if (index % 1)==0 and hvd.rank()==0:
                # progress_bar.update(index)
                print('processed {}/{} batches in {}'.format(index + 1, total_batches, time.time() - start))

        # save weights every epoch
        if hvd.rank()==0:

            safe_mkdir(WeightsDir)

            print ("saving weights of gen")
            generator.save_weights(WeightsDir + '/generator_{0}{1:03d}.hdf5'.format(g_weights, epoch), overwrite=True)

            print ("saving weights of disc")
            discriminator.save_weights(WeightsDir + '/discriminator_{0}{1:03d}.hdf5'.format(d_weights, epoch), overwrite=True)

            epoch_time = time.time()-epoch_start
            print("The {} epoch took {} seconds".format(epoch, epoch_time))
            # pickle.dump({'train': train_history, 'test': test_history}, open(WeightsDir + 'dcgan2D-history.pkl', 'wb'))
            if analysis:
              analysis_history = defaultdict(list)
              noise_test = np.random.normal(0., 1., (nb_test, latent_size))
              ep_test = np.expand_dims(Y_test, axis=-1)
              generator_ip_test = np.multiply(ep_test, noise_test)
              gen_losses = []
            for _ in range(2):
                noise = np.random.normal(0, 1, (batch_size, latent_size))
                sampled_energies = np.random.uniform(0.1, 5, ( batch_size,1 ))
                generator_ip = np.multiply(sampled_energies, noise)
                ecal_ip = GetEcalFit(sampled_energies, mod, xscale)
                gen_losses.append(combined.train_on_batch(
                    [generator_ip],
                    [trick, sampled_energies.reshape((-1, 1)), ecal_ip]))
            epoch_gen_loss.append([
                (a + b) / 2 for a, b in zip(*gen_losses)
            ])

            if (index % 1)==0 and hvd.rank()==0:
                # progress_bar.update(index)
                print('processed {}/{} batches in {}'.format(index + 1, total_batches, time.time() - start))

        # save weights every epoch
        if hvd.rank()==0:

            safe_mkdir(WeightsDir)

            print ("saving weights of gen")
            generator.save_weights(WeightsDir + '/generator_{0}{1:03d}.hdf5'.format(g_weights, epoch), overwrite=True)

            print ("saving weights of disc")
            discriminator.save_weights(WeightsDir + '/discriminator_{0}{1:03d}.hdf5'.format(d_weights, epoch), overwrite=True)

            epoch_time = time.time()-epoch_start
            print("The {} epoch took {} seconds".format(epoch, epoch_time))
            # pickle.dump({'train': train_history, 'test': test_history}, open(WeightsDir + 'dcgan2D-history.pkl', 'wb'))
            if analysis:
              analysis_history = defaultdict(list)
              noise_test = np.random.normal(0., 1., (nb_test, latent_size))
              ep_test = np.expand_dims(Y_test, axis=-1)
              generator_ip_test = np.multiply(ep_test, noise_test)
              generated_images_test = g.predict(generator_ip_test, verbose=0)
              if keras_dformat !='channels_last':
                 generated_images_test = np.swapaxes(generated_images_test, -1, 1)
                 X_test =  np.swapaxes(X_test, -1, 1)
              var = gan.sortEnergy([X_test, Y_test], ecal_test, energies, ang=0)
              print('Analysing............')
              result = gan.OptAnalysisShort(var, generated_images_test, energies, ang=0)
              # All of the results correspond to mean relative errors on different quantities
              analysis_history['total'].append(result[0])
              analysis_history['energy'].append(result[1])
              analysis_history['moment'].append(result[2])
              print('Result = ', result)
              pickle.dump({'results': analysis_history}, open(resultfile, 'a+'))


def get_parser():
    parser = argparse.ArgumentParser(description='3D GAN Params' )
    parser.add_argument('--model', '-m', action='store', type=str, default='EcalEnergyGan', help='Model architecture to use.')
    parser.add_argument('--nbepochs', action='store', type=int, default=25, help='Number of epochs to train for.')
    parser.add_argument('--batchsize', action='store', type=int, default=126, help='batch size per update')
    parser.add_argument('--latentsize', action='store', type=int, default=128, help='size of random N(0, 1) latent space to sample')
    parser.add_argument('--datapath', action='store', type=str, default='/eos/project/d/dshep/LCD/V1/*scan/*.h5', help='HDF5 files to train from.')
    parser.add_argument('--nbEvents', action='store', type=int, default=200000, help='Number of Data points to use')
    parser.add_argument('--nbperfile', action='store', type=int, default=10000, help='Number of events in a file.')
    parser.add_argument('--verbose', action='store_true', help='Whether or not to use a progress bar')
    parser.add_argument('--weightsdir', action='store', type=str, default='weights2D', help='Directory to store weights.')
    parser.add_argument('--mod', action='store', type=int, default=0, help='How to calculate Ecal sum corressponding to energy.\n [0].. factor 50 \n[1].. Fit from Root')
    parser.add_argument('--xscale', action='store', type=int, default=1, help='Multiplication factor for ecal deposition')
    parser.add_argument('--yscale', action='store', type=int, default=100, help='Division Factor for Primary Energy.')
    parser.add_argument('--learningRate', '-lr', action='store', type=float, default=0.001, help='Learning Rate')
    parser.add_argument('--optimizer', action='store', type=str, default='RMSprop', help='Keras Optimizer to use.')
    parser.add_argument('--intraop', action='store', type=int, default=9, help='Sets onfig.intra_op_parallelism_threads and OMP_NUM_THREADS')
    parser.add_argument('--interop', action='store', type=int, default=1, help='Sets config.inter_op_parallelism_threads')
    parser.add_argument('--warmupepochs', action='store', type=int, default=5, help='No wawrmup epochs')
    parser.add_argument('--channel_format', action='store', type=str, default='channels_last', help='NCHW vs NHWC')
    parser.add_argument('--analysis', action='store', type=bool, default=False, help='Calculate optimisation function')
    return parser


if __name__ == '__main__':

    import keras.backend as K


    from keras.layers import Input
    from keras.models import Model
    from keras.optimizers import Adadelta, Adam, RMSprop
    from keras.utils.generic_utils import Progbar
    from sklearn.cross_validation import train_test_split

    import tensorflow as tf
    import horovod.keras as hvd

    #Values to be set by user
    parser = get_parser()
    params = parser.parse_args()
    print(params)

    d_format = params.channel_format

    if d_format == 'channels_first':
        print('Setting th channel ordering (NCHW)')
        K.set_image_dim_ordering('th')
    else:
        print('Setting tf channel ordering (NHWC)')
        K.set_image_dim_ordering('tf')

    # Initialize Horovod.
    hvd.init()

    config = tf.ConfigProto()#(log_device_placement=True)
    config.gpu_options.allow_growth = True