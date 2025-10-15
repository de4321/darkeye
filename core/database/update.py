'''更新数据库的操作都在这里'''
import logging
from config import DATABASE
from .connection import get_connection
from sqlite3 import Cursor,IntegrityError
#----------------------------------------------------------------------------------------------------------
#                                               公共数据库的更新
#----------------------------------------------------------------------------------------------------------

def update_tag_type(tag_type_data:list[dict])->bool:
    '''更新tag_type'''
    #1.计算需要删除的部分然后删除
    #获得当前所有的tag_type_id的集合
    conn = get_connection(DATABASE,False)
    cursor = conn.cursor()
    cursor.execute("SELECT tag_type_id FROM tag_type")
    existing_tag_type = {row[0] for row in cursor.fetchall()}
    #比较现有的差距
    new_tag_type=set([data["tag_type_id"] for data in tag_type_data])
    delete_tag_type=existing_tag_type-new_tag_type
    logging.debug(f"要删除的tag_type_id{delete_tag_type}")

    try:
        for tag_type_id in delete_tag_type:
            cursor.execute("DELETE FROM tag_type WHERE tag_type_id=?",(tag_type_id,))
            #现在没有外键会导致失误删除

        #2.计算需要添加的部分然后添加
        #要添加的就是tag_type_id为空的
        order=1
        for data in tag_type_data:
            if not data.get("tag_type_id"):
                cursor.execute("INSERT INTO tag_type (tag_type_name,tag_order) VALUES(?,?)",(data["tag_type_name"],order))
                logging.debug(f"要添加的tag_type:{data["tag_type_name"]}")
            else:
                cursor.execute("UPDATE tag_type SET tag_type_name=?,tag_order=? Where tag_type_id=?",(data["tag_type_name"],order,data["tag_type_id"]))
            order+=1
        conn.commit()
        logging.debug("标签类型更新成功")
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"更新标签失败: {e}")
        return False
    finally:
        conn.close()

#需要外键检查的
def UpdateWorkTags(work_id, new_tag_ids)->bool:
    """更高效地更新作品标签关系（只删除不再需要的，只添加新的）"""
    try:
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        # 1. 获取现有的标签ID集合
        cursor.execute("SELECT tag_id FROM work_tag_relation WHERE work_id = ?", (work_id,))
        existing_tags = {row[0] for row in cursor.fetchall()}
        new_tags = set(new_tag_ids)
        
        # 2. 计算需要删除和需要添加的标签
        tags_to_remove = existing_tags - new_tags
        tags_to_add = new_tags - existing_tags
        
        # 3. 执行删除（只删除不再需要的）
        if tags_to_remove:
            placeholders = ','.join(['?'] * len(tags_to_remove))
            cursor.execute(
                f"DELETE FROM work_tag_relation WHERE work_id = ? AND tag_id IN ({placeholders})",
                (work_id, *tags_to_remove)
            )
        
        # 4. 执行添加（只添加新的）
        if tags_to_add:
            cursor.executemany(
                "INSERT INTO work_tag_relation (work_id, tag_id) VALUES (?, ?)",
                [(work_id, tag_id) for tag_id in tags_to_add]
            )
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"更新标签失败: {e}")
        return False
    finally:
        conn.close()

def _update_actor(cursor:Cursor,work_id:int,actor_ids:list):
    '''更新作品的男优关系，传入一个cursor'''
    # 3. 更新男优----------------------------------------------------------------------------
    cursor.execute("SELECT actor_id FROM work_actor_relation WHERE work_id = ?", (work_id,))
    existing_actor = {row[0] for row in cursor.fetchall()}
    new_actor = set(actor_ids)
    
    #  计算需要删除和需要添加的男优
    actor_to_remove = existing_actor - new_actor
    actor_to_add = new_actor - existing_actor
    
    #  执行删除（只删除不再需要的）
    if actor_to_remove:
        placeholders = ','.join(['?'] * len(actor_to_remove))
        cursor.execute(
            f"DELETE FROM work_actor_relation WHERE work_id = ? AND actor_id IN ({placeholders})",
            (work_id, *actor_to_remove)
        )
    
    #  执行添加（只添加新的）
    if actor_to_add:
        cursor.executemany(
            "INSERT INTO work_actor_relation (work_id, actor_id) VALUES (?, ?)",
            [(work_id, tag_id) for tag_id in actor_to_add]
        )

def _update_actress(cursor:Cursor,work_id:int,actress_ids:list):
    # 2. 更新女优,用try包裹---------------------------------------------------------------------------------
    cursor.execute("SELECT actress_id FROM work_actress_relation WHERE work_id = ?", (work_id,))
    existing_actress = {row[0] for row in cursor.fetchall()}
    new_actress = set(actress_ids)
    
    #  计算需要删除和需要添加的女优
    actress_to_remove = existing_actress - new_actress
    actress_to_add = new_actress - existing_actress
    
    #  执行删除（只删除不再需要的）
    if actress_to_remove:
        placeholders = ','.join(['?'] * len(actress_to_remove))
        cursor.execute(
            f"DELETE FROM work_actress_relation WHERE work_id = ? AND actress_id IN ({placeholders})",
            (work_id, *actress_to_remove)
        )
    
    #  执行添加（只添加新的）
    if actress_to_add:
        cursor.executemany(
            "INSERT INTO work_actress_relation (work_id, actress_id) VALUES (?, ?)",
            [(work_id, tag_id) for tag_id in actress_to_add]
        )

def _update_worktag(cursor:Cursor,work_id:int,tag_ids:list):
    # 1. 更新tag
    cursor.execute("SELECT tag_id FROM work_tag_relation WHERE work_id = ?", (work_id,))
    existing_tags = {row[0] for row in cursor.fetchall()}
    new_tags = set(tag_ids)
    # 2. 计算需要删除和需要添加的标签
    tags_to_remove = existing_tags - new_tags
    tags_to_add = new_tags - existing_tags
    # 3. 执行删除（只删除不再需要的）
    if tags_to_remove:
        placeholders = ','.join(['?'] * len(tags_to_remove))
        cursor.execute(
            f"DELETE FROM work_tag_relation WHERE work_id = ? AND tag_id IN ({placeholders})",
            (work_id, *tags_to_remove)
        )
    # 4. 执行添加（只添加新的）
    if tags_to_add:
        cursor.executemany(
            "INSERT INTO work_tag_relation (work_id, tag_id) VALUES (?, ?)",
            [(work_id, tag_id) for tag_id in tags_to_add]
        )

def update_work_byhand(work_id,director,release_date, story, actress_ids,actor_ids,cn_title, cn_story, jp_title, jp_story,image_url,tag_ids)->bool:
    '''更新作品的信息，默认番号是不会出错的'''
    try:
        conn = get_connection(DATABASE,False)
        cursor:Cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")#打开外键约束
        # 1. 更新基本的信息
        cursor.execute('''
                        UPDATE work
                        SET director=?,
                        release_date=?,
                        story=?,
                        cn_title=?,
                        cn_story=?,
                        jp_title=?,
                        jp_story=?,
                        image_url=?
                        WHERE work_id = ?
''',(director,release_date,story,cn_title,cn_story,jp_title,jp_story,image_url,work_id,))

        _update_actress(cursor,work_id,actress_ids)

        _update_actor(cursor,work_id,actor_ids)

        _update_worktag(cursor,work_id,tag_ids)

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"更新作品信息失败: {e}")
        return False
    finally:
        conn.close()

def update_work_byhand_(work_id: int, **fields) -> bool:
    """
    动态更新作品的信息，传入什么字段就更新什么字段,只能更新最基本的
    例如：
        update_work_byhand(1, director="A", cn_title="标题")
    """
    if not fields:
        return False  # 没有字段传入，不更新
    
    try:
        conn = get_connection(DATABASE, False)
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")  # 打开外键约束

        # 特殊处理 actress_ids
        if 'actress_ids' in fields:
            actress_ids = fields.pop('actress_ids')# 从 fields 中移除并获取值
            # 执行演员关联的更新逻辑
            _update_actress(cursor,work_id, actress_ids)

        if 'actor_ids' in fields:
            actor_ids = fields.pop('actor_ids')# 从 fields 中移除并获取值
            # 执行演员关联的更新逻辑
            _update_actor(cursor,work_id, actor_ids)
        
        if 'tag_ids' in fields:
            tag_ids = fields.pop('tag_ids')# 从 fields 中移除并获取值
            # 执行演员关联的更新逻辑
            _update_worktag(cursor,work_id, tag_ids)

        if not fields:
            conn.commit()
            return True  # 如果没有其他字段需要更新，直接提交并返回
        
        # 动态拼接 SET 子句
        set_clauses = []
        params = []
        for key, value in fields.items():
            set_clauses.append(f"{key}=?")
            params.append(value)

        sql = f"""
            UPDATE work
            SET {', '.join(set_clauses)}
            WHERE work_id=?
        """
        params.append(work_id)  # 最后加上 work_id

        cursor.execute(sql, params)
        conn.commit()
        return True

    except Exception as e:
        logging.warning(f"更新失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_work_actor(work_id:int,actor_ids:list)->bool:
    '''更新作品的信息，默认番号是不会出错的'''
    try:
        conn = get_connection(DATABASE,False)
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")#打开外键约束
        _update_actor(cursor,work_id,actor_ids)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"更新作品信息失败: {e}")
        return False
    finally:
        conn.close()


#不需要外键检查的

def check_workcover_integrity():
    '''检查数据库中图片地址与实际位置的完整性
    
    文件夹中多出来的图片给删除
    文件夹中如果少了，也就是数据库中的image_url找不到指定的文件，把库中的相对位置给删除成NULL
    '''
    return

def update_db_actress(id:int,data:dict):
    '''更新女优名字，身材信息数据，写入数据库的表中，一条一条写'''

    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info(f"准备更新:{data},{id}")
        cursor.execute(
            "UPDATE actress SET birthday= ?,height = ?, bust = ?, waist = ?, hip = ?, cup = ?,debut_date=?,need_update=0 WHERE actress_id = ?",
            (data['出生日期'],data['身高'],data['胸围'],data['腰围'],data['臀围'],data['罩杯'],data['出道日期'],id)
        )
        #更新英文名,假名

        cursor.execute("UPDATE actress_name SET en=?,kana=? WHERE actress_id=?",
                (data['英文名'],data['假名'],id))
        

        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_actress_image(id:int,image_url):
    '''更新女优头像地址写入数据库的表中，一条一条写'''

    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",image_url,id)
        cursor.execute(
            "UPDATE actress SET image_urlA=?,need_update=0 WHERE actress_id = ?",
            (image_url,id)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_actress_minnano_id(id,minnano_actress_id):
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",minnano_actress_id,id)
        cursor.execute(
            "UPDATE actress SET minnano_url=?,need_update=0 WHERE actress_id = ?",
            (minnano_actress_id,id)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_work_javtxt(id,javtxt_id):
    '''写入javtxt_id的缓存数据'''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",javtxt_id,id)
        cursor.execute(
            "UPDATE work SET javtxt_id=? WHERE work_id = ?",
            (javtxt_id,id)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_titlestory(serial_number,cn_title,jp_title,cn_story,jp_story):
    '''更新故事进去'''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s",serial_number)
        cursor.execute(
            "UPDATE work SET cn_title=?,jp_title=?,cn_story=?,jp_story==? WHERE serial_number = ?",
            (cn_title,jp_title,cn_story,jp_story,serial_number)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_tag_color(tag_ids:list,color):
    '''更新tag的color'''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()
    try:
        logging.info("准备更新:%s",tag_ids)
        cursor.executemany(
                "UPDATE tag SET color=? Where tag_id=?",
                [(color,tag_id) for tag_id in tag_ids]
            )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0

def update_fanza_cover_url(work_id:int,fcover_url:str):
    '''更新'''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",work_id,fcover_url)
        cursor.execute(
            "UPDATE work SET fcover_url=? WHERE work_id = ?",
            (fcover_url,work_id)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()
    return 0


def update_on_dan(work_id:int,on_dan:int):
    '''更新一部作品能否在avdan上找到0找不到，1 找到'''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",work_id,on_dan)
        cursor.execute(
            "UPDATE work SET on_dan=? WHERE work_id = ?",
            (on_dan,work_id)
        )
        conn.commit()
        logging.info("更新成功")
    except Exception as e:
        conn.rollback()
        logging.info("更新失败",e)
    finally:
        cursor.close()
        conn.close()

def update_tag(tag_id:int,tag_name:str,tag_type_id:int,tag_color:str,tag_detail:str,tag_redirect_tag_id:int,tag_alias:list[dict])->bool:
    '''
            "tag_id": self._tag_id,
            "tag_name":self._tag_name,
            "tag_type":self._tag_type,
            "tag_color":self._tag_color,
            "tag_detail":self._tag_detail,
            "tag_redirect_tag_id":self._tag_redirect_tag_id
    '''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()

    try:
        logging.info("准备更新:%s,%s",tag_id,tag_name)
        cursor.execute(
            "UPDATE tag SET tag_name=?,tag_type_id=?,color=?,detail=?,redirect_tag_id=? WHERE tag_id = ?",
            (tag_name,tag_type_id,tag_color,tag_detail,tag_redirect_tag_id,tag_id)
        )
        update_tag_alias(cursor,tag_alias,tag_id)
        conn.commit()
        logging.info("更新成功")
        return True
    except IntegrityError as e:
        if "UNIQUE constraint failed: tag.tag_name" in str(e):
            print(f"错误：标签名称 '{tag_name}' 已存在")
            # 标签已存在
        else:
            print(f"其他完整性错误: {e}")
        conn.rollback()
        return False
    except Exception as e:
        conn.rollback()
        logging.info(f"更新失败{e}")
        return False
    finally:
        cursor.close()
        conn.close()

def update_tag_alias(cursor:Cursor,tag_alias:list[dict],tag_id):
    '''更新tag_alias'''
    #先计算要删除的部分，然后计算添加的部分
    #先取原来的
    cursor.execute(f'''
SELECT 
	tag_id
FROM tag 
WHERE redirect_tag_id=?''', (tag_id,))
    existing_ids = {row[0] for row in cursor.fetchall()}
    existing_ids = set(existing_ids)
    logging.debug(existing_ids)
    new_ids = {name['tag_id'] for name in tag_alias if name['tag_id'] is not None}
    logging.debug(new_ids)
    delete_ids= existing_ids - new_ids
    logging.debug(delete_ids)
    # 3. 执行删除（只删除不再需要的）
    if delete_ids:
        placeholders = ','.join(['?'] * len(delete_ids))
        cursor.execute(
            f"DELETE FROM tag WHERE tag_id IN ({placeholders})",
            (*delete_ids,)
        )
    logging.debug("删除成功")
    #修改与添加
    for tag in tag_alias:
        if tag['tag_id'] is None or tag['tag_id']=="":#表明是新添加的
            cursor.execute(
                "INSERT INTO tag (tag_name,redirect_tag_id) VALUES (?,?)",
                (tag["tag_name"],tag_id)
            )
        else: #修改
            cursor.execute(
                "UPDATE tag SET tag_name=? WHERE tag_id=?",(tag["tag_name"],tag["tag_id"])
            )

def mark_delete(work_id)->bool:
    '''将作品标记为未删除
    '''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()
    try:
        #logging.info("准备更新:%s,%s",work_id)
        cursor.execute(
            "UPDATE work SET is_deleted=1 WHERE work_id = ?",
            (work_id,)
        )
        conn.commit()
        logging.info("标记作品为删除状态")
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"标记作品为删除状态失败{e}")
        return False
    finally:
        cursor.close()
        conn.close()

def mark_undelete(work_id)->bool:
    '''将作品标记为未删除
    '''
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()
    try:
        #logging.info("准备更新:%s,%s",work_id)
        cursor.execute(
            "UPDATE work SET is_deleted=0 WHERE work_id = ?",
            (work_id,)
        )
        conn.commit()
        logging.info("标记作品为未删除状态")
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"标记作品为未删除状态失败{e}",)
        return False
    finally:
        cursor.close()
        conn.close()


def update_actress_name(cursor:Cursor,actress_name:list[dict],actress_id)->bool:
    '''更新女优的名字'''
    #先计算要删除的部分，然后计算添加的部分
    cursor.execute("SELECT actress_name_id FROM actress_name WHERE actress_id = ?", (actress_id,))
    existing_ids = {row[0] for row in cursor.fetchall()}
    existing_ids = set(existing_ids)
    new_ids = {name['actress_name_id'] for name in actress_name if name['actress_name_id'] is not None}
    delete_ids= existing_ids - new_ids
    print(delete_ids)
    # 外键全删除
    cursor.execute("UPDATE actress_name SET redirect_actress_name_id = NULL WHERE actress_id = ?", (actress_id,))
    print("外键清理成功")
    # 3. 执行删除（只删除不再需要的）
    if delete_ids:#这个删除的时候还有外键问题
        placeholders = ','.join(['?'] * len(delete_ids))
        cursor.execute(
            f"DELETE FROM actress_name WHERE actress_name_id IN ({placeholders})",
            (*delete_ids,)
        )
    # TODO
    print("删除成功")
    #修改与添加
    for i, name_data in enumerate(actress_name):
        # 确定 name_type 和 redirect_id 的值
        # 假设 name_type 0 为主要名字，1为其他名字
        # 且 redirect_actress_name_id 指向上一条记录
        if i == 0:
            # 列表的第一条数据，name_type=0，redirect_id=None
            name_type = 1
            redirect_id = None
        else:
            # 后续数据，name_type=1，redirect_id指向上一条数据的ID
            name_type = 0
            redirect_id = last_id
        
        if name_data['actress_name_id'] is None or name_data['actress_name_id']=="":
            # 插入新名字
            print(f"插入新名字{name_data['jp']}")
            cursor.execute(
                "INSERT INTO actress_name (actress_id, name_type, cn, jp, en, kana, redirect_actress_name_id) VALUES (?,?,?,?,?,?,?)",
                (actress_id, name_type, name_data['cn'], name_data['jp'], name_data['en'], name_data['kana'], redirect_id)
            )
            print("插入新名字")
            last_id = cursor.lastrowid # 更新上一条记录的ID
            
        else:
            # 修改已有的名字
            print(f"修改现有名字{name_data['jp']}")
            cursor.execute(
                "UPDATE actress_name SET name_type = ?, cn = ?, jp = ?, en = ?, kana = ?, redirect_actress_name_id = ? WHERE actress_name_id = ?",
                (name_type, name_data['cn'], name_data['jp'], name_data['en'], name_data['kana'], redirect_id, name_data['actress_name_id'])
            )
            last_id = name_data['actress_name_id'] # 更新上一条记录的ID


def update_actress_byhand(actress_id,height,cup,birthday,hip,waist,bust,debut_date,need_update,image_urlA,actress_name):
    ''' {
            "actress_id": self._actress_id,
            "height": self._height,
            "cup": self._cup,
            "birthday": self._birthday,
            "hip": self._hip,
            "waist": self._waist,
            "bust": self._bust,
            "debut_date": self._debut_date,
            "need_update": self._need_update,
            "image_urlA": self._image_urlA,
            "actress_name": self._actress_name
        }'''
    
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()
    try:
        cursor.execute("UPDATE actress SET birthday=?,height=?,bust=?,waist=?,hip=?,cup=?,debut_date=?,need_update=?,image_urlA=? WHERE actress_id=?",(birthday,height,bust,waist,hip,cup,debut_date,need_update,image_urlA,actress_id))

        #actress_name的修改部分
        update_actress_name(cursor,actress_name,actress_id)

        conn.commit()
        logging.info("更新成功")
        print("更新成功")
        return True

    except Exception as e:
        conn.rollback()
        logging.info(f"更新女优数据失败{e}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_actor_byhand(actor_id,handsome,fat,image_url,actor_name):
    ''' {

        }'''
    
    conn=get_connection(DATABASE,False)
    logging.info("数据库打开成功")
    cursor=conn.cursor()
    try:
        cursor.execute("UPDATE actor SET handsome=?,fat=?,image_url=? WHERE actor_id=?",(handsome,fat,image_url,actor_id))

        #actor_name的修改部分
        update_actor_name(cursor,actor_name,actor_id)

        conn.commit()
        logging.info("更新成功")
        print("更新成功")
        return True

    except Exception as e:
        conn.rollback()
        logging.info(f"更新女优数据失败{e}")
        return False
    finally:
        cursor.close()
        conn.close()


def update_actor_name(cursor:Cursor,actor_name:list[dict],actor_id)->bool:
    '''更新男优的名字'''
    #先计算要删除的部分，然后计算添加的部分
    cursor.execute("SELECT actor_name_id FROM actor_name WHERE actor_id = ?", (actor_id,))
    existing_ids = {row[0] for row in cursor.fetchall()}
    existing_ids = set(existing_ids)
    new_ids = {name['actor_name_id'] for name in actor_name if name['actor_name_id'] is not None}
    delete_ids= existing_ids - new_ids
    print(delete_ids)


    # 3. 执行删除（只删除不再需要的）
    if delete_ids:#这个删除的时候还有外键问题
        placeholders = ','.join(['?'] * len(delete_ids))
        cursor.execute(
            f"DELETE FROM actor_name WHERE actor_name_id IN ({placeholders})",
            (*delete_ids,)
        )
    # TODO
    print("删除成功")
    #修改与添加
    for i, name_data in enumerate(actor_name):
        # 确定 name_type 和 redirect_id 的值
        # 假设 name_type 0 为主要名字，1为其他名字
        # 且 redirect_actor_name_id 指向上一条记录
        if i == 0:
            # 列表的第一条数据，name_type=0
            name_type = 1
        else:
            # 后续数据，name_type=1
            name_type = 0

        if name_data['actor_name_id'] is None or name_data['actor_name_id']=="":
            # 插入新名字
            print(f"插入新名字{name_data['jp']}")
            cursor.execute(
                "INSERT INTO actor_name (actor_id, name_type, cn, jp, en, kana) VALUES (?,?,?,?,?,?)",
                (actor_id, name_type, name_data['cn'], name_data['jp'], name_data['en'], name_data['kana'])
            )
            print("插入新名字")
        else:
            # 修改已有的名字
            print(f"修改现有名字{name_data['jp']}")
            cursor.execute(
                "UPDATE actor_name SET name_type = ?, cn = ?, jp = ?, en = ?, kana = ? WHERE actor_name_id = ?",
                (name_type, name_data['cn'], name_data['jp'], name_data['en'], name_data['kana'], name_data['actor_name_id'])
            )
