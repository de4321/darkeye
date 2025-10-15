from PIL import Image
import numpy as np
from PySide6.QtGui import QImage, QPixmap,QColor
from PySide6.QtWidgets import QWidget
import re
import logging
import shutil
from pathlib import Path

#番号相关
def is_valid_serialnumber(code: str) -> bool:
    """
    检查番号是否符合格式：字母+可选数字 前缀，中间 "-"，后面为 1-5 位数字
    如：ABP-123、IPX-1024、SSNI-009、CAWD-999
    """
    pattern = r'^[A-Z]{2,6}-\d{1,5}$'
    return bool(re.match(pattern, code.upper()))

def covert_fanza(serial_number:str)->str:
    '''将传统的番号转化成fanza番号模式
    例如 IPX-247   ---->   ipx00247
    '''
    # 转换为小写
    lower_code = serial_number.lower()
    # 替换 - 为 00
    converted_code = lower_code.replace('-', '00')
    return converted_code

def serial_number_equal(A:str,B:str)->bool:
    """
    比较番号是否相等：
    - 全部小写
    - '-' 替换成 '00'
    """
    def normalize(s: str) -> str:
        return s.lower().replace('-', '00')

    return normalize(A) == normalize(B)

#图片相关
def AlternativeQPixmap(image_path):
    #临时的代替方法，什么时候QImage能直接加载jpg图片这个就不用了
    #mide537这个图片有问题，需要测试
    image = Image.open(image_path).convert("RGB")
    data = image.tobytes("raw", "RGB")
    qimage = QImage(data, image.width, image.height, QImage.Format_RGB888)
    return QPixmap.fromImage(qimage)

def mse(image1_path, image2_path):
    '''比较两张图片是否相似，输出0表示完全相同'''
    # 正确转换为numpy数组的方式
    img1 = np.array(Image.open(image1_path)).astype(float)  # 注意括号位置
    img2 = np.array(Image.open(image2_path)).astype(float)
    
    if img1.shape != img2.shape:
        #raise ValueError("图片尺寸不一致")
        logging.debug("图片尺寸不一致，直接判断不同")
        return 1
    err = np.sum((img1 - img2) ** 2)
    err /= float(img1.shape[0] * img1.shape[1])
    logging.debug("两张图片的相似错误率为:%s",err)
    return err

def delete_image(path):
    '''删除路径下的文件'''
    file_path = Path(path)
    if file_path.exists():
        file_path.unlink()  # 删除文件
        logging.info("图片%s已删除",file_path)


def conver2jpg(image_path):
    '''把图片转成jpg'''
    

def load_ini_ids(settings_config:str) -> list[int]:
    """从ini安全加载ID列表，处理以下情况：
    1. 键不存在 -> 返回空列表 []
    2. 值为 @Invalid() -> 返回空列表 []
    3. JSON解析失败 -> 返回空列表 []
    4. 值不是列表 -> 尝试转换或返回 []
    """
    from config import settings
    import json
    
    # 读取原始值（指定默认值为空列表的JSON字符串）
    raw_value = settings.value(settings_config, "[]")

    # 处理 @Invalid()
    if isinstance(raw_value, str) and raw_value == "@Invalid()":
        return []

    # 尝试JSON解析
    try:
        ids = json.loads(raw_value)
    except json.JSONDecodeError:
        return []

    # 校验数据类型
    if not isinstance(ids, list):
        return []

    # 过滤非整数项（可选）
    return [int(x) for x in ids if isinstance(x, (int, str)) and str(x).isdigit()]


def capture_full(widget:QWidget):
    '''动态区域截图'''
    #widget = scroll_area.widget()  # 获取 ScrollArea 的内容 widget
    size = widget.size()

    # 创建全尺寸 Pixmap
    pixmap = QPixmap(size)
    widget.render(pixmap)  # 渲染整个 widget

    # 弹出选择文件位置
    from PySide6.QtWidgets import QFileDialog
    file_path, _ = QFileDialog.getSaveFileName(
        widget,
        "保存截图",
        "screenshot.png",
        "PNG 图像 (*.png);;JPEG 图像 (*.jpg)"
    )

    if not file_path:
        return  # 用户取消
    
    # 保存
    pixmap.save(file_path)
    print("已保存 full_screenshot.png")




from googletrans import Translator
async def translate_text(text:str, dest="zh-CN"):
    translator = Translator()
    result = await translator.translate(text, dest=dest)  # 使用 await
    return result.text

def get_text_color_from_background(new_color: QColor)->str:
    """
    计算颜色的感知亮度（Perceived Luminance）,通过背景计算前面的文字是黑色还是白色
    """
    # 计算颜色的感知亮度（Perceived Luminance）
    # 这是一个常用的公式，能够更准确地判断颜色深浅
    luminance = (
        0.299 * new_color.red() + 
        0.587 * new_color.green() + 
        0.114 * new_color.blue()
    )
    # 根据亮度值决定文本颜色
    if luminance > 128:  # 亮度大于128（中灰色）则认为是浅色
        return "black"
    else:
        return "white"

def get_hover_color_from_background(new_color: QColor)->str:
    """
    计算颜色的感知亮度（Perceived Luminance）,通过背景计算前面的文字是黑色还是白色
    """
    # 计算颜色的感知亮度（Perceived Luminance）
    # 这是一个常用的公式，能够更准确地判断颜色深浅
    luminance = (
        0.299 * new_color.red() + 
        0.587 * new_color.green() + 
        0.114 * new_color.blue()
    )
    # 根据亮度值决定文本颜色
    if luminance > 128:  # 亮度大于128（中灰色）则认为是浅色
        return "#646464"
    else:
        return "#C5C5C5"


def invert_color(color: QColor) -> QColor:
    """
    返回给定 QColor 的反色
    """
    return QColor(255 - color.red(),
                  255 - color.green(),
                  255 - color.blue(),
                  color.alpha())

#计算相关
def get_rank(value, data, reverse=False):
    """
    计算 value 在 data 中的归一化位次 [0,1]
    reverse=False 表示越大越好
    reverse=True  表示越小越好
    """
    data_sorted = sorted(data)
    n = len(data_sorted)

    # 找到小于等于 value 的数量
    rank = sum(v <= value for v in data_sorted)

    # 转为 [0,1]
    if rank<=1:
        rank=1
    pos = (rank - 1) / (n - 1) if n > 1 else 0.0

    # 如果是反向指标（越小越好），取反
    if reverse:
        pos = 1 - pos

    return pos

import time
import functools
def timeit(func):
    """装饰器：打印函数执行耗时"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.debug(f"⏱ {func.__name__} 执行耗时: {end - start:.4f} 秒")
        return result
    return wrapper

#日期相关
def convert_date(date_str:str)->str:
    """
    使用datetime模块转换日期格式
    
    Args:
        date_str: 日期字符串，格式为xxxx-xx-xx
        
    Returns:
        转换后的日期字符串，格式为xxxx年xx月xx日
    """
    from datetime import datetime
    if date_str is None:
        return ""
    try:
        # 解析日期字符串
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # 格式化为目标格式
        return date_obj.strftime('%Y年%m月%d日')
    except ValueError:
        # 处理格式错误的情况
        return date_str


from PySide6.QtWidgets import QTableView, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
import csv
import os
def export_view_to_csv(tableView: QTableView, csv_file_path: str):
    """
    将 QTableView 的内容导出到 CSV 文件。
    
    Args:
        tableView (QTableView): 要导出的 QTableView 实例。
        csv_file_path (str): 导出文件的完整路径和文件名。
    """
    try:
        # 1. 获取模型
        model = tableView.model()
        if not model:
            QMessageBox.warning(tableView, "导出失败", "视图没有关联的模型。")
            return False

        # 2. 准备数据
        column_count = model.columnCount()
        row_count = model.rowCount()
        
        # 获取表头
        header_labels = [model.headerData(col, Qt.Horizontal) for col in range(column_count)]
        
        # 获取所有单元格数据
        data_rows = []
        for row in range(row_count):
            row_data = [model.data(model.index(row, col)) for col in range(column_count)]
            data_rows.append(row_data)

        # 3. 写入 CSV 文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 写入表头
            writer.writerow(header_labels)
            
            # 写入所有行数据
            writer.writerows(data_rows)
            
        QMessageBox.information(tableView, "导出成功", f"数据已成功导出到：\n{csv_file_path},用excel打开时请使用utf-8导入，否则会出现乱码")
        return True

    except Exception as e:
        QMessageBox.critical(tableView, "导出错误", f"导出失败，发生错误：\n{e}")
        return False

from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

def mosaic_qimage(img: QImage, pixel_size=20) -> QImage:
    """
    给 QImage 整体打马赛克
    :param img: 输入的 QImage
    :param pixel_size: 马赛克块大小
    :return: 处理后的 QImage
    """
    w, h = img.width(), img.height()

    # 缩小
    small = img.scaled(
        max(1, w // pixel_size),
        max(1, h // pixel_size),
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation
    )

    # 放大
    mosaic = small.scaled(
        w, h,
        Qt.IgnoreAspectRatio,
        Qt.FastTransformation
    )

    return mosaic

import re



def load_sensitive_words()->list[str]:
    from config import SENSITIVE_WORDS_PATH
    words = []
    with open(SENSITIVE_WORDS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word:  # 忽略空行
                words.append(word)
    return words

SENSITIVE_WORDS=load_sensitive_words()

def replace_sensitive(text: str, repl="**") -> str:
    """替换文本中的敏感词"""
    # 构造正则模式（忽略大小写）
    if not text:
        return text
    pattern = re.compile("|".join(map(re.escape, SENSITIVE_WORDS)), re.IGNORECASE)
    return pattern.sub(repl, text)


def sort_dict_list_by_keys(data: list[dict], key_order: list[str]) -> list[dict]:
    """
    将一个字典列表按照指定的键序重新排序。

    Args:
        data: 待排序的字典列表。
        key_order: 包含期望键序的字符串列表。

    Returns:
        一个新列表，其中每个字典的键都按照指定顺序排列。
    """
    ordered_data = []
    for d in data:
        # 使用字典推导式，按照 key_order 的顺序重新构建字典
        # .get(key, None) 用于处理字典中可能不存在的键，防止报错
        ordered_dict = {key: d.get(key) for key in key_order}
        ordered_data.append(ordered_dict)
    return ordered_data