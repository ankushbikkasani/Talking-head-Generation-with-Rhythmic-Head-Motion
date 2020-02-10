# Copyright (c) 2019, NVIDIA Corporation. All rights reserved.
#
# This work is made available
# under the Nvidia Source Code License (1-way Commercial).
# To view a copy of this license, visit
# https://nvlabs.github.io/few-shot-vid2vid/License.txt
import torch

############################# input processing ###################################
def encode_input(opt, data_list, dummy_bs):
    if opt.isTrain and data_list[0].get_device() == 0:
        data_list = remove_dummy_from_tensor(opt, data_list, dummy_bs)
    tgt_label, tgt_image, flow_gt, conf_gt, ref_label, ref_image, prev_label, prev_image = data_list

    # target label and image
    tgt_label = encode_label(opt, tgt_label)
    tgt_image = tgt_image.cuda()            
             
    # reference label and image
    ref_label = encode_label(opt, ref_label)        
    ref_image = ref_image.cuda()
        
    return tgt_label, tgt_image, flow_gt, conf_gt, ref_label, ref_image, prev_label, prev_image

def encode_label(opt, label_map):
    size = label_map.size()
    if len(size) == 5:
        bs, t, c, h, w = size
        label_map = label_map.view(-1, c, h, w)
    else:
        bs, c, h, w = size        

    label_nc = opt.label_nc
    if label_nc == 0:
        input_label = label_map.cuda()
    else:
        # create one-hot vector for label map                         
        label_map = label_map.cuda()
        oneHot_size = (label_map.shape[0], label_nc, h, w)
        input_label = torch.cuda.FloatTensor(torch.Size(oneHot_size)).zero_()
        input_label = input_label.scatter_(1, label_map.long().cuda(), 1.0)
    
    if len(size) == 5:
        return input_label.view(bs, t, -1, h, w)
    return input_label

def remove_dummy_from_tensor(opt, tensors, remove_size=0):    
    if remove_size == 0: return tensors
    if tensors is None: return None
    if isinstance(tensors, list):
        return [remove_dummy_from_tensor(opt, tensor, remove_size) for tensor in tensors]    
    if isinstance(tensors, torch.Tensor):
        tensors = tensors[remove_size:]
    return tensors