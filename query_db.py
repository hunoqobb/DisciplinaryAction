import sqlite3
import os

# 连接到数据库
db_path = os.path.join('data', 'student_management.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
cursor = conn.cursor()

# 查询所有学生
print('\n===== 查询所有学生 =====')
cursor.execute('SELECT * FROM students')
students = cursor.fetchall()
for student in students:
    print(f"ID: {student['id']}, 姓名: {student['name']}, 性别: {student['gender']}, 年级ID: {student['grade_id']}, 专业班级ID: {student['class_id']}")

# 查询所有年级
print('\n===== 查询所有年级 =====')
cursor.execute('SELECT * FROM grades')
grades = cursor.fetchall()
for grade in grades:
    print(f"ID: {grade['id']}, 名称: {grade['name']}")

# 查询所有专业班级
print('\n===== 查询所有专业班级 =====')
cursor.execute('SELECT * FROM classes')
classes = cursor.fetchall()
for cls in classes:
    print(f"ID: {cls['id']}, 名称: {cls['name']}")

# 查询张三的记录
print('\n===== 查询张三的记录 =====')
cursor.execute("""
    SELECT s.id, s.name, s.gender, g.name as grade_name, c.name as class_name, s.grade_id, s.class_id 
    FROM students s 
    JOIN grades g ON s.grade_id = g.id 
    LEFT JOIN classes c ON s.class_id = c.id 
    WHERE s.name LIKE '%张三%'
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 年级ID: {row['grade_id']}, 专业班级ID: {row['class_id']}")
else:
    print("未找到张三的记录")

# 查询2023级护理专业的学生
print('\n===== 查询2023级护理专业的学生 =====')
cursor.execute("""
    SELECT s.id, s.name, s.gender, g.name as grade_name, c.name as class_name, s.grade_id, s.class_id 
    FROM students s 
    JOIN grades g ON s.grade_id = g.id 
    LEFT JOIN classes c ON s.class_id = c.id 
    WHERE g.name LIKE '%2023%' AND c.name LIKE '%护理%'
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 年级ID: {row['grade_id']}, 专业班级ID: {row['class_id']}")
else:
    print("未找到2023级护理专业的学生")

# 查询处分记录
print('\n===== 查询处分记录 =====')
cursor.execute("""
    SELECT p.id, s.name, s.gender, g.name as grade_name, c.name as class_name, pt.name as punishment_type, p.date, p.required_points,
           CASE WHEN p.is_cleared = 1 THEN '已核销' ELSE '未核销' END as status,
           s.grade_id, s.class_id
    FROM punishments p
    JOIN students s ON p.student_id = s.id
    JOIN grades g ON s.grade_id = g.id
    LEFT JOIN classes c ON s.class_id = c.id
    JOIN punishment_types pt ON p.type_id = pt.id
    ORDER BY p.date DESC
""")
results = cursor.fetchall()
if results:
    for row in results:
        print(f"ID: {row['id']}, 姓名: {row['name']}, 性别: {row['gender']}, 年级: {row['grade_name']}, 专业班级: {row['class_name']}, 处分类型: {row['punishment_type']}, 日期: {row['date']}, 状态: {row['status']}, 年级ID: {row['grade_id']}, 专业班级ID: {row['class_id']}")
else:
    print("未找到处分记录")

# 关闭连接
conn.close()

print('\n查询完成，请检查结果以确定问题所在。')