from xml.dom import minidom
import os
import sys
import csv
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

USEED_LABEL = '1-60'
XML_FILE_DIR = './Hard_Sample_Test/Hard_sample/'
IMAGE_DIR = './Hard_Sample_Test/Hard_Picture/'
VISUAL_CORRECT_IAMGE_DIR = './Hard_Sample_Test/Hard_visual/'

CSV_FILE_PATH = './Hard_Sample_Test/Hard_sample.csv'
CSV_FILE_PATH_ADD_PREFIX_DIR = './Hard_Sample_Test/Prefix_Hard_sample.csv'
CLASS_LABEL = './class_label.csv'


def xml_to_data(xml_path):

    class_label_dict = {}
    # with open(CLASS_LABEL, encoding='utf-8') as class_csv:
    #     class_reader = csv.reader(class_csv)
    #     for x in class_reader:
    #         class_label_dict[x[0]] = x[1]
    data_list = []

    with open(xml_path, 'r') as fh:
        # parse()获取DOM对象
        dom = minidom.parse(fh)
        # 获取根节点
        root = dom.documentElement
        filename_node = root.getElementsByTagName('filename')[0]
        filename = filename_node.childNodes[0].data
        print(filename)
        for i, object in enumerate(root.getElementsByTagName('object')):
            name_node = object.getElementsByTagName('name')[0]
            class_name = name_node.childNodes[0].data

            if(USEED_LABEL == '1-60'):
                class_name = str(int(class_name) + 1)

            bnbbox = object.getElementsByTagName('bndbox')[0]

            xmin = bnbbox.getElementsByTagName('xmin')[0]
            x1 = xmin.childNodes[0].data
            ymin = bnbbox.getElementsByTagName('ymin')[0]
            y1 = ymin.childNodes[0].data
            xmax = bnbbox.getElementsByTagName('xmax')[0]
            x2 = xmax.childNodes[0].data
            ymax = bnbbox.getElementsByTagName('ymax')[0]
            y2 = ymax.childNodes[0].data

            if(int(x2) < int(x1)):
                x1, x2 = x2, x1
            if(int(y2) < int(y1)):
                y1, y2 = y2, y1

            data_list.append([filename, x1, y1, x2, y2, class_name])
        return data_list


def xml_transfer_data(xml_file_path):
    dirs = os.listdir(xml_file_path)
    data_list = []
    for dir in dirs:
        xml_path = os.path.join(xml_file_path, dir)

        data = xml_to_data(xml_path)
        if data != None:
            for x in data:
                data_list.append(x)

    return data_list


def data_write_csv(xml_file_path, data_csv_path):
    data_list = xml_transfer_data(xml_file_path)
    with open(data_csv_path, 'w', encoding = "utf-8", newline='') as f:
        csv_write = csv.writer(f)
        for data in data_list:
            csv_write.writerow(data)


def visual_data(class_label_csv, data_csv_path, visual_correct_image_dir):

    class_label_dict = {}
    with open(class_label_csv, encoding='utf-8') as class_csv:
        class_reader = csv.reader(class_csv)
        for x in class_reader:
            class_label_dict[x[1]] = x[0]

    with open(data_csv_path, encoding='utf-8') as data_csv_file:
        csv_reader = csv.reader(data_csv_file)
        for i, data in enumerate(csv_reader):
            img_name = data[0]
            img_path = os.path.join(IMAGE_DIR, img_name)
            image = cv2.imread(img_path)

            image_class = str(int(data[-1])-1)

            [x1, y1, x2, y2] = np.array(data[1:-1]).astype(int)

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # cv2和PIL中颜色的hex码的储存顺序不同
            pilimg = Image.fromarray(cv2img)

            # PIL图片上打印汉字
            draw = ImageDraw.Draw(pilimg)  # 图片上打印
            font = ImageFont.truetype("/home/lab716/msyh.ttf", 20, encoding="utf-8")  # 参数1：字体文件路径，参数2：字体大小
            draw.text((x1, y1), class_label_dict[image_class], (255, 0, 0), font=font)  # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体

            iamge = cv2.cvtColor(np.array(pilimg), cv2.COLOR_RGB2BGR)

            # cv2.putText(image, "{0}".format(class_label_dict[image_class]), (x1, y1),
            #          cv2.FONT_HERSHEY_SIMPLEX, 1, (245, 0, 0), 2)
            #cv2.imshow("{0}".format(1), iamge)

            cv2.imwrite(visual_correct_image_dir + '{0}.jpg'.format(i), iamge)
            # cv2.waitKey()


def add_base_dir():
    data_list = []
    base_dir = '/home/lab716/YuChen/BaiDu_V2/datasets/train/'
    with open(CSV_FILE_PATH, encoding='utf-8') as rdata_csv_file:
        csv_reader = csv.reader(rdata_csv_file)
        for data in csv_reader:
            data_list.append(data)
    print("Could add label number = {0}".format(len(data_list)))
    with open(CSV_FILE_PATH_ADD_PREFIX_DIR, 'w', encoding = "utf-8", newline='') as f:
        csv_write = csv.writer(f)
        for data in data_list:
            data[0] = os.path.join(base_dir, data[0])
            # print(data[0])
            csv_write.writerow(data)


if __name__ == '__main__':

    print("Loading...")
    data_write_csv(XML_FILE_DIR, CSV_FILE_PATH)
    print("Transfer finished")
    visual_data(CLASS_LABEL, CSV_FILE_PATH, VISUAL_CORRECT_IAMGE_DIR)
    print("The visual correct image dir is {0}, please check it".format(sys.path[0]+VISUAL_CORRECT_IAMGE_DIR) )

    add_base_dir()