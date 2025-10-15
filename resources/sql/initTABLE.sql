--初始化数据库
--包含整体的数据库TABLE与部分TRIGGER
-------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS work (--公有作品表
    work_id INTEGER PRIMARY KEY AUTOINCREMENT,--不重复主键
    serial_number TEXT NOT NULL UNIQUE,--番号不能空不能重复
    director TEXT,                     --导演
    story TEXT,                        --这个主要是自己写的剧情
    release_date TEXT,                 --发布时间
    image_url TEXT,                    --图片地址
    video_url TEXT,                    --视频地址
	cn_title TEXT,                     --翻译标题
	jp_title TEXT,                     --官方标题
	cn_story TEXT,                     --翻译剧情
	jp_story TEXT,                     --官方剧情
	create_time TEXT DEFAULT (datetime('now', 'localtime')),
    update_time TEXT DEFAULT (datetime('now', 'localtime')),
	is_deleted INTEGER DEFAULT 0, 
	javtxt_id INTEGER
);

CREATE TRIGGER IF NOT EXISTS update_work_timestamp                                  --自动更新时间触发器
AFTER UPDATE ON work
FOR EACH ROW
BEGIN
    UPDATE work 
    SET update_time = DATETIME('now', 'localtime')
    WHERE work_id = OLD.work_id;
END;

CREATE TABLE IF NOT EXISTS actress(    				--女优表
	actress_id INTEGER PRIMARY KEY AUTOINCREMENT,
	birthday TEXT,                                    --出生日期
	height INTEGER,                                   --身高
	bust INTEGER,                                     --胸围
	waist INTEGER,                                    --腰围
	hip INTEGER,                                      --臀围
	cup TEXT,                                         --罩杯
	debut_date TEXT,                                  --出道日期
	need_update INTEGER DEFAULT 1,                    --是否需要爬虫更新数据,创建后默认需要更新 1代表需要更新 0代表不需要
	create_time TEXT DEFAULT (datetime('now', 'localtime')),
    update_time TEXT DEFAULT (datetime('now', 'localtime')), 
	image_urlA TEXT, 
	image_urlB TEXT, 
	minnano_url TEXT
);

CREATE TRIGGER IF NOT EXISTS update_actress_timestamp               --自动更新时间触发器
AFTER UPDATE ON actress
FOR EACH ROW
BEGIN
    UPDATE actress 
    SET update_time = DATETIME('now', 'localtime')
    WHERE actress_id = OLD.actress_id;
END;


CREATE TABLE IF NOT EXISTS actress_name(   --女优姓名表,解决女优多艺名问题
	actress_name_id INTEGER PRIMARY KEY AUTOINCREMENT,--不重复主键
	actress_id INTEGER,--女优id-这个是外键
	name_type INTEGER,--1主名，0代表非主名，最新的名字根据下面的链条算出来
	cn TEXT,
	jp TEXT,
	en TEXT,
	kana TEXT,
	redirect_actress_name_id INTEGER,--自引用外键，解决名字的链条问题，这个是NULL说明是最新的名字
	FOREIGN KEY(actress_id) REFERENCES actress(actress_id)
	FOREIGN KEY(redirect_actress_name_id) REFERENCES actress_name(actress_name_id)
);

CREATE TABLE IF NOT EXISTS work_actress_relation(  --作品女演员表，主要解决一个作品有多个女演员的问题，多对多
	work_actress_relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
	work_id INTEGER NOT NULL,
	actress_id INTEGER NOT NULL,
	job TEXT, --"职员""上司""老板"
	age TEXT, --"年轻"
	married TEXT, --"人妻" "女友"
	state TEXT,  --"主动"
	FOREIGN KEY(work_id) REFERENCES work(work_id),
	FOREIGN KEY(actress_id) REFERENCES actress(actress_id)
);



--------------------------------------------------------
CREATE TABLE IF NOT EXISTS manufacturer(--制作商，メーカー
	manufacturer_id INTEGER PRIMARY KEY AUTOINCREMENT,--不重复主键
	cn_name TEXT,										--中文名
	jp_name TEXT,										--日文名
	aliases TEXT,										--别名
	detail TEXT,                                       --其他信息
	logo_url TEXT										--logo地址
);

CREATE TABLE IF NOT EXISTS label(--厂牌，レーベル
	label_id INTEGER PRIMARY KEY AUTOINCREMENT,--不重复主键
	cn_name TEXT,										--中文名
	jp_name TEXT,										--日文名
	detail TEXT                                       --其他信息
);


CREATE TABLE IF NOT EXISTS tag (--标签表
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT, --主键
    tag_name TEXT UNIQUE NOT NULL,
    tag_type_id INTEGER, 
	color TEXT DEFAULT '#cccccc',  -- 存 hex 颜色码（推荐）
	redirect_tag_id INTEGER, -- 自引用外键，解决tag的重定向问题
	detail TEXT,  --详细说明
	group_id INTEGER,   --互斥组标记
	FOREIGN KEY (redirect_tag_id) REFERENCES tag(tag_id)
	FOREIGN KEY (tag_type_id)REFERENCES tag_type(tag_type_id)
);

CREATE TABLE IF NOT EXISTS work_tag_relation(--作品标签表 解决n对n的问题
	work_tag_id INTEGER PRIMARY KEY AUTOINCREMENT,--主键
	work_id INTEGER,--外键
	tag_id INTEGER,--外键
	FOREIGN KEY(work_id)REFERENCES work(work_id),
	FOREIGN KEY(tag_id)REFERENCES tag(tag_id),
	UNIQUE(work_id, tag_id) -- 防止插入重复对
);

----------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS actor(    				--男优表，主要是筛选男的帅不帅，有的实在是太丑了，又丑又胖,
	actor_id INTEGER PRIMARY KEY AUTOINCREMENT,			--自增id
	birthday   TEXT,                                    --出生年份-大致的
	height   INTEGER,                                   --身高
	handsome  INTEGER,		--0分丑，1分正常，2分帅
	fat       INTEGER,       --0分胖，1分正常，2分瘦
	need_update INTEGER DEFAULT 1,                    --男优数据没有地方去查，默认都没有，但是留着吧
	create_time TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS actor_name(   --男优姓名表,解决男优多艺名问题
	actor_name_id INTEGER PRIMARY KEY AUTOINCREMENT,--不重复主键
	actor_id INTEGER,--男id-这个是外键
	name_type INTEGER,--1主名，0代表非主名
	cn TEXT,
	jp TEXT,
	en TEXT,
	kana TEXT,
	FOREIGN KEY(actor_id) REFERENCES actor(actor_id)
);


-------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS work_actor_relation(  --作品男演员表，多对多，不要有其他数据，没有意义
	work_actor_relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
	work_id INTEGER NOT NULL,
	actor_id INTEGER NOT NULL,
	FOREIGN KEY(work_id) REFERENCES work(work_id),
	FOREIGN KEY(actor_id) REFERENCES actor(actor_id)
);

--公共知识表，这会随着时间更新，如果有更多的前缀
------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prefix_maker_relation(--番号前缀与片商的对应关系
	prefix_maker_relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
	prefix TEXT,--番号前缀
	maker_id INTEGER,
	FOREIGN KEY(maker_id)REFERENCES maker(maker_id)
)