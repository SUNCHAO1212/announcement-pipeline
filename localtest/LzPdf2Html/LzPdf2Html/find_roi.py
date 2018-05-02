# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from collections import defaultdict

import cv2


# def contourArea(cnt):
#     rect = cv2.boundingRect(cnt)
#     return rect[2] * rect[3]

def contourArea(boundRect):
    return boundRect[2] * boundRect[3]


def find_roi(joints, boundRect):
    x = boundRect[0]
    y = boundRect[1]
    x_w = boundRect[0] + boundRect[2]
    y_h = boundRect[1] + boundRect[3]
    return joints[y:y_h, x:x_w].copy()


def extrTablePosition(imgpath):
    src = cv2.imread(imgpath)  # 读取图片

    h = src.shape[0]
    w = src.shape[1]

    scale = 50

    if h < scale or w < scale:
        return None, h, w

    src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)  # 转换了灰度化
    src_thresh = cv2.adaptiveThreshold(~src_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 0)  # 二值化

    # 垂直分析
    vertical = src_thresh.copy()

    verticalsize = int(vertical.shape[0] / scale)

    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))

    vertical = cv2.erode(vertical, verticalStructure)
    vertical = cv2.dilate(vertical, verticalStructure)

    # 水平分析
    horizontal = src_thresh.copy()
    horizontalsize = int(horizontal.shape[1] / scale)

    # 为了获取横向的表格线，设置腐蚀和膨胀的操作区域为一个比较大的横向直条
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    horizontal = cv2.erode(horizontal, horizontalStructure)
    horizontal = cv2.dilate(horizontal, horizontalStructure)

    joints = cv2.bitwise_and(horizontal, vertical)

    mask = horizontal + vertical

    _, cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cnts_size = len(cnts)

    # rois = []
    boundRects = defaultdict(set)
    for i in range(cnts_size):
        # print(cv2.boundingRect(cnts[i]))
        # if contourArea(cnts[i]) < 2000:
        #     print('area not match')
        #     continue

        contours_poly = cv2.approxPolyDP(cnts[i], 5, True)

        boundRect = cv2.boundingRect(contours_poly)

        roi = find_roi(joints, boundRect)

        _, joints_contours, _ = cv2.findContours(roi, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        if len(joints_contours) < 4:
            continue

        boundRects[contourArea(boundRect)].add(
            (boundRect[0], boundRect[1], boundRect[0] + boundRect[2], boundRect[1] + boundRect[3]))

        # 将矩形画在原图上

        # new_src = cv2.rectangle(src, (boundRect[0], boundRect[1]),
        #                         (boundRect[0] + boundRect[2], boundRect[1] + boundRect[3]),
        #                         (0, 255, 0), 1)
        # cv2.imshow('new_src', new_src)
        #
        # cv2.waitKey(0)
    cv2.destroyAllWindows()

    return sorted(boundRects.items(), key=lambda x: x[0], reverse=True), h, w


def combine(boundRects):
    newBoundRects = []
    for boundrect in boundRects[0][1]:
        newBoundRects.append(boundrect)

    boundRectsSize = len(boundRects)
    for i in range(1, boundRectsSize):
        for boundrect in boundRects[i][1]:
            isNewRect = True
            for newBoundrect in newBoundRects:
                if boundrect[0] >= newBoundrect[0] and boundrect[1] >= newBoundrect[1] and boundrect[2] <= newBoundrect[
                    2] and boundrect[3] <= newBoundrect[3]:
                    isNewRect = False
                    break

            if isNewRect:
                newBoundRects.append(boundrect)

    return newBoundRects


def get_roi(imgpath):
    boundRects, h, w = extrTablePosition(imgpath)

    if boundRects:
        return combine(boundRects)
    else:
        return None


if __name__ == '__main__':
    boundRects, h, w = extrTablePosition('/myJob/liangzhi/2018/LzMyTools/ParsePDF/myResultHtml/1204455645/bg5.png')
    print(len(boundRects), boundRects)
    newBoundRects = combine(boundRects)
    print(len(newBoundRects), newBoundRects)
