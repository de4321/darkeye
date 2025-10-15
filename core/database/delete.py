import sqlite3
from config import DATABASE,PRIVATE_DATABASE
import logging
from .connection import get_connection

def delete_favorite_actress(actress_id)->bool:
    '''删除私有库中喜欢的女优记录'''
    success=False
    try:
        conn = sqlite3.connect(PRIVATE_DATABASE)
        cursor = conn.cursor()
        
        #添加的自慰记录
        cursor.execute("DELETE FROM favorite_actress WHERE actress_id=?",(actress_id,))
        conn.commit()
        logging.info(f"删除记录成功")
        success=True
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
    finally:
        cursor.close()
        conn.close()

    return success

def delete_favorite_work(work_id)->bool:
    '''删除私有库中喜欢的作品记录'''
    success=False
    try:
        conn = sqlite3.connect(PRIVATE_DATABASE)
        cursor = conn.cursor()
        
        #添加的自慰记录
        cursor.execute("DELETE FROM favorite_work WHERE work_id=?",(work_id,))
        conn.commit()
        logging.info(f"删除记录成功")
        success=True
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
    finally:
        cursor.close()
        conn.close()

    return success

def delete_work(work_id:int)->bool:
    '''彻底删除作品'''
    from utils.utils import delete_image
    try:
        conn = get_connection(DATABASE)
        cursor = conn.cursor()
        
        #删除私有库中喜欢的作品记录,但是这个问题不大，先不弄了
        #delete_favorite_work(work_id)
        cursor.execute("DELETE FROM work_actress_relation WHERE work_id=?",(work_id,))
        cursor.execute("DELETE FROM work_actor_relation WHERE work_id=?",(work_id,))
        cursor.execute("DELETE FROM work_tag_relation WHERE work_id=?",(work_id,))
        cursor.execute("SELECT image_url FROM work WHERE work_id=?",(work_id,))
        image_url=cursor.fetchone()


        cursor.execute("DELETE FROM work WHERE work_id=?",(work_id,))
        conn.commit()
        logging.info(f"删除记录成功")
        # 成功后这里删除图片，或者后面用其他工具完成一致性
        if image_url and image_url[0]:
            from config import WORKCOVER_PATH
            from pathlib import Path
            delete_image(Path(WORKCOVER_PATH/image_url[0]))
        return True
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
        return False
    finally:
        cursor.close()

def delete_actress(actress_id:int)->tuple[bool,str]:
    '''删除某个女优，包括名字'''
    from utils.utils import delete_image
    try:
        conn = get_connection(DATABASE)
        cursor = conn.cursor()
        
        #删除私有库中喜欢的作品记录,但是这个问题不大，先不弄了
        #删除某个女优的喜欢的记录，不过先不弄了
        #先删除
        cursor.execute("SELECT image_urlA FROM actress WHERE actress_id=?",(actress_id,))
        image_url=cursor.fetchone()
        cursor.execute("DELETE FROM actress_name WHERE actress_id=?",(actress_id,))
        cursor.execute("DELETE FROM actress WHERE actress_id=?",(actress_id,))

        logging.info(image_url)
        conn.commit()
        logging.info(f"删除女优成功")
        
        #这里还要删除女优的头像
        if image_url and image_url[0]:
            from config import ACTRESSIMAGES_PATH
            from pathlib import Path
            delete_image(Path(ACTRESSIMAGES_PATH/image_url[0]))
        return True,"删除女优成功"
    except sqlite3.IntegrityError as e:
        # 捕获外键约束异常
        if "FOREIGN KEY constraint failed" in str(e):
            logging.warning(f"删除失败：存在关联数据，无法删除女优ID {actress_id}")
            return False,"存在包含该女优的作品,无法删除该女优"
        else:
            logging.warning(f"删除失败：完整性约束错误 {e}")
        if conn:
            conn.rollback()
        return False,"删除失败"
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
        return False,"删除失败"
    finally:
        cursor.close()

def delete_actor(actor_id:int)->tuple[bool,str]:
    '''删除某个男优，包括名字'''
    from utils.utils import delete_image
    try:
        conn = get_connection(DATABASE)
        cursor = conn.cursor()
        
        #删除私有库中喜欢的作品记录,但是这个问题不大，先不弄了
        #删除某个女优的喜欢的记录，不过先不弄了
        #先删除
        cursor.execute("SELECT image_url FROM actor WHERE actor_id=?",(actor_id,))
        image_url=cursor.fetchone()
        cursor.execute("DELETE FROM actor_name WHERE actor_id=?",(actor_id,))
        cursor.execute("DELETE FROM actor WHERE actor_id=?",(actor_id,))

        logging.info(image_url)
        conn.commit()
        logging.info(f"删除男优成功")
        
        #这里还要删除男优的头像
        if image_url and image_url[0]:
            from config import ACTORIMAGES_PATH
            from pathlib import Path
            delete_image(Path(ACTORIMAGES_PATH/image_url[0]))
        return True,"删除男优成功"
    except sqlite3.IntegrityError as e:
        # 捕获外键约束异常
        if "FOREIGN KEY constraint failed" in str(e):
            logging.warning(f"删除失败：存在关联数据，无法删除男优ID {actor_id}")
            return False,"存在包含该男优的作品,无法删除该女优"
        else:
            logging.warning(f"删除失败：完整性约束错误 {e}")
        if conn:
            conn.rollback()
        return False,"删除失败"
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
        return False,"删除失败"
    finally:
        cursor.close()



def delete_tag(tag_id:int)->tuple[bool,str]:
    '''删除某个tag'''

    message=""
    try:
        conn = get_connection(DATABASE)
        cursor = conn.cursor()

        #先删除redirect_tag_id
        cursor.execute("DELETE FROM tag WHERE redirect_tag_id=?",(tag_id,))
        #后删除
        cursor.execute("DELETE FROM tag WHERE tag_id=?",(tag_id,))

        conn.commit()
        logging.info(f"删除标签成功")

        return True,"删除标签成功"
    except sqlite3.IntegrityError as e:
        # 捕获外键约束异常
        if "UNIQUE constraint failed: tag.tag_name" in str(e):
            logging.warning(f"删除失败：该标签已使用 {tag_id}")
            message="该标签已使用"
        else:
            logging.warning(f"删除失败：Tag完整性约束错误 {e}")
        if conn:
            conn.rollback()
        return False,message
    except Exception as e:
        conn.rollback()
        logging.info(f"删除失败{e}")
        return False,"删除失败"
    finally:
        cursor.close()