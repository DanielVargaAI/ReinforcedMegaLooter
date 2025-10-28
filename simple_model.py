import torch
import torch.nn as nn
import torch.nn.functional as F
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor
from simple_settings import *


class VisionActionNet(nn.Module):
    """Eigenes CNN-Modell für Feature-Extraktion und Action-Regression"""
    def __init__(self, input_channels=3, num_actions=4):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(input_channels, 16, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2),
            nn.ReLU(),
            nn.Flatten()
        )

        with torch.no_grad():
            dummy = torch.zeros(1, input_channels, scale_to_y, scale_to_x)
            n_flat = self.features(dummy).shape[1]

        self.fc_shared = nn.Sequential(
            nn.Linear(n_flat, 512),
            nn.ReLU()
        )

        # Für Tests – nicht Teil von SB3 direkt
        self.coord_head = nn.Sequential(
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Linear(128, 2),
            nn.Sigmoid()
        )
        self.action_head = nn.Linear(512, num_actions)

    def forward(self, x):
        x = x / 255.0
        feats = self.features(x)
        shared = self.fc_shared(feats)
        coords = self.coord_head(shared)
        actions = self.action_head(shared)
        return coords, actions


class CustomFeatureExtractor(BaseFeaturesExtractor):
    """Wrapper für SB3, der nur die Features extrahiert"""
    def __init__(self, observation_space, features_dim=512):
        super().__init__(observation_space, features_dim)
        input_channels = observation_space.shape[0]
        self.cnn = VisionActionNet(input_channels=input_channels)
        self._features_dim = 512

    def forward(self, observations):
        x = observations / 255.0
        feats = self.cnn.features(x)
        return self.cnn.fc_shared(feats)
