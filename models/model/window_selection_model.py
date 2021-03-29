import torch
import torch.nn as nn
class WindowSelectionModel(nn.Module):
    def __init__(self):
        super(WindowSelectionModel, self).__init__()
        self.feature_dim = 12
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=(3, 1), stride=1, padding=(1, 0))
        self.relu1 = nn.ReLU()
        
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=1, kernel_size=(3, 1), stride=1, padding=(1, 0))
        self.relu2 = nn.ReLU()
        self.fc1 = nn.Linear(in_features=self.feature_dim, out_features=64)
        self.relu3 = nn.ReLU()
        self.fc2 = nn.Linear(in_features=64, out_features=2)

    def forward(self, x):
        output = self.relu1(self.conv1(x))
        output = self.relu2(self.conv2(output))

        output = output.reshape([-1, self.feature_dim])
        output = self.relu3(self.fc1(output))
        output = self.fc2(output)
        output = output.reshape(x.shape[0], -1, 2)
        result = torch.zeros([output.shape[0], output.shape[1]+1])
        result[:, 0] = output[:, 0, 0]
        result[:, 1:-1] = (output[:, 1:, 0] + output[:, 0:-1, 1])/2
        result[:, -1] = output[:, -1, 1]
        return result