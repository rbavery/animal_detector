################
#
# train.py
#
# Trains a FasterRCNN-based detector for the wildlife classification project.
#
# Most of the actual training is deferred to the FasterRCNNTrainer class in trainer.py.
#
################

import os
import matplotlib
from tqdm import tqdm
import time
import numpy as np
import tensorboardX
import datetime 
import glob
import shutil
import torch.utils.data
import torch

from utils.config import opt
from data.dataset import Dataset, TestDataset, inverse_normalize
from model import FasterRCNNVGG16
from torch.autograd import Variable
from torch.utils import data as data_
from trainer import FasterRCNNTrainer
from utils import array_tool as at
from utils.vis_tool import visdom_bbox
from utils.eval_tool import eval_detection_voc

torch.set_num_threads(1)

# matplotlib.use('agg')
import torch.backends.cudnn as cudnn
cudnn.benchmark = True

# Prepare logging
log_dir = './log/run_{}'.format(datetime.datetime.now().strftime('%b%d_%H-%M-%S'))

# The summary file will contain most of the print outputs for convenience
log_summary_file = os.path.join(log_dir, 'summary.txt')

# The object for logging tensorboard events
writer = tensorboardX.SummaryWriter(log_dir=log_dir)

# Copy all python files to the log directly
log_py_dir = os.path.join(log_dir, 'code')
os.makedirs(log_py_dir)
for fi in  glob.glob('./*.py'):
    shutil.copyfile(fi, os.path.join(log_py_dir, fi))


def eval(dataloader, faster_rcnn, trainer, dataset, global_step, test_num=10000):
    """
    Evaluates a trained detector on a data set.
    """

    with torch.no_grad():

        print('Running validation')
        # Each predicted box is organized as :`(y_{min}, x_{min}, y_{max}, x_{max}), 
        # Where y corresponds to the height and x to the width
        pred_bboxes, pred_labels, pred_scores = list(), list(), list()
        gt_bboxes, gt_labels, gt_difficults = list(), list(), list()
        image_ids = list()

        for ii, (imgs, sizes, gt_bboxes_, gt_labels_, gt_difficults_, image_ids_) in tqdm(
                                                         enumerate(dataloader), total=test_num):
            sizes = [sizes[0].detach().numpy().tolist()[0],  sizes[1].detach().numpy().tolist()[0]]
            pred_bboxes_, pred_labels_, pred_scores_ = faster_rcnn.predict(imgs, [sizes])
            
            # We have to add .copy() here to allow for the loaded image to be released after each iteration
            if len(gt_bboxes_) > 0:
            
                # The original loader creates numpy arrays
                if hasattr(gt_bboxes_, 'numpy'):
                    gt_bboxes += list(gt_bboxes_.numpy().copy())
            
                # To support empty images, we have to switch to lists and hence we also need to support these here
                else:
                    gt_bboxes.append([[j.item() for j in i] for i in gt_bboxes_])
            else:
                gt_bboxes += []
            gt_labels += list(gt_labels_.numpy().copy())
            gt_difficults += list(gt_difficults_.numpy().copy())
            image_ids += list(image_ids_.numpy().copy())
            pred_bboxes += [pp.copy() for pp in pred_bboxes_]
            pred_labels += [pp.copy() for pp in pred_labels_]
            pred_scores += [pp.copy() for pp in pred_scores_]
            if ii == test_num: break

        result = eval_detection_voc(
            pred_bboxes, pred_labels, pred_scores,
            gt_bboxes, gt_labels, gt_difficults,
            use_07_metric=True)

        if opt.validate_only:
            save_path = '{}_detections.npz'.format(opt.load_path)
            np.savez(save_path, pred_bboxes=pred_bboxes, 
                                pred_labels=pred_labels,
                                pred_scores=pred_scores,
                                gt_bboxes=gt_bboxes, 
                                gt_labels=gt_labels, 
                                gt_difficults=gt_difficults,
                                image_ids=image_ids,
                                result=result)
        else:
            classwise_ap = dict()
            for cname, ap in zip(dataset.get_class_names(), result['ap']):
                classwise_ap[cname] = ap
            writer.add_scalars('validation/classwise_ap', classwise_ap, global_step)
            writer.add_scalar('validation/mAP', result['map'], global_step)
            writer.add_scalars('validation/prec@recall', result['prec@recall'], global_step)

            ori_img_ = inverse_normalize(at.tonumpy(imgs[0]))
            gt_img = visdom_bbox(ori_img_,
                                 at.tonumpy(gt_bboxes[-1]),
                                 at.tonumpy(gt_labels[-1]),
                                 label_names=dataset.get_class_names()+['BG'])
            writer.add_image('test_gt_img', gt_img, global_step)

            # plot predicted bboxes
            pred_img = visdom_bbox(ori_img_,
                                   at.tonumpy(pred_bboxes[-1]),
                                   at.tonumpy(pred_labels[-1]).reshape(-1),
                                   at.tonumpy(pred_scores[-1]),
                                   label_names=dataset.get_class_names()+['BG'])
            writer.add_image('test_pred_img', pred_img, global_step)


        del imgs, gt_bboxes_, gt_labels_, gt_difficults_, image_ids_, pred_bboxes_, pred_labels_, pred_scores_
        torch.cuda.empty_cache()
        return result


def train(**kwargs):
    """
    The main entry point for training; trains a FasterRCNN-based detector.
    """

    opt._parse(kwargs)

    # Loading class names from checkpoint, if available
    # We need to load the checkpoint here 
    if opt.load_path:
        old_state = torch.load(opt.load_path)
        class_names = old_state['class_names']
        best_map = old_state['best_map']
    else:
        class_names = []
        best_map = 0
        old_state = None

    print('load data')
    dataset = Dataset(opt, class_names)
    dataloader = data_.DataLoader(dataset, \
                                  batch_size=1, \
                                  shuffle=True, \
                                  # pin_memory=True,
                                  num_workers=opt.num_workers)

    testset = TestDataset(opt, dataset.get_class_names())
    test_dataloader = data_.DataLoader(testset, \
                                       batch_size=1, \
                                       num_workers=opt.test_num_workers,
                                       shuffle=False, \
                                       pin_memory=True
                                       )

    faster_rcnn = FasterRCNNVGG16(n_fg_class=dataset.get_class_count())
    print('Model construct completed')
    trainer = FasterRCNNTrainer(faster_rcnn, n_fg_class=dataset.get_class_count())


    if opt.use_cuda:

        trainer = trainer.cuda()

    if opt.load_path:

        trainer.load(old_state)
        print_log('load pretrained model from %s' % opt.load_path)

    if opt.validate_only:

        num_eval_images = len(testset)
        eval_result = eval(test_dataloader, faster_rcnn, trainer, testset, global_step, test_num=num_eval_images)
        print_log('Evaluation finished, obtained {} using {} out of {} images'.
                format(eval_result, num_eval_images, len(testset)))
        return
    
    if old_state and 'epoch' in old_state.keys():

        starting_epoch = old_state['epoch'] + 1
        print_log('Model was trained until epoch {}, continuing with epoch {}'.format(old_state['epoch'], starting_epoch))

    else:

        starting_epoch = 0
    
    lr_ = opt.lr
    global_step = 0

    for epoch in range(starting_epoch, opt.num_epochs):

        writer.add_scalar('epoch', epoch, global_step)
        lr_ = opt.lr * (opt.lr_decay ** np.sum(epoch >= np.array(opt.lr_schedule)))
        trainer.faster_rcnn.set_lr(lr_)

        print_log('Starting epoch {} with learning rate {}'.format(epoch, lr_))
        trainer.reset_meters()
        for ii, (img, bbox_, label_, scale) in tqdm(enumerate(dataloader), total=len(dataset)):
            global_step = global_step + 1
            scale = at.scalar(scale).item()
            if opt.use_cuda: 
                img = img.cuda().float()
                label = label_.float().cuda()

                if len(bbox_[0]) > 0:
                    bbox = bbox_.float().cuda()
                else:
                    bbox = bbox_
            else:
                
                img, label = img.float(),  label_.float()
                if len(bbox_[0]) > 0:
                    bbox = bbox_.float()
                else:
                    bbox = bbox_

            img, label = Variable(img), Variable(label)
            if len(bbox[0]) > 0:
                bbox = Variable(bbox)    
            else:
                bbox = np.asarray(bbox)
            
            #img, bbox, label = Variable(img), Variable(bbox), Variable(label)
            losses = trainer.train_step(img, bbox, label, scale)

            writer.add_scalars('training/losses', dict(total_loss=losses.total_loss,
                                                       roi_cls_loss=losses.roi_cls_loss,
                                                       roi_loc_loss=losses.roi_loc_loss,
                                                       rpn_cls_loss=losses.rpn_cls_loss,
                                                       rpn_loc_loss=losses.rpn_loc_loss), global_step)
            
            if (ii + 1) % opt.plot_every == 0:
                if os.path.exists(opt.debug_file):
                    ipdb.set_trace()

                # plot loss
                # trainer.vis.plot_many(trainer.get_meter_data())

                # plot ground truth bboxes
                ori_img_ = inverse_normalize(at.tonumpy(img[0]))
                gt_img = visdom_bbox(ori_img_,
                                     at.tonumpy(bbox_[0]),
                                     at.tonumpy(label_[0]),
                                     label_names=dataset.get_class_names()+['BG'])
                writer.add_image('gt_img', gt_img, global_step)

                # plot predicti bboxes
                _bboxes, _labels, _scores = trainer.faster_rcnn.predict([ori_img_], visualize=True)
                pred_img = visdom_bbox(ori_img_,
                                       at.tonumpy(_bboxes[0]),
                                       at.tonumpy(_labels[0]).reshape(-1),
                                       at.tonumpy(_scores[0]),
                                       label_names=dataset.get_class_names()+['BG'])
                writer.add_image('pred_img', pred_img, global_step)

                # rpn confusion matrix(meter)
                # trainer.vis.text(str(trainer.rpn_cm.value().tolist()), win='rpn_cm')
                # roi confusion matrix
                # trainer.vis.img('roi_cm', at.totensor(trainer.roi_cm.conf, False).float())
                
            if (global_step) % opt.snapshot_every == 0:
                snapshot_path = trainer.save(epoch=epoch, class_names=testset.get_class_names())
                print_log("Snapshotted to {}".format(snapshot_path))

        #snapshot_path = trainer.save(epoch=epoch)
        #print("After epoch {}: snapshotted to {}".format(epoch,snapshot_path))
        
        for lo in losses:
            del lo
        del img, bbox_, label_, scale
        torch.cuda.empty_cache()
        eval_result = eval(test_dataloader, faster_rcnn, trainer, testset, global_step, test_num=min(opt.test_num, len(testset)))
        print_log(eval_result)
        # TODO: this definitely is not good and will bias evaluation
        if eval_result['map'] > best_map:
            best_map = eval_result['map']
            best_path = trainer.save(best_map=eval_result['map'],epoch=epoch, class_names=testset.get_class_names())
            print_log("After epoch {}: snapshotted to {}".format(epoch, best_path))

        del eval_result
        torch.cuda.empty_cache()

# ...def train(**kwargs)

def print_log(text):

    print(text)
    with open(log_summary_file, 'at') as summaryfile:
        summaryfile.write("{}: {}\n".format(datetime.datetime.now().strftime('%a %Y-%m-%d %H:%M:%S'),text))


if __name__ == '__main__':

    import fire
    fire.Fire()
