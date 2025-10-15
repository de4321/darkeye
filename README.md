
# DarkEye - 在暗黑界睁开一只眼
一个使用PySide6 GUI开发，sqlite数据存储的暗黑影片数据存储与分析软件。


# 开发方向
1.0 基础工具的完善，包括力导向图探索影片之间的关系
2.0 UGC，分布式同步数据
3.0 机器学习推荐算法

## 特性
- [x] 影片的手动添加，增删查改，部分爬虫
- [x] 女优的手动添加，增删查改，部分爬虫
- [x] 男优的手动添加，增删查改
- [x] 标签的手动添加，增删查改
- [x] 撸管记录的手动添加，增删查改
- [x] 做爱记录的手动添加，增删查改
- [x] 晨勃记录的手动添加，增删查改
- [x] 分析图表
- [ ] 科普知识
- [ ] 插件化网页跳转
- [ ] 插件化爬虫
- [ ] 绿色模式


# 快速开始
#使用下面创建虚拟环境
conda create -n avlite python=3.12
conda activate avlite

pip install -r requirements.txt

下载后请复制public基本数据包到resource/文件夹下面
## 运行
python main.py

# 打包发布
在powershell里，刚刚创建的conda 虚拟环境中，运行build-pyinstaller.ps1
打包后的结构，一个绿色的可移动的文件夹，运行main.exe就能运行


# 文档的构建
mkdocs serve
mkdocs build  构建的位置是在site