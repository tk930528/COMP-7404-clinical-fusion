import sys

import os
import sys
import time
import numpy as np
from sklearn import metrics
import random
import json
from glob import glob
from collections import OrderedDict
from tqdm import tqdm


import torch
from torch.autograd import Variable
from torch.backends import cudnn
from torch.nn import DataParallel
from torch.utils.data import DataLoader

import data_loader
import lstm, cnn
import myloss
import function
from utils import cal_metric

sys.path.append('./tools')
import parse, py_op

args = parse.args
args.embed_size = 200
args.hidden_size = args.rnn_size = args.embed_size
if torch.cuda.is_available():
    args.gpu = 1
else:
    args.gpu = 0

args.use_ve = 1
args.n_visit = 24

args.use_unstructure = None
if(args.use_unstructure is None):
    args.use_unstructure = args.use_text
    
args.value_embedding = 'use_order'
# args.value_embedding = 'no'
print ('epochs,', args.epochs)

#args.task = 'llos'

args.files_dir = args.files_dir
args.data_dir = args.data_dir

def _cuda(tensor, is_tensor=True):
    if args.gpu:
        if is_tensor:
            return tensor.cuda(non_blocking=True)
        else:
            return tensor.cuda()
    else:
        return tensor

def get_lr(epoch):
    if epoch <= args.epochs * 0.5:
        lr = args.lr
    elif epoch <= args.epochs * 0.75:
        lr = 0.1 * args.lr
    else:
        lr = 0.01 * args.lr
    return lr

def index_value(data):
    '''
    map data to index and value
    '''
    if args.use_ve == 0:
        data = Variable(_cuda(data)) # [bs, 250]
        return data
    data = data.numpy()
    index = data / (args.split_num + 1)
    value = data % (args.split_num + 1)
    index = Variable(_cuda(torch.from_numpy(index.astype(np.int64))))
    value = Variable(_cuda(torch.from_numpy(value.astype(np.int64))))
    return [index, value]

def train_eval(data_loader, net, loss, epoch, optimizer, best_metric, phase='train'):
    print(phase)
    lr = get_lr(epoch)
    if phase == 'train':
        net.train()
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
    else:
        net.eval()

    loss_list, pred_list, label_list, = [], [], []
    for b, data_list in enumerate(tqdm(data_loader)):
        data, dtime, demo, content, label, files = data_list
        if args.value_embedding == 'no':
            data = Variable(_cuda(data))
        else:
            data = index_value(data)


        dtime = Variable(_cuda(dtime))
        demo = Variable(_cuda(demo))
        content = Variable(_cuda(content))
        label = Variable(_cuda(label))
        
        output = None
        if (args.use_unstructure==1):
            output = net(data, dtime, demo, content) # [bs, 1]
        else:
            output = net(data, dtime, demo) # [bs, 1]



        loss_output = loss(output, label)
        pred_list.append(output.data.cpu().numpy())
        loss_list.append(loss_output[0].data.cpu().numpy())
        label_list.append(label.data.cpu().numpy())

        if phase == 'train':
            optimizer.zero_grad()
            loss_output[0].backward()
            optimizer.step()

    pred = np.concatenate(pred_list, 0)
    label = np.concatenate(label_list, 0)
    if len(pred.shape) == 1:
        metric = function.compute_auc(label, pred)
    else:
        metrics = []
        auc_metrics = []
        for i_shape in range(pred.shape[1]):
            metric0 = cal_metric(label[:, i_shape], pred[:, i_shape])
            auc_metric = function.compute_auc(label[:, i_shape], pred[:, i_shape])
            # print('........AUC_{:d}: {:3.4f}, AUPR_{:d}: {:3.4f}'.format(i_shape, auc, i_shape, aupr))
            print(i_shape + 1, metric0)
            metrics.append(metric0)
            auc_metrics.append(auc_metric)
        print('Avg', np.mean(metrics, axis=0).tolist())
        metric = np.mean(auc_metrics)
    avg_loss = np.mean(loss_list)

    print('\n{:s} Epoch {:d} (lr {:3.6f})'.format(phase, epoch, lr))
    print('loss: {:3.4f} \t'.format(avg_loss))
    print('auc: {:3.4f} \t'.format(metric))
    if phase == 'valid' and (best_metric[0] < metric or np.mean(metrics, axis=0).tolist()[0]>0.6 or avg_loss<=0.2):
        print('best_metric is updated to {0}'.format(metric))
        best_metric = [metric, epoch]
        function.save_model({'args': args, 'model': net, 'epoch':epoch, 'best_metric': best_metric})
    if phase != 'train':
        print('\t\t\t\t best epoch: {:d}     best AUC: {:3.4f} \t'.format(best_metric[1], best_metric[0])) 
    return best_metric


def main():
    args.n_ehr = len(json.load(open(os.path.join(args.files_dir, 'demo_index_dict.json'), 'r'))) + 10
    args.name_list = json.load(open(os.path.join(args.files_dir, 'feature_list.json'), 'r'))[1:]
    args.input_size = len(args.name_list)
    files = sorted(glob(os.path.join(args.data_dir, 'resample_data/*.csv')))
    data_splits = json.load(open(os.path.join(args.files_dir, 'splits.json'), 'r'))
    train_files = [f for idx in [0, 1, 2, 3, 4, 5, 6] for f in data_splits[idx]]
    valid_files = [f for idx in [7] for f in data_splits[idx]]
    test_files = [f for idx in [8, 9] for f in data_splits[idx]]
    if args.phase == 'test':
        train_phase, valid_phase, test_phase, train_shuffle = 'test', 'test', 'test', False
    else:
        train_phase, valid_phase, test_phase, train_shuffle = 'train', 'valid', 'test', True
    train_dataset = data_loader.DataBowl(args, train_files, phase=train_phase)
    valid_dataset = data_loader.DataBowl(args, valid_files, phase=valid_phase)
    test_dataset = data_loader.DataBowl(args, test_files, phase=test_phase)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=train_shuffle, num_workers=args.workers, pin_memory=True)
    valid_loader = DataLoader(valid_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=args.workers, pin_memory=True)

    args.vocab_size = args.input_size + 2

    '''
    if args.use_unstructure:
        len_vocab_list = len(json.load(open(os.path.join(args.files_dir, 'vocab_list.json'), 'r')))
        print('unstructure:',len_vocab_list)
        args.unstructure_size = len_vocab_list + 10
    '''
    
    if args.model == 'cnn':
        print('Training CNN...')
        net = cnn.CNN(args)
        torch.save(net, 'cnn.pt')
    else:
        print('Training LSTM...')
        net = lstm.LSTM(args)
    # net = torch.nn.DataParallel(net)
    # loss = myloss.Loss(0)
    loss = myloss.MultiClassLoss(0)

    net = _cuda(net, 0)
    loss = _cuda(loss, 0)

    best_metric= [0,0]
    start_epoch = 0

    if args.phase == 'test':
        print('Resuming...')
        p_dict = {'model': net}
        function.load_model(p_dict, 'models/best.ckpt')
        best_metric = p_dict['best_metric']
        start_epoch = p_dict['epoch'] + 1

        num_params = sum(p.numel() for p in net.parameters() if p.requires_grad)
        print('number of parameters: {}'.format(num_params))


    parameters_all = []
    for p in net.parameters():
        parameters_all.append(p)

    optimizer = torch.optim.Adam(parameters_all, args.lr)

    if args.phase == 'train':
        for epoch in range(start_epoch, args.epochs):
            print('start epoch :', epoch)
            t0 = time.time()
            t0_process = time.process_time()
            train_eval(train_loader, net, loss, epoch, optimizer, best_metric)
            t1 = time.time()
            t1_process = time.process_time()
            print('Wall time:', t1 - t0)
            print('CPU time:', t1_process - t0_process)
            best_metric = train_eval(valid_loader, net, loss, epoch, optimizer, best_metric, phase='valid')
        print('best metric', best_metric)

    elif args.phase == 'test':
        train_eval(test_loader, net, loss, 0, optimizer, best_metric, 'test')

if __name__ == '__main__':
    print(args)
    main()
