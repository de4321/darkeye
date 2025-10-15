
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

# 项目整体的结构
AVmanagement_project/
├── main.py                  # 入口，启动 QApplication 和主窗口
├── config.py                # 配置与路径管理（兼容 PyInstaller）
├── settings.ini             # INI 配置文件,这个不跟踪，由程序生成
├── requirements.txt         # 运行环境的要求
├── README.md                # 基本的文档说明
├── main.spec                # pyinstaller打包配置文件
├── mkdocs.yml               # mkdocs文档的配置


├── controller/          #控制
│   ├── __init__.py
│   ├── GlobalSignalBus.py       #全局信号
│   └── MessageService.py        #信息框弹出

├── scripts/                   #使用脚本
│   ├── build-nuitka.ps1
│   ├── build-pyinstaller.ps1   # powershell，构建项目的命令行
│   ├── cloc_by_file.py
│   └── clocCode.ps1           # powershell，看项目有多少行代码的命令行

├── core/ 
│   ├── __init__.py
│   ├── chart/                  # 绘图
│   ├── crawler/                # 爬虫
│   ├── database/               # SQLite 操作封装
│   ├── recommendation/         # 推荐算法

├── ui/                      # UI 构造模块（可以手写或加载 .ui 文件）
│   ├── __init__.py
│   ├── main_window.py       # 主窗口逻辑
│   ├── widgets/      # 自定义控件
│   ├── statistics/   # 统计表控件
│   ├── pages/        #页面    
│   ├── basic/        #基本的控件    
│   ├── base/         #基础  


├── resources/            # 图片、图标、数据库等静态资源,是需要复制到打包后的文件夹里的
│   ├── icons/            #内部的图标
│   ├── public/
│   │   ├── actressimages/  #女演员头像
│   │   ├── actorimages/    #男演员头像
│   │   ├── workcovers/     #作品的封面
│   │   └── public.db        #公有数据库   
│   ├── private/            
│   │   └── private.db      #私有数据库
│   ├── config/
│   │   ├── sesitive_words.txt  #敏感词过滤表
│   │   ├── tag_map.json        #文字转换标签表
│   └── sql/              #sql语句

├── tests/                   # 单元测试

├── docs/                             # 文档
│   ├── api.md
│   ├── av.md
│   ├── AV数据库概念ERD.excalidraw
│   ├── bug.md
│   ├── data-collect.md
│   ├── db-design.md
│   ├── develop.md
│   ├── future.md
│   ├── index.md
│   ├── recommendation.md
│   ├── ui-design.md
│   ├── usage.md
│   └── 软件架构.excalidraw


# 快速开始
#使用下面创建虚拟环境
conda create -n avlite python=3.12
conda activate avlite

pip install -r requirements.txt

## 运行
python main.py

# 打包发布
在powershell里，刚刚创建的conda 虚拟环境中，运行build-pyinstaller.ps1
打包后的结构，一个绿色的可移动的文件夹，运行main.exe就能运行


# 文档的构建
mkdocs serve
mkdocs build  构建的位置是在site