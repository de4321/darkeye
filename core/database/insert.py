
'''插入数据库的操作在这里'''
from sqlite3 import IntegrityError
from config import DATABASE,PRIVATE_DATABASE
import logging
from .connection import get_connection

def InsertNewActress(ch_name,jp_name)->bool:
    '''插入女优数据'''
    conn = get_connection(DATABASE,False)
    cursor = conn.cursor()
    success=False
    try:
        cursor.execute("INSERT INTO actress DEFAULT VALUES")
        new_id = cursor.lastrowid

        #添加中文日文名
        cursor.execute("INSERT INTO actress_name (actress_id,name_type,cn,jp) VALUES(?,?,?,?)",
                    (new_id,1,ch_name,jp_name))

        conn.commit()
        logging.info(f"新插入的 actress_id 是: {new_id}:日文名:{jp_name}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
        success= False
    finally:
        cursor.close()
        conn.close()
    return success
    
def InsertNewActor(cn_name,jp_name)->bool:
    '''插入男优数据'''
    conn = get_connection(DATABASE,False)
    cursor = conn.cursor()
    success=False
    try:
        #添加中文日文名
        cursor.execute("INSERT INTO actor DEFAULT VALUES")
        new_id = cursor.lastrowid

        #添加中文日文名
        cursor.execute("INSERT INTO actor_name (actor_id,name_type,cn,jp) VALUES(?,?,?,?)",
                    (new_id,1,cn_name,jp_name))
        conn.commit()
        
        logging.info(f"新插入的 actor_id 是: {new_id}:日文名:{jp_name}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
        success= False
    finally:
        cursor.close()
        conn.close()
    return success

def InsertNewWork(serial_number:str)->int:
    conn = get_connection(DATABASE,False)
    cursor = conn.cursor()
    success=False
    try:
        #添加新作品
        cursor.execute("INSERT INTO work (serial_number) VALUES(?)",(serial_number,))
        new_id = cursor.lastrowid

        conn.commit()
        logging.info(f"新插入的 work_id 是: {new_id}")
        success=new_id
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
        return None
    finally:
        cursor.close()
        conn.close()

    return success

def InsertNewWorkByHand(serial_number,director,release_date,story,actress_ids,actor_ids,cn_title,cn_story,jp_title,jp_story,image_url,tag_ids)->bool:
    success=False
    try:
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        #添加新作品
        cursor.execute("INSERT INTO work (serial_number,director,story,release_date,cn_title,cn_story,jp_title,jp_story,image_url) VALUES(?,?,?,?,?,?,?,?,?)",(serial_number,director,story,release_date,cn_title,cn_story,jp_title,jp_story,image_url))
        new_id = cursor.lastrowid
        for id in actress_ids:
            cursor.execute("INSERT INTO work_actress_relation (work_id,actress_id) VALUES(?,?)",(new_id,id))
        for id in actor_ids:
            cursor.execute("INSERT INTO work_actor_relation (work_id,actor_id) VALUES(?,?)",(new_id,id))
        for id in tag_ids:
            cursor.execute("INSERT INTO work_tag_relation (work_id,tag_id) VALUES(?,?)",(new_id,id))            
        conn.commit()
        logging.info(f"新插入的 work_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        cursor.close()
        conn.close()
    return success

def insert_tag(tag_name:str,tag_type_id:int,tag_color:str,tag_detail:str,tag_redirect_tag_id:int,tag_alias:list[dict])->tuple[bool, str]:
    success=False
    try:
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tag (tag_name,tag_type_id,color,detail,redirect_tag_id) VALUES(?,?,?,?,?)",(tag_name,tag_type_id,tag_color,tag_detail,tag_redirect_tag_id))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 tag_id 是: {new_id}")
        return True, "插入成功"
    
    except IntegrityError as e:
        if "UNIQUE constraint failed: tag.tag_name" in str(e):
            print(f"错误：标签名称 '{tag_name}' 已存在")
            # 标签已存在
            message=f"标签名称 '{tag_name}' 已存在"
        else:
            print(f"其他完整性错误: {e}")
        conn.rollback()
        return False,message
    
    except Exception as e:
        conn.rollback()
        logging.warning(f"插入失败:{e}")
        return False, str(e) # 将错误信息转换为字符串返回
    finally:
        cursor.close()
        conn.close()

    return success

def add_tag2work(work_id:int,tag_ids:list[int])->bool:
    '''给作品添加标签,只添加没有的'''
    success=False
    try:
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        cursor.execute("SELECT tag_id FROM work_tag_relation WHERE work_id = ?", (work_id,))
        existing_tags = {row[0] for row in cursor.fetchall()}
        new_tags = set(tag_ids)
        # 2. 计算需要需要添加的标签
        tags_to_add = new_tags - existing_tags
        print(f"要添加的新标签{tags_to_add}")
        # 4. 执行添加（只添加新的）
        if tags_to_add:
            cursor.executemany(
                "INSERT INTO work_tag_relation (work_id, tag_id) VALUES (?, ?)",
                [(work_id, tag_id) for tag_id in tags_to_add]
            )
        conn.commit()
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning(f"插入失败:{e}")
    finally:
        cursor.close()
        conn.close()
    return success

def rename_save_image(_path:str,name:str,type:str):
    '''更改名字保存封面图片到库中，并且将相对地址写入数据库
    _path:一个图片的绝对地址
    name:图片要更改的名字'''
    from pathlib import Path
    from config import WORKCOVER_PATH,ACTRESSIMAGES_PATH,ACTORIMAGES_PATH
    from utils.utils import delete_image
    import shutil
    if type=="cover":
        dst_path:Path = Path(WORKCOVER_PATH) / name
    elif type=="actress":
        dst_path:Path = Path(ACTRESSIMAGES_PATH) / name
    elif type=="actor":
        dst_path:Path = Path(ACTORIMAGES_PATH) / name
    else:
        logging.info("选择保存的类型错误")

    # 检查源路径是否存在
    if not _path:
        return
    src_path = Path(_path)
    
    # 当源路径和目标路径相同时不操作
    if src_path.resolve() == dst_path.resolve():
        return
    
    shutil.copy(src_path, dst_path)
    logging.info("图片复制成功，已保存位置为：%s",dst_path)

    #删除临时地址的文件
    delete_image(_path)
#----------------------------------------------------------------------------------------------------------
#                                      私有数据库的插入数据
#----------------------------------------------------------------------------------------------------------

def insert_masturbation_record(work_id,serial_number,start_time,rating,tool_name,comment)->bool:
    """
    向自慰记录表 masturbation 插入一条新的记录。

    参数:
    - work_id: 关联作品的ID（整数）
    - start_time: 起飞时间，文本格式（如“YYYY-MM-DD HH:MM”）
    - rating: 满意度评分，整数，范围1-5
    - tool_name: 使用的工具名称（如“手”，“飞机杯”等）
    - comment: 对此次记录的备注或评论（文本）

    返回:
    - bool: 插入是否成功，True表示成功，False表示失败
    """
    success=False
    try:
        conn = get_connection(PRIVATE_DATABASE,False)
        cursor = conn.cursor()
        
        #添加的自慰记录
        cursor.execute("INSERT INTO masturbation (work_id,serial_number,start_time,tool_name,rating,comment) VALUES(?,?,?,?,?,?)",(work_id,serial_number,start_time,tool_name,rating,comment))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 masturbate_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        cursor.close()
        conn.close()

    return success

def insert_lovemaking_record(event_time, rating, comment) -> bool:
    """
    向做爱记录表 lovemaking 插入一条新的记录。

    参数:
    - event_time: 做爱事件的时间，文本格式（如“YYYY-MM-DD HH:MM”）
    - rating: 满意度评分，整数，范围1-5
    - comment: 对此次做爱的备注或评价（文本）

    返回:
    - bool: 插入是否成功，True表示成功，False表示失败
    """
    success=False
    try:
        conn = get_connection(PRIVATE_DATABASE,False)
        cursor = conn.cursor()
        
        #添加的自慰记录
        cursor.execute("INSERT INTO love_making (event_time,rating,comment) VALUES(?,?,?)",(event_time,rating,comment))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 love_making_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        cursor.close()
        conn.close()

    return success

def insert_sexual_arousal_record(arousal_time, comment) -> bool:
    """
    向晨勃记录表 sexual_arousal 插入一条新的记录。

    参数:
    - arousal_time: 晨勃时间，文本格式（如“YYYY-MM-DD HH:MM”）
    - comment: 对此次晨勃的备注或梦境描述（文本）

    返回:
    - bool: 插入是否成功，True表示成功，False表示失败
    """
    success=False
    try:
        conn = get_connection(PRIVATE_DATABASE,False)
        cursor = conn.cursor()
        
        #添加的自慰记录
        cursor.execute("INSERT INTO sexual_arousal (arousal_time,comment) VALUES(?,?)",(arousal_time,comment))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 sexual_arousal_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        cursor.close()
        conn.close()

    return success

def insert_liked_actress(actress_id)->bool:
    '''向私库中添加喜欢的女优'''
    from .db_utils import attach_private_db,detach_private_db
    success=False
    try:
        #先查询后添加
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        query="""
SELECT 
(SELECT jp FROM actress_name WHERE actress_id=actress.actress_id AND redirect_actress_name_id is NULL)AS jp_name
FROM actress 
WHERE actress_id=?
"""
        cursor.execute(query,(actress_id,))
        jp_name=cursor.fetchone()[0]

        attach_private_db(cursor)

        cursor.execute("INSERT INTO priv.favorite_actress (actress_id,jp_name) VALUES(?,?)",(actress_id,jp_name))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 favorite_actress_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        detach_private_db(cursor)
        cursor.close()
        conn.close()

    return success

def insert_liked_work(work_id)->bool:
    '''向私库中添加喜欢的女优'''
    from .db_utils import attach_private_db,detach_private_db
    success=False
    try:
        #先查询后添加
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        query="""
SELECT 
serial_number
FROM work 
WHERE work_id=?
"""
        cursor.execute(query,(work_id,))
        serial_number=cursor.fetchone()[0]

        attach_private_db(cursor)

        cursor.execute("INSERT INTO priv.favorite_work (work_id,serial_number) VALUES(?,?)",(work_id,serial_number))
        new_id = cursor.lastrowid
        conn.commit()
        logging.info(f"新插入的 favorite_work_id 是: {new_id}")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
    finally:
        detach_private_db(cursor)
        cursor.close()
        conn.close()

    return success

def InsertAliasName(id,alias_chain:list[dict])->bool:
    '''插入女优别名链'''
    conn = get_connection(DATABASE,False)
    cursor = conn.cursor()
    success=False
    try:
        cursor.execute("SELECT actress_name_id FROM actress_name WHERE actress_id=?",(id,))
        cur_id=cursor.fetchone()[0]
        
        for alias in reversed(alias_chain):
            print(alias)
            #添加中文日文名
            cursor.execute("INSERT INTO actress_name (actress_id,jp,kana,en,redirect_actress_name_id) VALUES(?,?,?,?,?)",
                        (id,alias['jp'],alias['kana'],alias['en'],cur_id))
            cur_id = cursor.lastrowid

        conn.commit()
        logging.info(f"")
        success=True
    except Exception as e:
        conn.rollback()
        logging.warning("插入失败:",e)
        success= False
    finally:
        cursor.close()
        conn.close()
    return success

