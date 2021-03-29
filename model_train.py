import torch 
from models.dataset.window_selection_dataset import WindowSelectionDataset
from models.model.window_selection_model import WindowSelectionModel
import torch.nn as nn
if __name__ == '__main__':
    model = WindowSelectionModel()
    dataset = WindowSelectionDataset(64)
    optimizer = torch.optim.Adam(model.parameters(),lr=0.001)
    for epoch in range(len(dataset)):
        data, label = dataset[epoch]
        pred = model(data)
        loss = nn.CrossEntropyLoss()(pred, label.long())
        pred_y = torch.max(pred, 1)[1].data.numpy() 
        accuracy = (pred_y==label.data.numpy()).sum()/label.shape[0]
        print('epoch:{}, loss:{}, acc:{}'.format(epoch, loss, accuracy))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    torch.save(model, './saved_model')

