import os
import urllib
import traceback
import time
import sys
import numpy as np
import cv2
from rknn.api import RKNN


def show_outputs(outputs):
    output = outputs[0][0]
    output_sorted = sorted(output, reverse=True)
    top5_str = 'resnet50v2\n-----TOP 5-----\n'
    for i in range(5):
        value = output_sorted[i]
        index = np.where(output == value)
        for j in range(len(index)):
            if (i + j) >= 5:
                break
            if value > 0:
                topi = '{}: {}\n'.format(index[j], value)
            else:
                topi = '-1: 0.0\n'
            top5_str += topi
    print(top5_str)


def readable_speed(speed):
    speed_bytes = float(speed)
    speed_kbytes = speed_bytes / 1024
    if speed_kbytes > 1024:
        speed_mbytes = speed_kbytes / 1024
        if speed_mbytes > 1024:
            speed_gbytes = speed_mbytes / 1024
            return "{:.2f} GB/s".format(speed_gbytes)
        else:
            return "{:.2f} MB/s".format(speed_mbytes)
    else:
        return "{:.2f} KB/s".format(speed_kbytes)


def show_progress(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    speed_str = " Speed: {}".format(readable_speed(speed))
    recv_size = blocknum * blocksize

    f = sys.stdout
    progress = (recv_size / totalsize)
    progress_str = "{:.2f}%".format(progress * 100)
    n = round(progress * 50)
    s = ('#' * n).ljust(50, '-')
    f.write(progress_str.ljust(8, ' ') + '[' + s + ']' + speed_str)
    f.flush()
    f.write('\r\n')


if __name__ == '__main__':
    # ONNX_MODEL = 'yolov5m_416x416.onnx'
    # RKNN_MODEL = 'yolov5m_416x416.rknn'

    # Create RKNN object
    rknn = RKNN()
    # If resnet50v2 does not exist, download it.
    # Download address:
    # https://s3.amazonaws.com/onnx-model-zoo/resnet/resnet50v2/resnet50v2.onnx
    # pre-process config
    print('--> config model')
    # rknn.config(mean_values=[[123.675, 116.28, 103.53]], std_values=[[58.82, 58.82, 58.82]], reorder_channel='0 1 2')
    # rknn.config(batch_size=1,target_platform=["rk1806", "rk1808", "rk3399pro"], mean_values='0 0 0 255')
    rknn.config(channel_mean_value='0 0 0 255', reorder_channel='0 1 2', batch_size=1)
    # rknn.config(channel_mean_value='0 0 0 1', reorder_channel='0 1 2', batch_size=1)
    # rknn.config(mean_values=[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], std_values=[[255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0, 255.0]], reorder_channel='0 1 2', batch_size=1)
    print('done')
 
    # Load tensorflow model
    print('--> Loading model')
    ret = rknn.load_onnx(model=ONNX_MODEL)
    if ret != 0:
        print('Load resnet50v2 failed!')
        exit(ret)
    print('done')

    # Build model
    print('--> Building model')
    ret = rknn.build(do_quantization=True, dataset='./dataset.txt')  # pre_compile=True
    # ret = rknn.build(do_quantization=True)  # pre_compile=True
    if ret != 0:
        print('Build resnet50 failed!')
        exit(ret)
    print('done')

    # Export rknn model
    print('--> Export RKNN model')
    ret = rknn.export_rknn(RKNN_MODEL)
    if ret != 0:
        print('Export resnet50v2.rknn failed!')
        exit(ret)
    print('done')
    rknn.release()

