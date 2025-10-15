--视图一，查询作品的基本数据的表
--DROP VIEW IF EXISTS v_work_all_info;
CREATE VIEW IF NOT EXISTS v_work_all_info AS
WITH actress_age_at_release AS (--计算每个女优发布作品的年龄
  SELECT
    w.work_id,
    a.actress_id,
    w.serial_number,
    w.release_date,
    a.birthday,
    -- 使用 julianday 计算日期差（以天为单位），然后除以 365.25 得到年龄
    (julianday(w.release_date) - julianday(a.birthday)) / 365.25 AS age_at_release
  FROM work w
  JOIN work_actress_relation war ON w.work_id = war.work_id
  JOIN actress a ON war.actress_id = a.actress_id
  WHERE w.release_date IS NOT NULL AND a.birthday IS NOT NULL
),
average_age_per_work AS (--辅助计算年龄的表
  SELECT
    work_id,
    serial_number,
    ROUND(AVG(age_at_release), 1)-0.45 AS avg_age_at_release--假设拍摄后5个多月发布
  FROM actress_age_at_release
  GROUP BY work_id
),
actress_list AS(--计算女优出演的名单
SELECT
	w.work_id,
    GROUP_CONCAT(
        (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)),
        ','
    ) AS actress_list,
	GROUP_CONCAT(war.job,',') AS job,
	GROUP_CONCAT(war.state,',') AS state
FROM
    work w
LEFT JOIN 
    work_actress_relation war ON w.work_id = war.work_id
LEFT JOIN 
    actress a ON war.actress_id = a.actress_id
GROUP BY w.work_id
),
actor_list AS(--男优名单
SELECT
	w.work_id,
    GROUP_CONCAT(
        (SELECT cn FROM actor_name WHERE actor_id=war1.actor_id),
        ','
    ) AS actor_list
FROM
    work w
LEFT JOIN 
    work_actor_relation war1 ON w.work_id = war1.work_id
LEFT JOIN 
    actor a ON war1.actor_id = a.actor_id
GROUP BY w.work_id
),
studio_list AS(--片商表
SELECT 
	w.work_id,
	(SELECT cn_name FROM maker WHERE maker_id =p.maker_id) AS studio_name
FROM 
    work w
INNER JOIN 
    prefix_maker_relation p ON p.prefix = SUBSTR(w.serial_number, 1, INSTR(w.serial_number, '-') - 1)
WHERE 
    w.serial_number LIKE '%-%'
)
SELECT --水平计算表，然后统一合并
	w.work_id,
    w.serial_number AS serial_number,
    w.director AS director,
	w.release_date AS release_date,
	(SELECT actress_list FROM actress_list WHERE work_id=w.work_id)AS actress,
	(SELECT avg_age_at_release FROM average_age_per_work WHERE work_id=w.work_id)AS avg_age,
	(SELECT state FROM actress_list WHERE work_id=w.work_id)AS state,
	(SELECT actor_list FROM actor_list WHERE work_id=w.work_id)AS actor,
	w.story AS story,
	w.cn_title,
	w.cn_story,
	w.jp_title,
	w.jp_story,
	(SELECT studio_name FROM studio_list WHERE work_id=w.work_id)AS studio
FROM 
    work w;
	
----------------------------------------------------------------------------------------------------------------------
--查询女优的基本数据的表
--DROP VIEW IF EXISTS v_actress_all_info;
CREATE VIEW IF NOT EXISTS v_actress_all_info AS
SELECT 
    actress_id AS "女优ID",
    (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)) AS "中文名",
	(SELECT jp FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)) AS "日文名",
	(SELECT en FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)) AS "英文名",
	(SELECT kana FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)) AS "假名",
    (
        SELECT GROUP_CONCAT(cn, ',') 
        FROM actress_name 
        WHERE actress_id = a.actress_id AND (name_type = 3 OR name_type=4)
		) AS "别名",
    birthday AS "出生日期",
    height AS "身高(cm)",
    bust AS "胸围(cm)",
    waist AS "腰围(cm)",
    hip AS "臀围(cm)",
    cup AS "罩杯",
	debut_date AS "出道日期",
	round((julianday(debut_date)-julianday(birthday))/365.25,1)-0.25 AS "出道年龄",
	need_update
FROM actress a;


----------------------------------------------------------------------------------------------------------------------
--查询一个女优在我的收藏的库里拍摄的影片数量
--DROP VIEW IF EXISTS v_actress_movie_stats;
CREATE VIEW IF NOT EXISTS v_actress_movie_stats AS
SELECT 
    a.actress_id,
    (SELECT cn FROM actress_name WHERE actress_id = a.actress_id AND(name_type=1)) AS actress_name,
    COUNT(war.work_id) AS total_movies,
    MIN(w.release_date) AS first_movie_date,
    MAX(w.release_date) AS latest_movie_date
FROM 
    actress a
LEFT JOIN work_actress_relation war ON a.actress_id = war.actress_id
LEFT JOIN work w ON war.work_id = w.work_id
GROUP BY a.actress_id
ORDER BY total_movies DESC;

----------------------------------------------------------------------------------------------------------------------

