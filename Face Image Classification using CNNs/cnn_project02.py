#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 22:34:36 2018

@author: MyReservoir
"""

def cnn_model_fn(features, labels, mode):
  """Model function for CNN."""
  
  # Input Layer
  # Reshape X to 4-D tensor: [batch_size, width, height, channels]
  # LFW images are 60X60 pixels, and have one color channel
  input_layer = tf.reshape(features["x"], [-1, 60, 60, 1])
  
  
  # Convolutional Layer #1
  # Computes 32 features using a 5x5 filter with ReLU activation.
  # Padding is added to preserve width and height.
  # Input Tensor Shape: [batch_size, 60, 60, 1]
  # Output Tensor Shape: [batch_size, 60, 60, 32]
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)
  
  
  # Pooling Layer #1
  # First max pooling layer with a 2x2 filter and stride of 2
  # Input Tensor Shape: [batch_size, 60, 60, 32]
  # Output Tensor Shape: [batch_size, 30, 30, 32]
  pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)
  
  
  # Convolutional Layer #2
  # Computes 64 features using a 5x5 filter.
  # Padding is added to preserve width and height.
  # Input Tensor Shape: [batch_size, 30, 30, 32]
  # Output Tensor Shape: [batch_size, 30, 30, 64]
  conv2 = tf.layers.conv2d(
      inputs=pool1,
      filters=64,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)
  
  
  # Pooling Layer #2
  # Second max pooling layer with a 2x2 filter and stride of 2
  # Input Tensor Shape: [batch_size, 30, 30, 64]
  # Output Tensor Shape: [batch_size, 10, 10, 64]
  pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[3, 3], strides=2)
  
  
  # Flatten tensor into a batch of vectors
  # Input Tensor Shape: [batch_size, 10, 10, 64]
  # Output Tensor Shape: [batch_size, 7 * 7 * 64]
  pool2_flat = tf.reshape(pool2, [-1, 7 * 7 * 256])
  
  
  # Dense Layer
  # Densely connected layer with 1024 neurons
  # Input Tensor Shape: [batch_size, 7 * 7 * 64]
  # Output Tensor Shape: [batch_size, 1024]
  dense = tf.layers.dense(inputs=pool2_flat, units=1024, activation=tf.nn.relu)
  
  
  # Add dropout operation; 0.6 probability that element will be kept
  dropout = tf.layers.dropout(
      inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)
  
  
  # Logits layer
  # Input Tensor Shape: [batch_size, 1024]
  # Output Tensor Shape: [batch_size, 2]
  logits = tf.layers.dense(inputs=dropout, units=2)
  predictions = {
      "classes": tf.argmax(input=logits, axis=1),
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }
  print("predictions", predictions)
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
    
  # Calculate Loss (for both TRAIN and EVAL modes)
  onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=2)
  loss = tf.losses.softmax_cross_entropy(
    onehot_labels=onehot_labels, logits=logits)
  
  # Configure the Training Op (for TRAIN mode)
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.0001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)
  
  # Add evaluation metrics (for EVAL mode)
  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def main(unused_argv):
  train_data_face = [[0]* 3600] * 13000
  train_data_face = np.array(train_data_face)
  non_train_data = [[0]* 3600] * 13000
  non_train_data = np.array(non_train_data)
  test_data_face = [[0]* 3600] * 101
  test_data_face = np.array(test_data_face)
  test_data_non_face = [[0]* 3600] * 101
  test_data_non_face = np.array(test_data_non_face)
  
  
  # Load training and test data
  train_path = '/Users/MyReservoir/Desktop/Project2/train/face'
  os.chdir(train_path)
  a = 1
  for faces in glob.glob('*.jpg'):
      print(1)
      print(2)
      print("Faces:", faces)
      face_obj = cv2.imread(faces, 0)
      face_obj = cv2.resize(face_obj, (60, 60))
      face_obj_flatten = face_obj.flatten()
      print(face_obj_flatten.shape)
      train_data_face[a,:] = face_obj_flatten
      a = a + 1
  non_train_path = '/Users/MyReservoir/Desktop/Project2/test/face'
  os.chdir(non_train_path)
  a = 1
  for non_faces in glob.glob('*.jpg'):
      face_obj = cv2.imread(non_faces, 0)
      face_obj = cv2.resize(face_obj, (60, 60))
      face_obj_flatten = face_obj.flatten()
      print(face_obj_flatten.shape)
      non_train_data[a,:] = face_obj_flatten
      a = a + 1
  print(np.asarray(non_train_data).shape)
  train_labels_face = np.asarray(np.zeros(len(train_data_face)), dtype=np.int32)
  train_labels_non_face = np.asarray(np.ones(len(non_train_data)), dtype=np.int32)
  train_data = np.concatenate((train_data_face, non_train_data), axis = 0)
  train_data = np.float32(train_data)
  train_labels = np.concatenate((train_labels_face, train_labels_non_face), axis = 0)
  print("Train data:", train_data.shape )
  print("Train Labels:", train_labels.shape)
  
  test_path = "/Users/MyReservoir/Desktop/Project2/test/nonface"
  os.chdir(test_path)
  b = 1
  for faces in glob.glob('*.jpg'):
      print(1)
      print(2)
      print("Faces:", faces)
      face_obj = cv2.imread(faces, 0)
      face_obj = cv2.resize(face_obj, (60, 60))
      face_obj_flatten = face_obj.flatten()
      print(face_obj_flatten.shape)
      test_data_face[b,:] = face_obj_flatten
      b = b + 1
  non_test_path = "/Users/MyReservoir/Desktop/Project2/train/nonface"
  os.chdir(non_test_path)
  b = 1
  for non_faces in glob.glob('*.jpg'):
      print(3)
      print(4)
      face_obj = cv2.imread(non_faces, 0)
      face_obj = cv2.resize(face_obj, (60, 60))
      face_obj_flatten = face_obj.flatten()
      print(face_obj_flatten.shape)
      test_data_non_face[b,:] = face_obj_flatten
      b = b + 1
  test_labels_face = np.asarray(np.zeros(len(test_data_face)), dtype=np.int32)
  test_labels_non_face = np.asarray(np.ones(len(test_data_non_face)), dtype=np.int32)
  eval_data = np.concatenate((test_data_face, test_data_non_face), axis = 0)
  eval_data = np.float32(eval_data)
  eval_labels = np.concatenate((test_labels_face, test_labels_non_face), axis = 0)
  
  
  mnist_classifier = tf.estimator.Estimator(
      model_fn=cnn_model_fn)
  

  tensors_to_log = {"probabilities": "softmax_tensor"}
  logging_hook = tf.train.LoggingTensorHook(
      tensors=tensors_to_log, every_n_iter=50)
  
  
  train_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": train_data},
      y=train_labels,
      batch_size=100,
      num_epochs=1000,
      shuffle=True)
  mnist_classifier.train(
      input_fn=train_input_fn,
      steps=5000,
      hooks=[logging_hook])
  
  
  eval_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": eval_data},
      y=eval_labels,
      num_epochs=1,
      shuffle=False)
  eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
  print("Eval_Results:", eval_results)


if __name__ == "__main__":
  tf.app.run()