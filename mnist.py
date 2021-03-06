# https://tensorflow.blog/2017/01/26/pytorch-mnist-example/
# https://github.com/rickiepark/pytorch-examples/blob/master/mnist.ipynb

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class MnistModel(nn.Module):
    def __init__(self):
        super(MnistModel, self).__init__()
        # input is 28x28
        # padding=2 for same padding
        self.conv1 = nn.Conv2d(1, 32, 5, padding=2)
        # feature map size is 14*14 by pooling
        # padding=2 for same padding
        self.conv2 = nn.Conv2d(32, 64, 5, padding=2)
        # feature map size is 7*7 by pooling
        self.fc1 = nn.Linear(64*7*7, 1024)
        self.fc2 = nn.Linear(1024, 10)

    def forward(self, x):
        x = F.max_pool2d(F.relu(self.conv1(x)), 2)
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = x.view(-1, 64*7*7)   # reshape Variable
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        # https://discuss.pytorch.org/t/implicit-dimension-choice-for-softmax-warning/12314/8
        return F.log_softmax(x, dim=1)


model = MnistModel().to(device)
print(model)


batch_size = 50
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('data', train=True, download=True,
                   transform=transforms.ToTensor()),
    batch_size=batch_size, shuffle=True)

test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('data', train=False, transform=transforms.ToTensor()),
    batch_size=1000)

for p in model.parameters():
    print(p.size())

optimizer = optim.Adam(model.parameters(), lr=0.0001)

model.train()
train_loss = []
train_accu = []
i = 0
for epoch in range(15):
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()    # calc gradients
        train_loss.append(loss.data)
        optimizer.step()   # update gradients
        prediction = output.data.max(1)[1]   # first column has actual prob.
        # accuracy = prediction.eq(target.data).sum()/batch_size*100
        # https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
        accuracy = (prediction == target).sum().item()/batch_size*100
        train_accu.append(accuracy)
        if i % 1000 == 0:
            print('Train Step: {}\tLoss: {:.3f}\tAccuracy: {:.3f}'.format(
                i, loss.data, accuracy))
        i += 1

plt.plot(np.arange(len(train_loss)), train_loss)

plt.plot(np.arange(len(train_accu)), train_accu)

model.eval()
correct = 0
for data, target in test_loader:
    data, target = data.to(device), target.to(device)
    output = model(data)
    prediction = output.data.max(1)[1]
    # correct += prediction.eq(target.data).sum()
    correct += (prediction == target).sum().item()

print('\nTest set: Accuracy: {:.2f}%'.format(
    100. * correct / len(test_loader.dataset)))
