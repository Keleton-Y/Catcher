import os
import random
import numpy as np
import tensorflow as tf
import tensorlayer as tl

# DDQN parameters
GAMMA = 0.995
LR = 0.005
BATCH_SIZE = 32
EPS = 0.1
# Training parameters
TRAIN_EPISODES = 200
TEST_EPISODES = 10
# Algorithm and environment names
ALG_NAME = 'DDQN'
ENV_ID = 'SC'


class ReplayBuffer:
    def __init__(self, capacity=250000):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = int((self.position + 1) % self.capacity)

    def sample(self, batch_size=BATCH_SIZE):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        """ 
        the * serves as unpack: sum(a,b) <=> batch=(a,b), sum(*batch) ;
        zip: a=[1,2], b=[2,3], zip(a,b) => [(1, 2), (2, 3)] ;
        the map serves as mapping the function on each list element: map(square, [2,3]) => [4,9] ;
        np.stack((1,2)) => array([1, 2])
        """
        return state, action, reward, next_state, done


class Agent:
    def __init__(self, n_state, n_action):
        # dim format: number   state format: []
        self.state_dim = n_state
        self.action_dim = n_action

        def create_model(input_state_shape):
            input_layer = tl.layers.Input(input_state_shape)
            layer_1 = tl.layers.Dense(n_units=32, act=tf.nn.relu)(input_layer)
            layer_2 = tl.layers.Dense(n_units=64, act=tf.nn.relu)(layer_1)
            output_layer = tl.layers.Dense(n_units=self.action_dim)(layer_2)
            return tl.models.Model(inputs=input_layer, outputs=output_layer)

        self.model = create_model([None, self.state_dim])
        self.target_model = create_model([None, self.state_dim])
        self.model.train()
        self.target_model.eval()
        self.model_optim = tf.optimizers.Adam(lr=LR)
        # Greedy factor
        self.epsilon = EPS
        # Experience buffer
        self.buffer = ReplayBuffer()

    def target_update(self):
        """Copy q network to target q network"""
        for weights, target_weights in zip(
                self.model.trainable_weights, self.target_model.trainable_weights):
            target_weights.assign(weights)

    def choose_action(self, state):
        if np.random.uniform() < self.epsilon:
            return np.random.choice(self.action_dim)
        else:
            q_value = self.model(np.array([state], dtype=np.float32)[np.newaxis, :])[0]
            return np.argmax(q_value)

    def replay(self, times=10):
        for _ in range(times):
            states, actions, rewards, next_states, done = self.buffer.sample()
            # targets [batch_size, action_dim]
            # Target represents the current fitting level
            target = self.target_model(states)
            target = target.numpy()
            # next_q_values [batch_size, action_diim]
            next_target = self.target_model(next_states).numpy()
            # next_q_value [batch_size, 1]
            next_q_value = next_target[
                range(BATCH_SIZE), np.argmax(self.model(next_states), axis=1)
            ]
            # next_q_value = tf.reduce_max(next_q_value, axis=1)
            target[range(BATCH_SIZE), actions] = rewards + (1 - done) * GAMMA * next_q_value

            # use sgd to update the network weight
            with tf.GradientTape() as tape:
                q_pred = self.model(states)
                loss = tf.losses.mean_squared_error(target, q_pred)
            grads = tape.gradient(loss, self.model.trainable_weights)
            self.model_optim.apply_gradients(zip(grads, self.model.trainable_weights))

    def get_action(self, state, learn):
        if learn:
            return self.choose_action(state)
        else:
            action = self.model(np.array([state], dtype=np.float32))[0]
            action = np.argmax(action)
            return action

    def saveModel(self, ex=''):
        path = os.path.join('model'+ex, '_'.join([ALG_NAME, ENV_ID]))
        if not os.path.exists(path):
            os.makedirs(path)
        tl.files.save_weights_to_hdf5(os.path.join(path, 'model.hdf5'), self.model)
        tl.files.save_weights_to_hdf5(os.path.join(path, 'target_model.hdf5'), self.target_model)
        print('Saved weights.')

    def loadModel(self):
        path = os.path.join('model', '_'.join([ALG_NAME, ENV_ID]))
        if os.path.exists(path):
            print('Load DQN Network parameters ...')
            tl.files.load_hdf5_to_weights_in_order(os.path.join(path, 'model.hdf5'), self.model)
            tl.files.load_hdf5_to_weights_in_order(os.path.join(path, 'target_model.hdf5'), self.target_model)
            print('Load weights!')
        else:
            print("No model file find, please train model first...")


if __name__ == '__main__':
    pass
