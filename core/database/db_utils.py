from config import PRIVATE_DATABASE
import sqlite3
from pathlib import Path
import logging

def attach_private_db(cursor:sqlite3.Cursor):
    attachsql = f"ATTACH DATABASE {repr(str(PRIVATE_DATABASE))} AS priv"
    cursor.execute(attachsql)

def detach_private_db(cursor:sqlite3.Cursor):
    cursor.execute("DETACH DATABASE priv")



def image_consistency(delete_extra:bool=False,scope:str="cover"):
    '''验证数据库中work中image_url字段与文件夹里的图片是否匹配
    delete_extra是否删除默认的，默认不删除
    scope 范围，默认是cover
        '''
    from config import WORKCOVER_PATH,ACTORIMAGES_PATH,ACTRESSIMAGES_PATH
    from config import DATABASE
    import os

    match scope:
        case "cover":
            image_path=WORKCOVER_PATH
            query="SELECT image_url FROM work"

        case "actress":
            image_path=ACTRESSIMAGES_PATH
            query="SELECT image_urlA FROM actress"
        case "actor":
            image_path=ACTORIMAGES_PATH
            query="SELECT image_url FROM actor"

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    db_files = set(row[0] for row in rows if row[0])

    # 2. 获取文件夹中所有文件名
    folder_files = set(f.name for f in image_path.iterdir() if f.is_file())

    # 3. 数据库缺失的文件
    missing_files = db_files - folder_files
    if missing_files:
        logging.debug(f"数据库记录的{scope}图片文件缺失：")
        for f in missing_files:
            logging.debug(f"  {f}")
    else:
        logging.debug(f"数据库记录的{scope}图片文件全部存在。")

    # 4. 文件夹多余的文件
    extra_files = folder_files - db_files
    if extra_files:
        logging.debug(f"文件夹中存在多余{scope}文件：")
        for f in extra_files:
            logging.debug(f"  {f}")
            if delete_extra:
                os.remove(image_path / f)
                logging.debug("    已删除")
    else:
        logging.debug(f"文件夹中没有多余{scope}文件。")



def sqlite_vaccum():
    '''清理数据库碎片'''
    from .connection import get_connection
    from config import DATABASE,PRIVATE_DATABASE,DATABASE_BACKUP_PATH,PRIVATE_DATABASE_BACKUP_PATH
    from .backup_utils import backup_database
    try:
        #先备份后清理碎片
        backup_database(DATABASE,DATABASE_BACKUP_PATH)
        conn1=get_connection(DATABASE)
        conn1.execute("VACUUM;")
        conn1.close()

        backup_database(PRIVATE_DATABASE,PRIVATE_DATABASE_BACKUP_PATH)
        conn2=get_connection(PRIVATE_DATABASE)
        conn2.execute("VACUUM;")
        conn2.close()
        logging.warning(f"清理碎片成功")
    except Exception as e:
        logging.warning(f"清理碎片错误:{e}")
        #从备份恢复

def clear_temp_images():
    '''清理temp文件夹中所有的临时的图片'''


def clear_temp_folder():
    """清空临时目录下的所有文件和子文件夹"""
    from config import TEMP_PATH
    import shutil
    temp_path=TEMP_PATH
    try:
        if not temp_path.exists():
            logging.info(f"临时目录不存在: {temp_path}")
            return
        
        # 遍历删除所有内容（文件 + 子目录）
        for item in temp_path.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()  # 删除文件或符号链接
                elif item.is_dir():
                    shutil.rmtree(item)  # 递归删除目录
            except Exception as e:
                logging.warning(f"删除失败: {item} ({e})")

        logging.info(f"✅ 已清空临时目录: {temp_path}")

    except Exception as e:
        logging.error(f"❌ 清空临时目录失败: {e}")

def pp_consistency():
    '''公库与私库的work_id一致性检查actress_id
    用于公库发生剧烈变化，合并等操作后的检查
    '''
    pass


def generate_standard_db():
    '''制作标准库用于软件的开发与测试
    包含50部影片+尽量少的男女优+空的私有库
    '''
    number=["ABP-159","SONE-855","IPX-149","PPPE-062","SSIS-798","SSNI-497","MIAA-870","STARS-910","STARS-171","IPX-177","IPX-475","IPX-726","START-126","JUL-388","CAWD-584","LULU-234","SDDE-652","SSIS-037","SONE-852","JUR-020","MEYD-931","SSNI-454","IPX-247","WAAA-098","IPX-811","SDMF-016","SDMF-029","MIDV-407","IPZZ-317","PRED-743","HMN-196","DPMX-015","URE-055","MIDV-229","DASS-490","SONE-521","FNS-052","ABW-322","EYAN-203","STARS-990","STARS-234","SONE-308","STARS-804","IPX-388","START-073","MOON-018","JUR-202","FSDSS-077","MEYD-568","START-140"]
    #只留下上面50个番号，其他全部删除
    from .query import get_workid_by_serialnumber,get_all_work_id
    from .delete import delete_work
    work_id_list=[]
    for n in number:
        work_id_list.append(get_workid_by_serialnumber(n))
    #print(work_id_list)
    print(work_id_list)
    ids_delete=set(get_all_work_id())-set(work_id_list)
    print(ids_delete)
    error_list=[]
    for id in ids_delete:
        if not delete_work(id):
            error_list.append(id)
    if error_list:
        print(f"删除失败的work_id{error_list}")
    else:
        print("删除完成")


def clear_actress():
    '''清理多余的女优'''
    from core.database.query import get_null_actress
    from core.database.delete import delete_actress
    actress_id_list=get_null_actress()
    errorlist=[]
    print(f"要删除的actress_id{actress_id_list}")
    for actress_id in actress_id_list:
        success,e=delete_actress(actress_id)
        if not success:
            errorlist.append(actress_id)
    if errorlist:
        print(f"删除失败的actress_id{errorlist}")
    else:
        print("删除完成")

def clear_actor():
    '''清理多余的男优'''
    from core.database.query import get_null_actor
    from core.database.delete import delete_actor
    actor_id_list=get_null_actor()
    errorlist=[]
    print(f"要删除的actor_id{actor_id_list}")
    for actor_id in actor_id_list:
        success,e=delete_actor(actor_id)
        if not success:
            errorlist.append(actor_id)
    if errorlist:
        print(f"删除失败的actor_id{errorlist}")
    else:
        print("删除完成")