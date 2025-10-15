from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm
import logging
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
from matplotlib import rcParams
rcParams['font.family'] = 'SimHei'        # 设置全局字体为黑体
rcParams['axes.unicode_minus'] = False    # 解决负号显示为方块的问题
import numpy as np
from core.database.query import getActressByPlane,getActressBodyData


def weighted_percentile(data:list, weights:list, percentile:float):
    """计算加权分位数（纯 Python 实现）"""
    # 将 data 和 weights 按 data 排序
    combined = sorted(zip(data, weights), key=lambda x: x[0])
    data_sorted, weights_sorted = zip(*combined)

    # 计算累积权重
    cum_weights = []
    total = 0
    for w in weights_sorted:
        total += w
        cum_weights.append(total)

    total_weight = cum_weights[-1]
    target = percentile * total_weight

    # 插值查找分位值
    for i, cw in enumerate(cum_weights):
        if cw >= target:
            if i == 0:
                return data_sorted[0]
            prev_cw = cum_weights[i - 1]
            prev_data = data_sorted[i - 1]
            curr_data = data_sorted[i]
            # 线性插值
            frac = (target - prev_cw) / (cw - prev_cw)
            return prev_data + frac * (curr_data - prev_data)

    return data_sorted[-1]  # fallback：100%分位时返回最大值

def float_range(start, stop=None, step=1.0):
    if stop is None:
        stop = start
        start = 0.0
    if step == 0:
        raise ValueError("step must not be zero")
    
    result = []
    while (step > 0 and start < stop) or (step < 0 and start > stop):
        result.append(start)
        start += step
    return result

def gaussian_kde_manual(x_vals, weights, grid, bandwidth):
    kde_vals = np.zeros_like(grid)
    norm_factor = np.sum(weights) * (bandwidth * np.sqrt(2 * np.pi))

    for xi, wi in zip(x_vals, weights):
        kde_vals += wi * np.exp(-0.5 * ((grid - xi) / bandwidth) ** 2)

    return kde_vals / norm_factor


from enum import Enum
class Scope(Enum):
    PUBLIC=0
    PRIVATE=1
    MAS_COUNT=2
    MAS_WEIGHT=3

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4), dpi=100)
        #self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


    #绘制作品的拍摄年龄的分布，频率图
    def plotWorkActressAge(self, scope):
        from core.database.query import fetch_work_actress_avg_age
        tuple_list = fetch_work_actress_avg_age(scope)
        age = np.array([item[0] for item in tuple_list])
        weight = np.array([item[1] for item in tuple_list])

        low = weighted_percentile(age, weight, 0.05)
        high = weighted_percentile(age, weight, 0.95)
        mid = (low + high) / 2

        self.fig.clf()
        self.ax = self.fig.add_subplot(111)

        # 画直方图
        counts, bins, _ = self.ax.hist(age, bins=50, weights=weight, color='skyblue', edgecolor='#7D9CE8', density=True)

        # KDE 平滑频率曲线
        grid = np.linspace(min(age), max(age), 500)
        bandwidth = 1.0  # 控制平滑程度，值越大越平滑
        kde_vals = gaussian_kde_manual(age, weight, grid, bandwidth)
        self.ax.plot(grid, kde_vals, color='blue', linewidth=2, label='频率曲线 (KDE)')
        # 辅助线
        ymin, ymax = self.ax.get_ylim()
        self.ax.axvline(low, color='red', linestyle='--', label='5th percentile')
        self.ax.axvline(high, color='red', linestyle='--', label='95th percentile')
        self.ax.text(mid, ymax * 0.9, '90%区间', ha='center', fontsize=12, color='black', fontname='SimHei')

        # 标题设置
        match scope:
            case 0:
                self.ax.set_title("收藏作品女优平均拍摄年龄分布", fontname='SimHei')
                self.ax.set_xlabel("平均拍摄年龄（岁）", fontname='SimHei')
                self.ax.set_ylabel("频率", fontname='SimHei')
            case 1:
                self.ax.set_title("撸过作品女优平均拍摄年龄分布", fontname='SimHei')
                self.ax.set_xlabel("平均拍摄年龄（岁）", fontname='SimHei')
                self.ax.set_ylabel("频率", fontname='SimHei')
            case 2:
                self.ax.set_title("起飞次数加权影片中女优平均拍摄年龄分布", fontname='SimHei')
                self.ax.set_xlabel("拍摄年龄", fontname='SimHei')
                self.ax.set_ylabel("频率", fontname='SimHei')
            case -1:
                self.ax.set_title("公共库内女优平均拍摄年龄分布", fontname='SimHei')
                self.ax.set_xlabel("拍摄年龄", fontname='SimHei')
                self.ax.set_ylabel("频率", fontname='SimHei')
        self.ax.legend()
        self.draw()

    #画女优的3维的散点图，颜色代表罩杯
    def Draw3DsizeDis(self):
        #这个现在有问题后面再改
        bodyData=getActressBodyData()
        cup_colors = {
            'A': '#d0d1e6',  # 浅蓝灰
            'B': '#a6bddb',  # 淡蓝
            'C': '#74a9cf',  # 中淡蓝
            'D': '#3690c0',  # 中蓝
            'E': '#0570b0',  # 深蓝
            'F': '#045a8d',  # 深靛蓝
            'G': '#023858',  # 更深蓝
            'H': '#238b45',  # 绿调混入（大）
            'I': '#006d2c',  # 深绿（巨）
            'J': '#00441b'   # 极深绿黑（超巨）
        }

        # 2. 映射颜色列表（DataFrame中要先填充空值或剔除）
        colors = [
            cup_colors.get(item.get('cup'), '#999999')  # 找不到就默认灰色
            for item in bodyData
        ]
        xs = [item.get('bust') for item in bodyData]
        ys = [item.get('waist') for item in bodyData]
        zs = [item.get('hip') for item in bodyData]

        self.fig.clf()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.scatter(xs, ys, zs, c=colors, alpha=0.7)

        for cup, color in cup_colors.items():
            self.ax.scatter([], [], [], c=color, label=cup)

        self.ax.legend(title='cup')
        self.ax.set_xlabel("胸围",fontname='SimHei')
        self.ax.set_ylabel("腰围",fontname='SimHei')
        self.ax.set_zlabel("臀围",fontname='SimHei')
        

        self.ax.set_title("女优三围分布图",fontname='SimHei')
        self.draw()

    #绘制女优的罩杯分布
    def draw_cup_distribution_pie(self,scope):
        from core.database.query import fetch_actress_cup_distribution
        tuple_list=fetch_actress_cup_distribution(scope)
        # 数据准备
        labels = [item[0] for item in tuple_list]
        sizes = [item[1] for item in tuple_list]
        # 颜色映射（你可以用之前定义的 cup_colors，也可以自动配色）
        colors = cm.tab20.colors[:len(labels)]  # 选前几个颜色，够用就行
        max_index = max(range(len(sizes)), key=lambda i: sizes[i])
        explode = [0.1 if i == max_index else 0 for i in range(len(sizes))]

        # 清空图像
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)

        # 绘制饼图
        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            explode=explode,
            startangle=140,
            colors=colors,
            textprops={'fontsize': 10, 'fontname': 'SimHei'}
        )
        match scope:
            case 0:
                self.ax.set_title("收藏库女优罩杯分布(日本罩杯比国内大两个)", fontname='SimHei', fontsize=14)
            case 1:
                self.ax.set_title("撸过女优罩杯分布(日本罩杯比国内大两个)", fontname='SimHei', fontsize=14)
            case 2:
                self.ax.set_title("按撸管次数加权女优罩杯分布(日本罩杯比国内大两个)", fontname='SimHei', fontsize=14)
            case -1:
                self.ax.set_title("公共库女优罩杯分布(日本罩杯比国内大两个)", fontname='SimHei', fontsize=14)        

        self.ax.axis('equal')  # 保持饼图为圆形
        self.draw()  # 刷新 FigureCanvas

    #绘制女优的身高分布
    def draw_height_distribution(self,scope):
        from core.database.query import fetch_actress_height_with_weights
        tuple_list = fetch_actress_height_with_weights(scope)

        height = np.array([item[0] for item in tuple_list])
        weight = np.array([item[1] for item in tuple_list])

        min_val=min(height)
        max_val=max(height)

        bin = float_range(min_val-0.5, max_val+1.5, 1)

        low = weighted_percentile(height, weight, 0.05)
        high = weighted_percentile(height, weight, 0.95)
        mid = (low + high) / 2

        self.fig.clf()
        self.ax = self.fig.add_subplot(111)

        # 画直方图
        counts, bins, _ = self.ax.hist(height, bins=bin, weights=weight, color='skyblue', edgecolor='#7D9CE8', density=True)

        # KDE 平滑频率曲线
        grid = np.linspace(min(height), max(height), 500)
        bandwidth = 2.0  # 控制平滑程度，值越大越平滑
        kde_vals = gaussian_kde_manual(height, weight, grid, bandwidth)
        self.ax.plot(grid, kde_vals, color='blue', linewidth=2, label='频率曲线 (KDE)')
        # 辅助线
        ymin, ymax = self.ax.get_ylim()
        self.ax.axvline(low, color='red', linestyle='--', label='5th percentile')
        self.ax.axvline(high, color='red', linestyle='--', label='95th percentile')
        self.ax.text(mid, ymax * 0.9, '90%区间', ha='center', fontsize=12, color='black', fontname='SimHei')

        match scope:
            case 0:
                self.ax.set_title("收藏库内女优身高分布",fontname='SimHei')
                self.ax.set_xlabel("身高",fontname='SimHei')
                self.ax.set_ylabel("频率",fontname='SimHei')
            case 1:
                self.ax.set_title("撸过女优身高分布",fontname='SimHei')
                self.ax.set_xlabel("身高",fontname='SimHei')
                self.ax.set_ylabel("频率",fontname='SimHei')
            case 2:
                self.ax.set_title("起飞次数加权影片中女优身高分布",fontname='SimHei')
                self.ax.set_xlabel("身高",fontname='SimHei')
                self.ax.set_ylabel("频率",fontname='SimHei')
            case -1:
                self.ax.set_title("公共库中女优身高分布",fontname='SimHei')
                self.ax.set_xlabel("身高",fontname='SimHei')
                self.ax.set_ylabel("频率",fontname='SimHei')                
        self.ax.legend()
        self.draw()

    #绘制女优的腰臀比分布
    def draw_actressBodyWH_ratio(self,scope):
        from core.database.query import fetch_actress_waist_hip_stats
        tuple_list=fetch_actress_waist_hip_stats(scope)
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        waist=[item[0] for item in tuple_list]
        hip=[item[1] for item in tuple_list]
        weight=[item[2] for item in tuple_list]
        wh_ratio=[item[3] for item in tuple_list]
        # 统计每个腰围-臀围组合的频次

        # 重映射计算点大小（基于频次，范围10-100）
        min_count=min(weight)
        max_count =max(weight)
        base=max_count-min_count
        
        size =[140*y/base+10 for y in [x-min_count for x in weight]]#重映射到10-150
        scatter=self.ax.scatter(
        x=waist,
        y=hip,
        s=size,
        c=wh_ratio,  # 颜色映射腰臀比
        cmap='RdYlBu_r',
        alpha=1,
        )
        # 添加颜色条
        cbar = self.figure.colorbar(scatter, ax=self.ax)
        cbar.set_label('腰臀比', fontsize=10,fontname='SimHei')  # 设置颜色条标签

        self.ax.set_xlabel('腰围 (cm)', fontsize=12,fontname='SimHei')
        self.ax.set_ylabel('臀围 (cm)', fontsize=12,fontname='SimHei')
        match scope:
            case 0:
                self.ax.set_title('收藏库女优腰臀比（颜色=腰臀比，大小=人数）', fontsize=14,fontname='SimHei')
            case 1:
                self.ax.set_title('撸过女优腰臀比（颜色=腰臀比，大小=人数）', fontsize=14,fontname='SimHei')
            case 2:
                self.ax.set_title('撸过加权女优腰臀比（颜色=腰臀比，大小=人数）', fontsize=14,fontname='SimHei')
            case -1:
                self.ax.set_title('公共库女优腰臀比（颜色=腰臀比，大小=人数）', fontsize=14,fontname='SimHei')
        self.draw()

    #导演的拍片的数量
    def draw_directorBar(self,scope:int):
        from core.database.query import fetch_top_directors_by_scope
        tuple_list=fetch_top_directors_by_scope(scope)
                # 绘制横向柱状图
        director=[item[0] for item in tuple_list]
        num = [item[1] for item in tuple_list]
        director.reverse()
        num.reverse()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        bars = self.ax.barh(
            director,
            num,
            color='skyblue',
            edgecolor='black',
            height=0.6
        )
        for bar in bars:
            width = bar.get_width()
            self.ax.text(
                width + 0.1,  # x位置（柱右侧+0.5单位）
                bar.get_y() + bar.get_height()/2,  # y位置（柱中心）
                f'{int(width)}',  # 显示整数
                va='center',      # 垂直居中
                ha='left'         # 水平左对齐
            )
                # 装饰图形

                # === 关键修复部分 ===
        # 1. 先固定刻度位置（对应每个柱子的中心）
        y_positions = [bar.get_y() + bar.get_height()/2 for bar in bars]
        self.ax.set_yticks(y_positions)  # 固定刻度位置
        
        # 2. 再设置刻度标签（日语字体）
        self.ax.set_yticklabels(
            director,
            fontname='MS Gothic'  # 或其他日语字体
        )
        # ===================
        #self.ax.set_yticklabels(df['导演'], fontname='MS Gothic')  # 仅Y轴标签
        self.ax.set_xlabel('影片数量', fontsize=12,fontname='SimHei')
        self.ax.set_title('导演作品数量排名', fontsize=14,fontname='SimHei')
        #self.ax.grid(axis='x', linestyle='--', alpha=0.6,fontname='SimHei')
        self.fig.tight_layout()
        self.draw()

    #最喜欢的女优
    def draw_mostlikeActress(self):
        tuple_list=getActressByPlane()
        actress=[item[0] for item in tuple_list]
        num = [item[1] for item in tuple_list]
        actress.reverse()
        num.reverse()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        bars = self.ax.barh(
            actress,
            num,
            color='skyblue',
            edgecolor='black',
            height=0.6
        )
        for bar in bars:
            width = bar.get_width()
            self.ax.text(
                width + 0.1,  # x位置（柱右侧+0.5单位）
                bar.get_y() + bar.get_height()/2,  # y位置（柱中心）
                f'{int(width)}',  # 显示整数
                va='center',      # 垂直居中
                ha='left'         # 水平左对齐
            )
                # 装饰图形

                # === 关键修复部分 ===
        # 1. 先固定刻度位置（对应每个柱子的中心）
        y_positions = [bar.get_y() + bar.get_height()/2 for bar in bars]
        self.ax.set_yticks(y_positions)  # 固定刻度位置
        
        # 2. 再设置刻度标签（日语字体）
        self.ax.set_yticklabels(
            actress,
            fontname='SimHei'  # 或其他日语字体
        )
        # ===================
        #self.ax.set_yticklabels(df['导演'], fontname='MS Gothic')  # 仅Y轴标签
        self.ax.set_xlabel('撸管次数', fontsize=12,fontname='SimHei')
        self.ax.set_title('女优按撸管次数排名', fontsize=14,fontname='SimHei')
        #self.ax.grid(axis='x', linestyle='--', alpha=0.6,fontname='SimHei')
        self.fig.tight_layout()
        self.draw()

    #片商的统计数量
    def draw_studioBar(self,scope:int):
        from core.database.query import fetch_top_studios_by_scope
        tuple_list=fetch_top_studios_by_scope(scope)
        studio=[item[0] for item in tuple_list]
        num = [item[1] for item in tuple_list]
        studio.reverse()
        num.reverse()
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        bars = self.ax.barh(
            studio,
            num,
            color='skyblue',
            edgecolor='black',
            height=0.6
        )
        for bar in bars:
            width = bar.get_width()
            self.ax.text(
                width + 0.1,  # x位置（柱右侧+0.5单位）
                bar.get_y() + bar.get_height()/2,  # y位置（柱中心）
                f'{int(width)}',  # 显示整数
                va='center',      # 垂直居中
                ha='left'         # 水平左对齐
            )
                
                # 1. 先固定刻度位置（对应每个柱子的中心）
        y_positions = [bar.get_y() + bar.get_height()/2 for bar in bars]
        self.ax.set_yticks(y_positions)  # 固定刻度位置
        
        # 2. 再设置刻度标签（日语字体）
        self.ax.set_yticklabels(
            studio,
            fontname='SimHei'  # 或其他日语字体
        )        
        # 装饰图形
        self.ax.set_xlabel('数量', fontsize=12,fontname='SimHei')
        self.ax.set_title('片商数量排名', fontsize=14,fontname='SimHei')
        
        #self.ax.grid(axis='x', linestyle='--', alpha=0.6,fontname='SimHei')
        #self.fig.tight_layout()
        self.draw()