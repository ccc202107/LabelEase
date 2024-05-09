from model import *
from config import *
from dataset import TraceDataset
from torch.utils.data import DataLoader
import numpy as np
import torch
import os
import time
from tqdm import tqdm
from torch import optim
from loguru import logger


def torch_seed(seed=2020):
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def main():
    torch_seed(seed)

    logger.info('loading trace dataset')
    dataset = TraceDataset(data_type)  

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=TraceDataset.collate_fn)
    # device = torch.device('cuda:{}'.format(args.gpu_id))
    device = torch.device('cpu')

    # 初始化模型
    gnn=GAT(embedding_size = embed_dim, hidden_dims = embed_dim,num_layers = num_layers).to(device)

    siamese_gnn = SiameseGNN(gnn).to(device)
    loss_func = ContrastiveLoss().to(device)
    optimizer = optim.Adam(siamese_gnn.parameters(), lr=learning_rate)
    fw=open(f"{out_path}/log.txt",'w')
    start_time = time.time()
    # 训练模型
    for e in range(epoch):
        total_loss = 0
        for data1, data2, data3 in tqdm(loader):
            optimizer.zero_grad()
            emb1, emb2, emb3 = siamese_gnn(data1, data2, data3, device)
            loss = loss_func(emb1, emb2, emb3)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        logger.info(f"Epoch {e+1}/{epoch}, Loss: {total_loss}")
        fw.write(f"Epoch {e+1}/{epoch}, Loss: {total_loss}\n")
        torch.save(gnn.state_dict(),os.path.join(save_dir,f"gnn_model_param_{e+1}epoch.pkl"))
    end_time = time.time()
    fw.write(f"\ntotal training time: {end_time-start_time}")
    torch.save(gnn.state_dict(),os.path.join(save_dir,f"gnn_model_param.pkl"))
    fw.close()

if __name__ == "__main__":
    main()