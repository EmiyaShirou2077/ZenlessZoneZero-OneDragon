import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import random
import numpy as np
from collections import deque
import os
import cv2

class SnakeDuelAgent(nn.Module):
    def __init__(self, action_space, epsilon=1.0, model_path=None):
        super().__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.action_space = action_space
        self.action_size = len(action_space)
        self.n_step_buffer = deque(maxlen=5)

        # CNN backbone with more layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=8, stride=4)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=4, stride=2)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=2)
        self.conv4 = nn.Conv2d(128, 128, kernel_size=3, stride=1)

        self.fc1_layer = None
        self.out = nn.Linear(512, self.action_size)
        self.to(self.device)

        self.gamma = 0.99
        self.epsilon = epsilon
        self.epsilon_decay = 0.9995
        self.epsilon_min = 0.0
        self.optimizer = optim.Adam(self.parameters(), lr=1e-4)
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        self.episodes = 0

        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "snakeDuel_agent.pth")
        self.model_path = model_path

        self._initialize_fc1_layer()

        if os.path.exists(self.model_path):
            self.load(self.model_path)

    def _initialize_fc1_layer(self):
        with torch.no_grad():
            dummy_input = torch.zeros(1, 3, 830, 954).to(self.device)
            x = F.relu(self.conv1(dummy_input), inplace=False)
            x = F.relu(self.conv2(x), inplace=False)
            x = F.relu(self.conv3(x), inplace=False)
            x = F.relu(self.conv4(x), inplace=False)
            feature_dim = x.reshape(1, -1).shape[1]
            self.fc1_layer = nn.Linear(feature_dim, 512).to(self.device)

    def forward(self, x):
        x = F.relu(self.conv1(x), inplace=False)
        x = F.relu(self.conv2(x), inplace=False)
        x = F.relu(self.conv3(x), inplace=False)
        x = F.relu(self.conv4(x), inplace=False)
        x = x.reshape(x.size(0), -1)
        x = F.relu(self.fc1_layer(x), inplace=False)
        return self.out(x)

    def _preprocess(self, img):
        return img.astype(np.float32) / 255.0

    def get_action(self, state):
        state = self._preprocess(state)
        if np.random.rand() <= self.epsilon:
            return random.choice(self.action_space)

        state_tensor = torch.tensor(state).permute(2, 0, 1).unsqueeze(0).to(self.device)
        q_values = self(state_tensor)
        action_idx = torch.argmax(q_values, dim=1).item()
        return self.action_space[action_idx]

    def remember(self, state, action, reward, next_state, done):
        state = self._preprocess(state)
        next_state = self._preprocess(next_state)
        self.n_step_buffer.append((state, action, reward, next_state, done))

        if done:
            for i, (s, a, r, ns, d) in enumerate(reversed(self.n_step_buffer)):
                if i == 0:
                    r += -10
                self.memory.append((s, a, r, ns, d))
            self.n_step_buffer.clear()
        else:
            self.memory.append((state, action, reward, next_state, done))

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(np.stack(states)).permute(0, 3, 1, 2).to(self.device)
        next_states = torch.tensor(np.stack(next_states)).permute(0, 3, 1, 2).to(self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
        dones = torch.tensor(dones, dtype=torch.float32).to(self.device)

        action_indices = [self.action_space.index(a) for a in actions]
        actions_tensor = torch.tensor(action_indices).to(self.device)

        q_values = self(states)
        q_action = q_values.gather(1, actions_tensor.unsqueeze(1)).squeeze()

        with torch.no_grad():
            q_next = self(next_states).max(1)[0]
            q_target = rewards + self.gamma * q_next * (1 - dones)

        loss = F.mse_loss(q_action, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path=None):
        torch.save({
            'model_state_dict': self.state_dict(),
            'episodes': self.episodes
        }, path or self.model_path)

    def load(self, path=None):
        checkpoint = torch.load(path or self.model_path, map_location=self.device)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.episodes = checkpoint.get('episodes', 0)
        self.eval()