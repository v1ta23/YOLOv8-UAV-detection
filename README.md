# 基于YOLOv8s的无人机检测识别系统
## 简介：
比较简单的无人机检测（UAV Detection）项目，模型为YOLOv8s。

本项目使用pyqt5完成了一个可视化系统。

内置用户登录功能，可加载视频和图片进行无人机检测识别。

UI类似Apple Google的白色极简风格。

（Vibe Coding产物）

后续随缘更新

##### 无人机数据集（UAV DATASETS）的链接：
https://www.kaggle.com/datasets/dasmehdixtr/drone-dataset-uav/（约1000张）

https://github.com/wangdongdut/DUT-Anti-UAV （10000张）

## 使用指南：
### 1. 环境准备
   
#### 1.1 操作系统
   
Windows，需适配 Python/CUDA 环境。

#### 1.2 Python 环境

Python3.10 或 3.11

python3 -m venv yolov8_env
source yolov8_env/bin/activate


**升级 pip**

pip install --upgrade pip

#### 1.3 依赖库安装（核心依赖）

项目核心依赖包括 PyTorch (带 CUDA)、Ultralytics YOLOv8、OpenCV、PyQt5 等，可参照如下：

pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install ultralytics
pip install opencv-python PyQt5

**注意：** Ultralytics YOLOv8 有时更新 API；建议使用官方稳定版本（pip install ultralytics==8.x.x）。

### 2. 获取与组织数据

该仓库未直接包含大规模训练数据，数据集请自行准备。

#### 2.1 数据集下载

Kaggle UAV Dataset

链接：
https://www.kaggle.com/datasets/dasmehdixtr/drone-dataset-uav/

**包含摄像头视角下的无人机目标图像标注。**

DUT Anti-UAV Dataset

**更大型、可增强精度。**

#### 2.2 数据整理

**数据文件结构：**

dataset/
├── images/

│   ├── train/

│   ├── val/

│   └── test/

└── labels/

    ├── train/
    
    ├── val/
    
    └── test/


**其中 .txt 标注格式如下：**

<class_id> <x_center> <y_center> <width> <height>


**创建一个 dataset.yaml：**

train: dataset/images/train
val:   dataset/images/val
test:  dataset/images/test

nc: 1
names: ['uav']

### 3. 模型训练

**模型训练推荐远程服务器训练（若显卡一般）**

YOLOv8 提供命令行与 Python API 两种训练方式。

#### 3.1 命令行训练

在项目根目录运行：

yolo task=detect mode=train \
     model=yolov8s.pt \
     data=dataset.yaml \
     epochs=50 \
     imgsz=640 \
     batch=16 \
     device=0


参数说明：

model: 初始模型权重（基础YOLOv8s）

data: 数据配置文件

epochs: 总训练轮数

imgsz: 图像像素尺寸

batch: 批量大小（显存较小时降低）

训练完成后，权重会自动保存到：

runs/detect/train/weights/best.pt

#### 3.2 Python API 训练（可调参）

创建脚本 train.py：

from ultralytics import YOLO

model = YOLO("yolov8s.pt")
model.train(data="dataset.yaml", epochs=50, imgsz=640, batch=16)


终端运行：

python train.py

### 4. 推理与可视化检测

训练完毕后，可使用命令行或 Python 进行推理：

#### 4.1 命令行推理
yolo task=detect mode=predict \
     model=runs/detect/train/weights/best.pt \
     source=dataset/images/test \
     save=True


推理输出保存在：

runs/detect/predict/

#### 4.2 Python 推理脚本
from ultralytics import YOLO
import cv2

model = YOLO("runs/detect/train/weights/best.pt")

img = cv2.imread("dataset/images/test/img001.jpg")
results = model(img)

results.show()

### 5. PyQt5 检测界面运行

项目代码中包含 Qt 相关文件（如 ui 目录）。



#### 5.1 运行界面程序

**系统运行:**

进入项目 UI 目录并执行

main_app.py

成功运行后可通过 GUI 加载模型和图片/视频进行实时检测。

