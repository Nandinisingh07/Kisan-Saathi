import tensorflow as tf
import numpy as np

model_path = "crop_disease_model.h5"

print("Loading existing crop disease model...")
model = tf.keras.models.load_model(model_path)

# Extract dense layer
dense_layer = model.get_layer("dense_1")
weights, biases = dense_layer.get_weights()

print("Original weights shape:", weights.shape) # (128, 16)
print("Original biases shape:", biases.shape)   # (16,)

# Create expanded weights and biases
new_output_dim = 26
new_weights = np.zeros((weights.shape[0], new_output_dim))
new_biases = np.zeros((new_output_dim,))

# Copy old weights
new_weights[:, :16] = weights
new_biases[:16] = biases

# Initialize new weights with small random values
new_weights[:, 16:] = np.random.normal(0.0, 0.01, (weights.shape[0], 10))
new_biases[16:] = 0.0

# Create new sequential model copying all old layers except the last one
new_model = tf.keras.models.Sequential()
for layer in model.layers[:-1]:
    new_model.add(layer)

# Add new dense layer
new_model.add(tf.keras.layers.Dense(new_output_dim, activation="softmax", name="dense_1"))

# Build model
new_model.build((None, 128, 128, 3))

# Copy weights
for i in range(len(model.layers) - 1):
    new_model.layers[i].set_weights(model.layers[i].get_weights())

new_model.layers[-1].set_weights([new_weights, new_biases])

# Save expanded model
new_model.save("crop_disease_model.h5")
print("Expanded sequential model saved successfully!")
