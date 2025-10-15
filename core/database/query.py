'''
这里写查询与数据库交互的函数，不会污染破坏数据库。
'''
import sqlite3
from config import DATABASE,PRIVATE_DATABASE
import logging
from .db_utils import attach_private_db,detach_private_db
from .connection import get_connection

# 跨库的CTE查询，无法直接在sqlite数据库里的创造的视图
masturbationsql=f'''masturbation_count AS(--按照有work_id撸管记录，统计每部作品撸了几次
SELECT 
	mas.work_id AS work_id,
    w.serial_number AS serial_number,
	count(mas.work_id)AS masturbation_count
FROM priv.masturbation mas
LEFT JOIN work w ON mas.work_id=w.work_id
WHERE mas.work_id is not NULL AND mas.work_id !=''
GROUP BY mas.work_id
)
'''

masturbation_actress_sql=f'''masturbation_actress AS(
SELECT 
    a.actress_id,
    -- 当前使用现用名
    (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND name_type = 1) AS actress_name,
    COUNT(m.work_id) AS num,
	MAX(m.start_time) AS latest_masturbate_time
FROM 
    actress a
LEFT JOIN work_actress_relation war ON a.actress_id = war.actress_id
LEFT JOIN work w ON war.work_id = w.work_id
LEFT JOIN priv.masturbation m ON m.work_id = w.work_id
GROUP BY a.actress_id
ORDER BY 
num DESC,
latest_masturbate_time DESC
)
'''

#----------------------------------------------------------------------------------------------------------
#                                               公共数据库的查询
#----------------------------------------------------------------------------------------------------------

def get_all_work_id()->list[int]:
    '''获得所有的work_id'''
    query = '''
    SELECT
    work_id
    FROM
    work
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def query_studio(work_id:int)->str|None:
    '''根据work_id返回发行商，如果为非标准发行商，就是私拍，或者没有封面的，就返回None'''
    query='''
SELECT 
	(SELECT cn_name FROM maker WHERE maker_id =p.maker_id) AS studio_name
FROM 
    work w
INNER JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(w.serial_number, 1, INSTR(w.serial_number, '-') - 1)
WHERE 
   work_id=?
'''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(work_id,))
        row = cursor.fetchone()
    #logging.debug(row)
    if row is not None:
        return row[0]
    else:
        return None

def get_actress_info(actress_id:int)->dict:
    '''查询一个女优的所有的信息'''
    query='''
SELECT
    n.cn,
    n.jp,
    n.en,
    n.kana,
    ROUND((julianday('now') - julianday(a.birthday)) / 365.25, 1) AS age,
    a.image_urlA,
    a.birthday,
    a.height,
    a.bust,
    a.waist,
    a.hip,
    a.cup,
    a.debut_date,
    a.need_update
FROM actress a
LEFT JOIN actress_name n
    ON n.actress_id = a.actress_id
   AND n.redirect_actress_name_id IS NULL
WHERE a.actress_id = ?
'''

    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actress_id,))
        row = cursor.fetchone()
        logging.debug(f"查询到女优的信息：\n{row}")
        column_names = [description[0] for description in cursor.description]
    return dict(zip(column_names, row))

def get_actor_info(actor_id:int)->dict:
    '''查询一个男演员的所有数据'''
    query='''
SELECT
    n.cn,
    n.jp,
    n.en,
    n.kana,
    a.image_url,
    a.birthday,
	a.handsome,
	a.fat
FROM actor a
LEFT JOIN actor_name n
    ON n.actor_id = a.actor_id
WHERE a.actor_id = ?
'''

    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actor_id,))
        row = cursor.fetchone()
        logging.debug(f"查询到男优的信息：\n{row}")
        column_names = [description[0] for description in cursor.description]
    return dict(zip(column_names, row))

def get_all_actress_data()->list[dict]:
    '''公共库内女优的身材数据'''
    query='''
            SELECT
                height,
                bust,
                waist,
                hip,
				cup
            FROM 
                actress a
            WHERE 
                height is NOT NULL AND height !=0
                AND waist IS NOT NULL AND waist !=0
                AND hip IS NOT NULL AND hip !=0
				AND bust IS NOT NULL AND bust !=0
				AND cup IS NOT NULL
            '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
    return results

def get_null_actress()->list:
    '''返回所有的没有作品的actress_id列表'''
    query="""
SELECT a.actress_id
	--(SELECT cn FROM actress_name WHERE actress_id=a.actress_id )AS name
FROM actress AS a
LEFT JOIN work_actress_relation AS r
    ON a.actress_id = r.actress_id
WHERE r.actress_id IS NULL;
"""
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_null_actor()->list:
    '''返回所有的没有作品的actor_id列表'''
    query="""
SELECT a.actor_id
	--(SELECT cn FROM actor_name WHERE actor_id=a.actor_id )AS name
FROM actor AS a
LEFT JOIN work_actor_relation AS r
    ON a.actor_id = r.actor_id
WHERE r.actor_id IS NULL;
"""
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_tag_type()->list[dict]:
    '''获得所有的tag_type'''
    query='''
SELECT
	tag_type_id,
	tag_type_name,
	tag_order
FROM
	tag_type
ORDER BY tag_order
            '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
    return results

def get_alias_tag(tag_id:int)->list[dict]:
    '''获得那些被重定向后的tag'''
    query='''
SELECT 
	tag_id,
    tag_name,
    redirect_tag_id
FROM tag 
WHERE redirect_tag_id=?
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(tag_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
    return results

# 加载tag_selector使用
def getTags()->list[tuple]:
    '''读取所有的tag库里的信息'''
    query='''
SELECT 
	tag_id, 
	tag_name, 
    tag_type.tag_type_name AS tag_name,
	color,
	detail,
	group_id
FROM tag 
JOIN tag_type ON tag_type.tag_type_id=tag.tag_type_id
WHERE redirect_tag_id is NULL 
ORDER BY tag_type.tag_order,color
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
    return results

def exist_actress(name)->int|None:
    '''根据name查询actress是否在库内'''
    query = f'''
        SELECT
        actress_id
        FROM
        actress_name
        WHERE
        actress_name.jp=? OR actress_name.cn=? OR actress_name.en=?
        '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(name,name,name))
        id = cursor.fetchone()
        if id is None:
            return None
        else:
            return id[0]

def exist_actor(name)->int|None:
    '''根据name查询actor是否在库内'''
    query = f'''
        SELECT
        actor_id
        FROM
        actor_name
        WHERE
        actor_name.jp=? OR actor_name.cn=? OR actor_name.en=?
        '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(name,name,name))
        id = cursor.fetchone()
        if id is None:
            return None
        else:
            return id[0]

def get_taginfo_by_id(tag_id:int)->dict:
    '''通过tag_id查询tag的所有的信息'''
    query='''
SELECT
	tag_id,
	tag_name,
	tag_type_id,
	color,
	detail,
	redirect_tag_id
FROM tag
WHERE tag_id=?
'''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(tag_id,))
        row = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]

    return dict(zip(column_names, row))


def get_tagid_by_keyword(keyword:str,match_hole_word=False)->list:
    '''这个递归搜索到所有的没有重定向的tag'''
    query=f"""
    WITH RECURSIVE tag_chain AS (
    -- 初始搜索
    SELECT tag_id
    FROM tag
    WHERE tag_name LIKE ?

    UNION ALL

    -- 递归跟随 redirect_tag_id
    SELECT t.redirect_tag_id
    FROM tag t
    JOIN tag_chain tc ON t.tag_id = tc.tag_id
    WHERE t.redirect_tag_id IS NOT NULL
)
-- 最终只保留没有重定向的 tag_id
SELECT DISTINCT tc.tag_id
FROM tag_chain tc
LEFT JOIN tag t2 ON tc.tag_id = t2.tag_id AND t2.redirect_tag_id IS NOT NULL
WHERE t2.tag_id IS NULL;
"""
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if match_hole_word:
            cursor.execute(query,(f"{keyword}",))
        else:
            cursor.execute(query,(f"%{keyword}%",))
        ids = cursor.fetchall()
        if ids is None:
            return None
        else:
            return [id[0] for id in ids]

def exist_minnao_id(actress_id)->int:
    '''查询女优是否存在minnao-av的缓存'''
    query = f'''
        SELECT
            minnano_url
        FROM actress
        WHERE
            actress_id=?
        '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actress_id,))
        id = cursor.fetchone()
        if id is None:
            return None
        else:
            return id[0]


#纯纯的单查询，获得不重复的东西，给提示框用
def get_tag_name()->list:
    '''获得库中所有的tag_name'''
    query = "SELECT tag_name FROM tag"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_actressname()->list:
    '''获得库中所有的女优的名字，包括曾用名，返回女优的名字'''
    query = '''
    SELECT
    cn
    FROM
    actress_name
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_actress_allname(actress_id)->list[dict]:
    '''反回某个女优的所有名字,而且是根据链式返回的，最前面的是最新的'''
    query = '''
WITH RECURSIVE chain AS (
    -- 递归的起始部分：找到链条的起点
    -- 这里的起点是redirect_actress_name_id为NULL，并且actress_id匹配的那条记录
    SELECT
        actress_name_id,
        cn,
        jp,
        en,
        kana,
        redirect_actress_name_id,
        1 AS level -- 用于排序的层级
    FROM
        actress_name
    WHERE
        actress_id = ? AND redirect_actress_name_id IS NULL

    UNION ALL

    -- 递归部分：顺着链条查找
    SELECT
        t2.actress_name_id,
        t2.cn,
        t2.jp,
        t2.en,
        t2.kana,
        t2.redirect_actress_name_id,
        chain.level + 1 AS level -- 递增层级
    FROM
        actress_name AS t2
    JOIN
        chain ON t2.redirect_actress_name_id = chain.actress_name_id
)
SELECT
    actress_name_id,
    cn,
    jp,
    kana,
    en,
    redirect_actress_name_id,
	level
FROM
    chain
ORDER BY
    level;
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actress_id,))
        rows = cursor.fetchall()        
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
        return results

def get_actor_allname(actor_id)->list[dict]:
    '''反回某个男优的所有名字，最前面的是最新的，其他的无所谓'''
    query = '''
    SELECT
        actor_name_id,
        cn,
        jp,
        en,
        kana
    FROM
        actor_name
    WHERE
        actor_id = ?
	ORDER BY name_type
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actor_id,))
        rows = cursor.fetchall()        
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
        return results


def get_actorname()->list:
    '''返回所有的男优的名字，包括曾用名'''
    query = '''
    SELECT
    cn,
    jp
    FROM
    actor_name
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_cup_type()->list[str]:
    '''返回女优所有的罩杯类型'''
    query = "SELECT DISTINCT cup FROM actress WHERE cup is not NULL ORDER BY cup"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        cup_list= [row[0] for row in cursor.fetchall()]
    cup_list=[s for s in cup_list if s and s.strip()]#去除空数据
    return cup_list

def get_maker_name()->list:
    """获取所有的片商"""
    query = "SELECT cn_name FROM maker"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

def get_serial_number()->list:
    '''返回所有的番号'''
    query = '''
    SELECT
    serial_number
    FROM
    work
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]   

def getUniqueDirector()->list:
    '''读取独一无二的导演信息'''
    query='''
    SELECT 
        director ,
        count (*)AS num
    FROM work
    GROUP BY director
    ORDER BY num DESC
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    return [row[0] for row in rows]

def get_unique_short_story()->list:
    '''获得库中所有的简短的剧情'''
    query = '''
    SELECT
    story,
    COUNT(*) AS num
    FROM work
    GROUP BY story
    ORDER BY num DESC
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def get_tag_type_dict()->dict:
    '''获得tag_type与tag_type_id中的映射关系,这是一个一一映射关系
    '''
    query = '''
    SELECT 
        tag_type_id,
        tag_type_name
    FROM tag_type
    ORDER BY tag_order
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        logging.debug(rows)
        return dict(rows)
    
def get_unique_tag_type()->list:
    '''获得tag_type'''
    '''获得库中所有的简短的剧情'''
    query = '''
    SELECT 
    DISTINCT tag_type_name
    FROM tag_type
    ORDER BY tag_order
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    
# 根据work_id去查数据
def get_workinfo_by_workid(work_id:int)->dict:
    '''根据work_id获得单部作品的基本数据'''
    query = f'''
SELECT 
serial_number,
director,
story,
release_date,
image_url,
cn_title,
cn_story,
jp_title,
jp_story,
(SELECT cn_name FROM maker WHERE maker_id =p.maker_id) AS studio_name
FROM work 
LEFT JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(work.serial_number, 1, INSTR(work.serial_number, '-') - 1)
WHERE work_id = ?
'''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
    return [dict(zip(column_names, row)) for row in rows][0]#转成字典


def get_workcardinfo_by_workid(work_id:int)->dict:
    '''根据work_id获得单部作品的卡片数据'''
    query = f'''
SELECT 
    work.serial_number, 
    cn_title, 
    image_url,
    wtr.tag_id,
    work.work_id,
    CASE 
        WHEN (SELECT cn_name FROM maker WHERE maker_id =p.maker_id) IS NULL
        THEN 0
        ELSE 1
    END AS standard
FROM work
LEFT JOIN work_tag_relation wtr ON work.work_id = wtr.work_id AND wtr.tag_id IN (1, 2, 3)
LEFT JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(work.serial_number, 1, INSTR(work.serial_number, '-') - 1)
WHERE work.work_id= ?
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
    return [dict(zip(column_names, row)) for row in rows][0]#转成字典

def get_actressid_by_workid(work_id:int)->list:
    '''根据work_id获得对应女优的id列表'''
    query = "SELECT actress_id FROM work_actress_relation WHERE work_id = ?"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        return [row[0] for row in cursor.fetchall()]

def get_coveriamgeurl(work_id:int)->str|None:
    '''根据work_id查找对应的封面图片的地址'''
    query = '''
    SELECT 
        image_url
    FROM work
    WHERE work_id = ?
    LIMIT 1
    '''
    try:
        with get_connection(DATABASE,True) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (work_id,))
            image_rul = cursor.fetchone()
            if image_rul:
                return image_rul[0]
            else:
                return None
    except sqlite3.Error as e:
        logging.info(f"get_coverimageurl查询时数据库错误: {e}")
        return None

def get_actorid_by_workid(work_id:int)->list:
    '''根据work_id获得对应男优的id列表'''
    query = "SELECT actor_id FROM work_actor_relation WHERE work_id = ?"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        return [row[0] for row in cursor.fetchall()]

def get_worktaginfo_by_workid(work_id:int)->list[dict]:
    '''根据work_id获得单部作品的基本数据'''
    query = '''
    SELECT 
        t.tag_id,
        t.tag_name,
        tt.tag_type_name,
        t.color,
        t.detail,
		tt.tag_order
    FROM work_tag_relation wtr
    JOIN tag t ON t.tag_id=wtr.tag_id
	JOIN tag_type tt ON tt.tag_type_id=t.tag_type_id
    WHERE wtr.work_id = ?
    ORDER BY tt.tag_order,color
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in rows]#转成字典


    #暂时没有用到

def get_work_tags(work_id:int)->list:
    """获取作品已有的标签ID列表"""
    query = "SELECT tag_id FROM work_tag_relation WHERE work_id = ?"
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        return [row[0] for row in cursor.fetchall()]

def findActressFromWorkID(work_id:int)->list[dict]:
    '''
    根据输入的work_id在数据库中找到对应的女优的id和女优名字

    Args:
        work_id:作品id

    Returns:
        返回字典列表，形式为[{actress_id:xxx,actress_name:xxx},{actress_id:xxx,actress_name:xxx}]
    '''
    #根据这个单个的id去找女优的数据,这个与上面的那个可能可以合并

    query="""
    SELECT
        a.actress_id,
    (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1))AS actress_name
        
    FROM 
        work w
    JOIN 
        work_actress_relation war ON w.work_id = war.work_id 
    JOIN 
        actress a ON war.actress_id = a.actress_id
    WHERE w.work_id=?
    """
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(work_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

    if not rows:
        return None
    result = [dict(zip(column_names, row)) for row in rows]#转为字典
    #result = [{'actress_id': k, 'actress_name': v} for k, v in tuple_list]#转成字典
    return result

def findActorFromWorkID(work_id:int)->list[dict]:
    '''
    根据输入的work_id在数据库中找到对应的男优的id和男优名字

    Args:
        work_id:作品id

    Returns:
        返回字典列表，形式为[{actor_id:xxx,actor_name:xxx},{actor_id:xxx,actor_name:xxx}]返回的男优的名字只有一个
    '''
    

    query="""
    SELECT
        a.actor_id,
		(SELECT cn FROM actor_name WHERE actor_id=a.actor_id)AS actor_name
    FROM 
        work w
    JOIN 
        work_actor_relation war ON w.work_id = war.work_id 
    JOIN 
        actor a ON war.actor_id = a.actor_id
    WHERE w.work_id=?
    """
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(work_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
    #logging.debug(rows)
    if not rows:
        return None
    result = [dict(zip(column_names, row)) for row in rows]#转为字典
    #logging.debug(result)
    return result

def getActressBodyData()->list[dict]:
    '''公共库内女优的身材数据'''
    query='''
            SELECT
                bust,
                waist,
                hip,
				cup
            FROM 
                actress a
            WHERE 
                waist IS NOT NULL 
                AND hip IS NOT NULL
				AND bust IS NOT NULL
				AND cup IS NOT NULL
                AND waist !=0
                AND hip !=0
                AND bust !=0
            '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]#转成列表字典
    return results

def get_workid_by_serialnumber(serial_number)->int|None:
    '''通过番号返回work_id'''
    query = f'''
        SELECT work_id
        FROM work
        WHERE serial_number=?
        '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(serial_number,))
        id = cursor.fetchone()
        if id is None:
            return None
        else:
            return id[0]

def get_javtxt_id_by_serialnumber(serial_number)->int|None:
    '''通过番号获取javtxt的缓存'''
    query = f'''
        SELECT javtxt_id
        FROM work
        WHERE serial_number=?
        '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(serial_number,))
        id = cursor.fetchone()
        if id is None:
            return None
        else:
            return id[0]

def get_all_actress_name(actress_id:int)->list[dict]:
    
    query="""
SELECT
    actress_name_id AS id,
    jp AS name,
    redirect_actress_name_id AS redirect
FROM 
    actress_name
WHERE actress_id=?
    """
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query,(actress_id,))
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
    #logging.debug(rows)
    if not rows:
        return None
    result = [dict(zip(column_names, row)) for row in rows]#转为字典
    #logging.debug(result)
    return result
#----------------------------------------------------------------------------------------------------------
#                                      混合数据库的查询，连接公有数据库然后附加私有
#----------------------------------------------------------------------------------------------------------
#下面的6个函数是可以优化聚合减少代码行数的，但是无所谓，换成拼接的话可读性很垃圾
def fetch_work_actress_avg_age(scope:int)->list[tuple]:
    """
    获取作品中女优的平均拍摄年龄及权重。

    参数：
        scope (int):
            0 - 收藏作品内数据
            1 - 撸过作品的数据（权重固定为 1）
            2 - 撸过作品带权重的数据（权重为撸的次数）
           -1 - 公共库内作品平均年龄数据

    返回：
        list[tuple]: [(avg_age, weight), ...]
    """
    match scope:
        case 0:#收藏作品内数据
            query='''
            SELECT 
            avg_age ,
            1 AS weight
            FROM v_work_all_info
            JOIN priv.favorite_work fav ON fav.work_id=v_work_all_info.work_id
            WHERE avg_age is not NULL
            '''
        case 1:#撸过作品的数据
            query=f'''WITH {masturbationsql}
SELECT
	avg_age ,
     1 AS weight
FROM v_work_all_info
JOIN masturbation_count ON masturbation_count.work_id=v_work_all_info.work_id
WHERE avg_age is not NULL
            '''
        case 2:#撸过作品带权重的数据
            query=f'''WITH {masturbationsql}
SELECT
	avg_age ,
    masturbation_count.masturbation_count AS weight
FROM v_work_all_info
JOIN masturbation_count ON masturbation_count.work_id=v_work_all_info.work_id
WHERE avg_age is not NULL
            '''
        case -1:#公共库内作品平均年龄数据,统计有的
            query='''
            SELECT 
                avg_age,
                1 AS weight
            FROM 
                v_work_all_info 
            WHERE avg_age is not NULL
            '''
    #logging.debug(query)
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results

def fetch_actress_cup_distribution(scope: int) -> list[tuple]:
    """
    获取女优罩杯分布数据。

    参数:
        scope (int):
            - -1: 统计主库内所有女优的罩杯分布
            -  0: 统计收藏作品中女优的罩杯分布（来自私有库 priv）
            -  1: 统计撸管过的女优罩杯分布（人数，不重复）
            -  2: 统计撸管次数按罩杯分布（次数总和）

    返回:
        list[tuple]: [(cup, num/count), ...]  
            cup   -> 罩杯 (str)
            num   -> 对应人数或次数 (int)
    """
    match scope:
        case 0:#收藏作品中的女优
            query='''
            SELECT 
                cup ,
                COUNT(*) AS num
            FROM actress
            JOIN priv.favorite_actress fav ON fav.actress_id=actress.actress_id
            WHERE cup is not NULL AND cup != ''
            GROUP BY cup
            ORDER BY cup
            '''
        case 1:
            query=f'''WITH {masturbation_actress_sql}
                SELECT 
                    cup, 
                    COUNT(*) AS count
                FROM actress a
                JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
                WHERE cup IS NOT NULL AND cup != '' AND ma.num !=0
                GROUP BY cup
                ORDER BY cup
            '''
        case 2:
            query=f'''WITH {masturbation_actress_sql}
            SELECT 
                cup, 
                sum(ma.num) AS count
            FROM actress a
            JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
            WHERE cup IS NOT NULL AND cup != '' AND ma.num !=0
            GROUP BY cup
            ORDER BY cup
            '''
        case -1:#库内女优
            query='''
            SELECT
                cup, 
                COUNT(*) AS num
            FROM actress
            WHERE cup IS NOT NULL AND cup != ''
            GROUP BY cup
            ORDER BY cup
            '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results

def fetch_actress_height_with_weights(scope: int) -> list[tuple]:
    """
    根据不同的统计范围 (scope) 获取女优身高及权重数据。

    参数:
        scope (int):
            - 0: 收藏的女优（数据来自私有库 priv.favorite_actress）
            - 1: 有过自慰记录的女优（权重=1）
            - 2: 有过自慰记录的女优（权重=次数 num）
            - -1: 所有女优（权重=1）

    返回:
        list[tuple]: 每个元素为 (height, weight) 的元组列表。
            height: 女优身高 (字符串或数值)
            weight: 权重 (int) — 表示数据在统计中的重要性

    依赖:
        - 可能会使用私有数据库，需要 attach_private_db 和 detach_private_db。
        - 当 scope 为 1 或 2 时，依赖 masturbation_actress_sql 生成的 CTE。
    """
    match scope:
        case 0:#收藏中
            query='''
            SELECT 
                height,
                1 AS weight
            FROM actress
            JOIN priv.favorite_actress fav ON fav.actress_id=actress.actress_id
            WHERE height IS NOT NULL AND height != '' AND height != 0
            '''
        case 1:
            query=f'''WITH {masturbation_actress_sql}
            SELECT 
                a.height,
                1 AS weight
            FROM actress a
            JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
            WHERE height IS NOT NULL AND height != '' AND ma.num !=0  AND height != 0
            '''
        case 2:
            query=f'''WITH {masturbation_actress_sql}
            SELECT 
                a.height, 
                ma.num AS weights
            FROM actress a
            JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
            WHERE height IS NOT NULL AND height != '' AND ma.num !=0  AND height != 0
            '''
        case -1:
            query='''
            SELECT 
                height,
                1 AS weight
            FROM actress
            WHERE height IS NOT NULL AND height != '' AND height != 0
            '''
    #logging.debug(query)
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results

def fetch_actress_waist_hip_stats(scope: int) -> list[tuple]:
    """
    获取女优腰围、臀围及腰臀比的统计数据。
    
    参数:
        scope (int):
            - 0: 收藏女优数据（从私库 favorite_actress 获取）
            - 1: 撸过的女优数据（从 masturbation_actress 获取）
            - 2: 撸过的女优数据，并按撸的次数加权统计（SUM(num)）
            - -1: 公共库中所有女优数据（不依赖私库）
    
    返回:
        list[tuple]: 每个元组包含 (waist, hip, frequency/weight, wh_ratio)
            - waist: 腰围
            - hip: 臀围
            - frequency/weight: 出现次数（或权重）
            - wh_ratio: 腰臀比 (四舍五入到两位小数)
    """
    match scope:
        case 0:#收藏女优
            query='''
            SELECT 
                waist,
                hip,
                COUNT(*) AS frequency,
                round(waist*1.0/hip,2)AS wh_ratio
            FROM 
                actress a
            JOIN priv.favorite_actress fav ON fav.actress_id=a.actress_id
            WHERE 
                waist IS NOT NULL AND hip IS NOT NULL  AND waist != 0  AND hip != 0
            GROUP BY 
                waist, hip
            ORDER BY 
                frequency DESC
            '''

        case 1:#返回撸过的女优的数据
            query=f'''WITH {masturbation_actress_sql}
                SELECT 
                    waist,
                    hip,
                    COUNT(*) AS frequency,
                --	SUM(ma.num) as weight,
                    round(waist*1.0/hip,2)AS wh_ratio
                FROM 
                    actress a
                JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
                
                WHERE 
                    waist IS NOT NULL 
                    AND hip IS NOT NULL
                    AND ma.num !=0 AND waist != 0  AND hip != 0
                GROUP BY 
                    waist, hip
                ORDER BY 
                    frequency DESC
            '''

        case 2:#返回撸过的女优的数据加撸的权重

            query=f'''WITH {masturbation_actress_sql}
            SELECT 
                waist,
                hip,
            --    COUNT(*) AS frequency,
                SUM(ma.num) as weight,
                round(waist*1.0/hip,2)AS wh_ratio
            FROM 
                actress a
            JOIN masturbation_actress ma ON ma.actress_id=a.actress_id
            
            WHERE 
                waist IS NOT NULL 
                AND hip IS NOT NULL
                AND ma.num !=0 AND waist != 0  AND hip != 0
            GROUP BY 
                waist, hip
            ORDER BY 
                weight DESC
            '''
        case -1:#公共库内女优
            query='''
            SELECT 
                waist,
                hip,
                COUNT(*) AS frequency,
                round(waist*1.0/hip,2)AS wh_ratio
            FROM 
                actress a
            WHERE 
                waist IS NOT NULL AND hip IS NOT NULL AND waist != 0  AND hip != 0
            GROUP BY 
                waist, hip
            ORDER BY 
                frequency DESC
            '''
    logging.debug(f"Executing SQL:\n{query}")
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results

def fetch_top_directors_by_scope(scope: int) -> list[tuple]:
    """
    获取导演及其对应拍片数量的排名数据。

    参数:
        scope (int): 查询范围
            0  - 收藏作品中的导演及作品数
            1  - 撸过的作品导演及作品数（次数统计）
            2  - 撸过的作品导演及作品数（权重统计）
           -1  - 全库导演及作品数

    返回:
        List[tuple]: 每项为 (director:str, num:int)，按拍片数降序排列，最多返回10条
    """
    match scope:
        case 0:
            query='''
            SELECT 
                director AS director,
                COUNT(*) AS num
            FROM 
                work
            JOIN priv.favorite_work fav ON fav.work_id=work.work_id
            WHERE 
                director IS NOT NULL AND director != '----' AND director != ''
            GROUP BY 
                director
            ORDER BY 
                num DESC
            Limit 10
            '''
        case 1:
            query=f'''WITH {masturbationsql}
            SELECT 
                director AS director,
                COUNT(*) AS num
            FROM 
                work
            JOIN masturbation_count ON masturbation_count.work_id=work.work_id
            WHERE 
                director IS NOT NULL AND director != '----' AND director != ''
            GROUP BY 
                director
            ORDER BY 
                num DESC
            Limit 10
            '''          
        case 2:
            query=f'''WITH {masturbationsql}
            SELECT 
                director AS director,
                sum(masturbation_count.masturbation_count) AS num
            FROM 
                work
            JOIN masturbation_count ON masturbation_count.work_id=work.work_id
            WHERE 
                director IS NOT NULL AND director != '----' AND director != ''
            GROUP BY 
                director
            ORDER BY 
                num DESC
            Limit 10
            '''
        case -1:
            query='''
            SELECT 
                director AS director,
                COUNT(*) AS num
            FROM 
                work
            WHERE 
                director IS NOT NULL AND director != '----' AND director != ''
            GROUP BY 
                director
            ORDER BY 
                num DESC
            Limit 10
            '''
    logging.debug(f"Executing SQL:\n{query}")
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results

def fetch_top_studios_by_scope(scope: int) -> list[tuple]:
    """
    获取制作商及其对应出现次数的排名信息。

    参数:
        scope (int): 查询范围
            0  - 收藏作品中出现的制作商及数量
            1  - 作品中撸管次数非空的制作商及作品数量统计
            2  - 作品中撸管次数非空的制作商及撸管次数加权统计
           -1  - 全库中出现的制作商及数量统计

    返回:
        List[tuple]: 每项为 (studio:str, num:int)，按出现次数降序排列，最多返回10条
    """
    match scope:
        case 0:
            query='''
            SELECT 
                studio ,
                COUNT(*) AS num
            FROM 
                v_work_all_info
            JOIN priv.favorite_work fav ON fav.work_id=v_work_all_info.work_id
            WHERE 
                studio IS NOT NULL  -- 排除为NULL的记录
            GROUP BY 
                studio
            ORDER BY 
                num DESC
            LIMIT 10 
            '''
        case 1:
            query=f'''WITH {masturbationsql}
            SELECT 
                studio ,
                COUNT(*) AS num
            FROM 
                v_work_all_info
            JOIN masturbation_count ON masturbation_count.work_id=v_work_all_info.work_id
            WHERE 
                studio IS NOT NULL  -- 排除为NULL的记录
            GROUP BY 
                studio
            ORDER BY 
                num DESC
            LIMIT 10
            '''
        case 2:
            query=f'''
WITH {masturbationsql}
SELECT 
    studio ,
    sum(masturbation_count.masturbation_count) AS num
FROM 
    v_work_all_info
JOIN masturbation_count ON masturbation_count.work_id=v_work_all_info.work_id
WHERE 
    studio IS NOT NULL  -- 排除为NULL的记录

GROUP BY 
    studio
ORDER BY 
    num DESC
LIMIT 10
'''
        case -1:
            query='''
            SELECT 
                studio ,
                COUNT(*) AS num
            FROM 
                v_work_all_info
            WHERE 
                studio IS NOT NULL  -- 排除为NULL的记录
            GROUP BY 
                studio 
            ORDER BY 
                num DESC
            LIMIT 10 
            '''
    logging.debug(f"Executing SQL:\n{query}")
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        if scope in (0,1,2):attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        if scope in (0,1,2):detach_private_db(cursor)
    return results


#下面的两个实际上可以合并
def getActressByPlane()->list[tuple]:
    '''返回撸的最多的女优的次数,10个'''
    query=f'''WITH {masturbation_actress_sql}
    SELECT
        actress_name,
        num
    FROM masturbation_actress
    ORDER BY num DESC
    LIMIT 10
    '''
    logging.debug(f"Execute SQL\n{query}")
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        attach_private_db(cursor)
        cursor.execute(query)
        results = cursor.fetchall()
        detach_private_db(cursor)
    return results

def get_top_actress_by_masturbation_count(days_interval: int) -> dict|None:
    """
    获取指定天数内撸管次数最多的女优信息，若次数相同则最近撸管时间优先。

    参数:
        days_interval (int): 向前统计的天数范围。

    返回:
        dict: 包含女优姓名（中文）、头像链接、最近撸管时间及撸管次数的字典。
    """
    query='''
	SELECT 
        a.actress_id,
        (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND name_type = 1) AS actress_name,
        a.image_urlA,
        MAX(m.start_time) AS latest_masturbate_time,
        COUNT(m.work_id) AS masturbation_count
    FROM 
        actress a
    JOIN work_actress_relation war ON a.actress_id = war.actress_id
    JOIN work w ON war.work_id = w.work_id
    JOIN priv.masturbation m ON m.work_id = w.work_id  AND m.start_time >= DATE('now', printf('-%d day',?))
    GROUP BY 
        a.actress_id
    ORDER BY 
        masturbation_count DESC,
        latest_masturbate_time DESC
    LIMIT 1
    '''
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        attach_private_db(cursor)
        cursor.execute(query, (days_interval,))
        data = cursor.fetchone()
        column_names = [description[0] for description in cursor.description]
        detach_private_db(cursor)
        if data:
            return dict(zip(column_names, data))#转成字典
        else:
            return None


def get_unmasturbated_work_count() -> int:
    """
    统计收藏的影片中尚未有撸管记录的影片数量。

    说明：
        - 使用公共库中的收藏影片表（work）。
        - 通过附加私有库，关联撸管记录表（masturbation）。
        - 统计没有对应撸管记录的影片数量。

    返回：
        int: 收藏影片中未撸管的影片总数。
    """
    query=f'''WITH {masturbationsql}
SELECT
	count(*) AS total_count
FROM 
    priv.favorite_work w
LEFT JOIN masturbation_count ON masturbation_count.work_id=w.work_id
WHERE masturbation_count is NULL
'''
    #logging.debug(query)
    with get_connection(DATABASE,True) as conn:
        cursor = conn.cursor()
        attach_private_db(cursor)
        cursor.execute(query)
        count=cursor.fetchone()[0]
        detach_private_db(cursor)
    return count

#----------------------------------------------------------------------------------------------------------
#                                      私有数据库的查询
#----------------------------------------------------------------------------------------------------------

def query_actress(actress_id)->bool:
    '''判断某个actress_id是否在私有库内'''
    query='''
    SELECT 
		actress_id
    FROM 
		favorite_actress
    WHERE actress_id=?
    '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (actress_id,))
        id= cursor.fetchone()
    if id:
        return True

def query_work(work_id)->bool:
    '''判断某个actress_id是否在私有库内'''
    query='''
    SELECT 
		work_id
    FROM 
		favorite_work
    WHERE work_id=?
    '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (work_id,))
        id= cursor.fetchone()
    if id:
        return True

def get_unique_tools_from_masturbation() -> list:
    """
    查询自慰记录表 masturbation 中所有不重复的工具名称，并按使用频次从高到低排序。

    返回:
    - list: 工具名称的列表，按使用次数降序排列
    """
    query='''
        SELECT 
            tool_name ,
            count(*) AS num
        FROM masturbation
        GROUP BY tool_name
        ORDER BY num DESC
        '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
    return [row[0] for row in rows]#只提第一列

def get_record_by_year(year: int,scope:int) -> dict:
    """
    根据指定年份，查询撸管记录 masturbation 表中每天的次数统计，
    并返回一个字典，键为 QDate 类型日期，值为当天次数。

    参数:
    - year: 整数年份，例如 2025

    返回:
    - dict: {QDate: int}，键为 PySide6.QtCore.QDate 对象，值为该日撸管次数
    """
    
    match scope:
        case 0:#代表撸管记录
            query = '''
    SELECT 
        DATE(start_time) AS day,   -- 只取日期部分 YYYY-MM-DD
        COUNT(*) AS count_per_day
    FROM masturbation
    WHERE strftime('%Y', start_time) = ?  -- 筛选年份是2025
    GROUP BY day
    ORDER BY day;
    '''
        case 1:#代表做爱记录
            query = '''
    SELECT 
        DATE(event_time) AS day,   -- 只取日期部分 YYYY-MM-DD
        COUNT(*) AS count_per_day
    FROM love_making
    WHERE strftime('%Y', event_time) = ?  -- 筛选年份是2025
    GROUP BY day
    ORDER BY day;
    '''
        case 2:#代表晨勃记录
            query = '''
    SELECT 
        DATE(arousal_time) AS day,   -- 只取日期部分 YYYY-MM-DD
        COUNT(*) AS count_per_day
    FROM sexual_arousal
    WHERE strftime('%Y', arousal_time) = ?  -- 筛选年份是2025
    GROUP BY day
    ORDER BY day;
    '''

    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (str(year),))
        data = cursor.fetchall()
    result = {}
    #logging.debug(data)
    from PySide6.QtCore import QDate
    for date_str, val in data:
        year, month, day = map(int, date_str.split('-'))
        qdate = QDate(year, month, day)
        result[qdate] = val
    #logging.debug(result)
    return result

def get_record_count_in_days(days: int,scope:int) -> int:
    """
    统计指定天数内的撸管总次数。

    参数:
        days (int): 向前统计的天数范围。
        scpoe(int):统计范围，0撸管，1做爱，2晨勃

    返回:
        int: 在该时间范围内的总数。
    """
    match scope:
        case 0:#代表撸管记录
            query='''
            SELECT 
                count(*) AS count
            FROM 
                masturbation
            WHERE start_time >= DATE('now', printf('-%d day', ?))
            '''
        case 1:#代表做爱记录
            query='''
            SELECT 
                count(*) AS count
            FROM 
                love_making
            WHERE event_time >= DATE('now', printf('-%d day', ?))
            '''
        case 2:#代表晨勃记录
            query='''
            SELECT 
                count(*) AS count
            FROM 
                sexual_arousal
            WHERE arousal_time >= DATE('now', printf('-%d day', ?))
            '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (days,))
        return cursor.fetchone()[0]

def get_record_count_by_year(year: int,scope:int) -> int:
    """
    根据指定年份，查询记录的次数

    参数:
    - year: 整数年份，例如 2025
    scope:范围

    返回:
    - 次数
    """
    
    match scope:
        case 0:#代表撸管记录
            query = '''
    SELECT 
        COUNT(*) AS count
    FROM masturbation
    WHERE strftime('%Y', start_time) = ?  -- 筛选年份是2025
    '''
        case 1:#代表做爱记录
            query = '''
    SELECT 
        COUNT(*) AS count
    FROM love_making
    WHERE strftime('%Y', event_time) = ?  -- 筛选年份是2025
    '''
        case 2:#代表晨勃记录
            query = '''
    SELECT 
        COUNT(*) AS count
    FROM sexual_arousal
    WHERE strftime('%Y', arousal_time) = ?  -- 筛选年份是2025
    '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (str(year),))
        return cursor.fetchone()[0]

def get_record_early_year()->int:
    '''返回三表最早记录的年份'''
    query='''
    SELECT MIN(year) AS earliest_year FROM (
        SELECT MIN(strftime('%Y', start_time)) AS year FROM masturbation
        UNION ALL
        SELECT MIN(strftime('%Y', event_time)) AS year FROM love_making
        UNION ALL
        SELECT MIN(strftime('%Y', arousal_time)) AS year FROM sexual_arousal
    );
    '''
    with get_connection(PRIVATE_DATABASE,True) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row=cursor.fetchone()
        if row and row[0]:
            return int(row[0])
        else:
            return None