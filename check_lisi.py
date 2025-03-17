import sqlite3
import os

# 连接到数据库
db_path = os.path.join('data', 'student_management.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
cursor = conn.cursor()

print('\n===== 查询李四的学生信息 =====')
cursor.execute("""
    SELECT s.id, s.name, s.gender, g.name as grade_name, c.name as class_name, s.grade_id, s.class_id 
    FROM students s 
    JOIN grades g ON s.grade_id = g.id 
    LEFT JOIN classes c ON s.class_id = c.id 
    WHERE s.name = '李四'
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 年级ID: {row['grade_id']}, 专业班级ID: {row['class_id']}")
else:
    print("未找到李四的学生记录")

print('\n===== 查询李四的处分记录 =====')
cursor.execute("""
    SELECT p.id, s.name, s.gender, g.name as grade_name, c.name as class_name, pt.name as punishment_type, p.date, p.required_points,
           CASE WHEN p.is_cleared = 1 THEN '已核销' ELSE '未核销' END as status,
           s.grade_id, s.class_id, s.id as student_id
    FROM punishments p
    JOIN students s ON p.student_id = s.id
    JOIN grades g ON s.grade_id = g.id
    LEFT JOIN classes c ON s.class_id = c.id
    JOIN punishment_types pt ON p.type_id = pt.id
    WHERE s.name = '李四'
    ORDER BY p.date DESC
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"处分ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 处分类型: {row['punishment_type']}, 日期: {row['date']}, 状态: {row['status']}, 年级ID: {row['grade_id']}, 专业班级ID: {row['class_id']}, 学生ID: {row['student_id']}")
else:
    print("未找到李四的处分记录")

print('\n===== 查询李四的公益活动记录 =====')
cursor.execute("""
    SELECT a.id, s.name, s.gender, g.name as grade_name, c.name as class_name, a.content, a.date, a.duration, a.points
    FROM activities a
    JOIN students s ON a.student_id = s.id
    JOIN grades g ON s.grade_id = g.id
    LEFT JOIN classes c ON s.class_id = c.id
    WHERE s.name = '李四'
    ORDER BY a.date DESC
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"活动ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 活动内容: {row['content']}, 日期: {row['date']}, 时长: {row['duration']}, 积分: {row['points']}")
else:
    print("未找到李四的公益活动记录")

# 模拟activity_tab.py中的添加活动记录查询
print('\n===== 模拟添加活动记录时的查询 =====')
name = "李四"
gender = "女"
grade_id = 2  # 2021级
class_id = 5  # 人工智能1班

cursor.execute("""
    SELECT id FROM students
    WHERE name = ? AND gender = ? AND grade_id = ? AND class_id = ?
""", (name, gender, grade_id, class_id))
result = cursor.fetchone()

if result:
    student_id = result[0]
    print(f"找到学生ID: {student_id}，可以添加活动记录")
else:
    print("未找到匹配的学生记录，无法添加活动记录")
    # 检查是否存在部分匹配的记录
    cursor.execute("SELECT id, name, gender, grade_id, class_id FROM students WHERE name = ?", (name,))
    partial_matches = cursor.fetchall()
    if partial_matches:
        print("\n找到部分匹配的记录:")
        for match in partial_matches:
            print(f"ID: {match['id']}, 姓名: {match['name']}, 性别: {match['gender']}, 年级ID: {match['grade_id']}, 专业班级ID: {match['class_id']}")

# 关闭连接
conn.close()