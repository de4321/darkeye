#推荐算法，
#目标是根据算法推荐每次打开软件的时候运算，推荐7部片子在首页，然后有缓存机制
import sqlite3
from config import DATABASE

def randomRec()->list[dict]:
    '''读数据库的所有的片子，然后随机选7部，返回作品的基本数据的字典列表'''

    
    query='''
    SELECT 
        work_id,serial_number,story,release_date,image_url,cn_title,cn_story 
    FROM work 
    WHERE image_url !='----'
    ORDER BY RANDOM()
    LIMIT 7
    '''
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]    #可选：获取字段名
    # 转换为列表字典
    result = [dict(zip(column_names, row)) for row in rows]
    return result

def recommendStart()->list[dict]:
    '''推荐特定初始作品数,一方面用来测试'''
    #安全测试，封面相对安全
    SerialNumber=["SONE-852","IPX-247","IPX-177","SSNI-497","JUR-020","START-257"]
    
    #bug测试
    #SerialNumber=["SONE-247","SSIS-783","SSIS-706"]

    #个人推荐的测试
    #SerialNumber=["SONE-852","STARS-171","IPX-247","SONE-521","IPX-177","SSNI-497","SDMF-016","IPX-726","IPX-149","STARS-979","JUR-020","IPX-776","LULU-234","JUL-388","SSNI-865","ABP-159","ATID-566","SNIS-675","START-257","PPPE-062","CAWD-584","MIAA-870","SSNI-830"]
    
    # 3. 构建 SQL 查询
    placeholders = ', '.join('?' for _ in SerialNumber)
    query = f'''
    SELECT work_id,serial_number,story,release_date,image_url,cn_title,cn_story
    FROM work
    WHERE serial_number IN ({placeholders})
    '''
    # 4. 执行查询

    with sqlite3.connect(f"file:{DATABASE}?mode=ro",uri=True) as conn:
        cursor = conn.cursor()
        cursor.execute(query, SerialNumber)
        rows = cursor.fetchall()
        #获取字段名
        column_names = [description[0] for description in cursor.description]

    #转换为列表字典
    result = [dict(zip(column_names, row)) for row in rows]
    result.sort(key=lambda x: SerialNumber.index(x['serial_number']))#按照输入的排序

    # 5. 查看结果
    return result
    

