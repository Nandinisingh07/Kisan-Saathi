import tensorflow as tf

model = tf.keras.models.load_model('crop_disease_model.h5', compile=False)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open('crop_disease_model.tflite', 'wb') as f:
    f.write(tflite_model)

print('Conversion done. File size (MB):', len(tflite_model) / (1024*1024))
