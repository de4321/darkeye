from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Work:
    """作品模型类
    Attributes:
        work_id: 作品ID，主键
        serial_number: 番号，唯一标识
        director: 导演
        story: 自定义剧情
        release_date: 发布日期
        image_url: 图片地址
        video_url: 视频地址
        cn_title: 中文标题
        jp_title: 日文标题
        cn_story: 中文剧情
        jp_story: 日文剧情
        create_time: 创建时间
        update_time: 更新时间
        is_deleted: 是否删除（软删除）
        javtxt_id: JavTxt ID
        fcover_url: 前置封面URL
        on_dan: 是否在弹幕网站
    """
    # 必填字段
    serial_number: str
    
    # 可选字段
    work_id: Optional[int] = None
    director: Optional[str] = None
    story: Optional[str] = None
    release_date: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    cn_title: Optional[str] = None
    jp_title: Optional[str] = None
    cn_story: Optional[str] = None
    jp_story: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    is_deleted: int = 0
    javtxt_id: Optional[int] = None
    fcover_url: Optional[str] = None
    on_dan: Optional[int] = None

    def __post_init__(self):
        """初始化后处理"""
        # 如果没有提供创建和更新时间，使用当前时间
        if not self.create_time:
            self.create_time = datetime.now()
        if not self.update_time:
            self.update_time = datetime.now()

    @property
    def is_active(self) -> bool:
        """是否未被删除"""
        return self.is_deleted == 0

    def delete(self):
        """标记为删除"""
        self.is_deleted = 1
        self.update_time = datetime.now()

    def update(self, **kwargs):
        """更新属性
        
        Args:
            **kwargs: 要更新的属性及其值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.update_time = datetime.now()

    def to_dict(self) -> dict:
        """转换为字典形式"""
        return {
            'work_id': self.work_id,
            'serial_number': self.serial_number,
            'director': self.director,
            'story': self.story,
            'release_date': self.release_date,
            'image_url': self.image_url,
            'video_url': self.video_url,
            'cn_title': self.cn_title,
            'jp_title': self.jp_title,
            'cn_story': self.cn_story,
            'jp_story': self.jp_story,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'update_time': self.update_time.isoformat() if self.update_time else None,
            'is_deleted': self.is_deleted,
            'javtxt_id': self.javtxt_id,
            'fcover_url': self.fcover_url,
            'on_dan': self.on_dan
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Work':
        """从字典创建实例
        
        Args:
            data: 字典数据
            
        Returns:
            Work: 作品实例
        """
        # 处理时间字段
        if 'create_time' in data and data['create_time']:
            data['create_time'] = datetime.fromisoformat(data['create_time'])
        if 'update_time' in data and data['update_time']:
            data['update_time'] = datetime.fromisoformat(data['update_time'])
        
        return cls(**data)

    def __str__(self) -> str:
        """字符串表示"""
        return f"Work({self.serial_number}: {self.cn_title or self.jp_title})"