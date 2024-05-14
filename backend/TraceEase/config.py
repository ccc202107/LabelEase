import argparse
import os


parser = argparse.ArgumentParser()

parser.add_argument('--seed', type=int, default=1)
parser.add_argument('--classes', type=int, default=2)
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--learning_rate', type=float, default=0.0001)
parser.add_argument('--epoch', type=int, default=5)
# parser.add_argument('--epoch', type=int, default=15)
parser.add_argument('--gpu_id', type=int, default=1)
parser.add_argument('--embed_dim', type=int, default=782)
parser.add_argument('--out_dir', type=str, default='0430')
parser.add_argument('--num_layers', type=int, default=3)
parser.add_argument('--data_type', type=str,default="data1")
parser.add_argument('--p', type=int,default=35)
parser.add_argument('--SAMPLE_NUM', type=int,default=60000)

args = parser.parse_args()

seed=args.seed
classes=args.classes
batch_size=args.batch_size
learning_rate=args.learning_rate
epoch=args.epoch
gpu_id=args.gpu_id
embed_dim=args.embed_dim
out_dir=args.out_dir
num_layers=args.num_layers
data_type=args.data_type
p=args.p
SAMPLE_NUM=args.SAMPLE_NUM

# data_root += data_type
out_path = f"Output"
# out_path = f"Output/{data_type}_{out_dir}__{epoch}epoch_{learning_rate}lr_{batch_size}bs_{num_layers}layers"
save_dir = os.path.join(out_path,"model_save")
if not os.path.exists(out_path):
    os.mkdir(out_path)
if not os.path.exists(save_dir):
    os.mkdir(save_dir)


