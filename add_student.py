import sqlite3
import os

# 连接到数据库
db_path = os.path.join('data', 'student_management.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
cursor = conn.cursor()

# 查找2023级的ID
cursor.execute("SELECT id FROM grades WHERE name LIKE '%2023%'")
grade_id = cursor.fetchone()['id']
print(f"2023级的ID是: {grade_id}")

# 查找护理专业的ID
cursor.execute("SELECT id FROM classes WHERE name LIKE '%护理%'")
class_ids = cursor.fetchall()
if class_ids:
    print("找到以下护理专业的ID:")
    for row in class_ids:
        print(f"ID: {row['id']}, 名称: {row['name']}")
else:
    print("未找到护理专业的记录，数据库中的专业班级:")
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    for cls in classes:
        print(f"ID: {cls['id']}, 名称: {cls['name']}")

# 添加2023级护理专业的张三
print("\n添加2023级护理专业的张三...")
try:
    # 首先检查是否已存在该学生
    cursor.execute("""
        SELECT * FROM students 
        WHERE name = '张三' AND gender = '男' AND grade_id = ? AND class_id = 1
    """, (grade_id,))
    existing = cursor.fetchone()
    
    if existing:
        print(f"该学生已存在，ID: {existing['id']}")
        student_id = existing['id']
    else:
        # 添加学生记录
        cursor.execute("""
            INSERT INTO students (name, gender, grade_id, class_id)
            VALUES (?, ?, ?, ?)
        """, ('张三', '男', grade_id, 1))
        
        # 获取新添加的学生ID
        student_id = cursor.lastrowid
        print(f"已添加学生，ID: {student_id}")
    
    # 添加处分记录
    cursor.execute("""
        INSERT INTO punishments (student_id, type_id, reason, date, required_points, is_cleared)
        VALUES (?, ?, ?, ?, ?, 0)
    """, (student_id, 1, '违反校规', '2025-03-15', 20))
    
    punishment_id = cursor.lastrowid
    print(f"已添加处分记录，ID: {punishment_id}")
    
    conn.commit()
    print("数据添加成功!")
    
    # 验证添加结果
    print("\n验证添加结果:")
    cursor.execute("""
        SELECT s.id, s.name, s.gender, g.name as grade_name, c.name as class_name, 
               p.id as punishment_id, pt.name as punishment_type
        FROM students s
        JOIN grades g ON s.grade_id = g.id
        LEFT JOIN classes c ON s.class_id = c.id
        JOIN punishments p ON p.student_id = s.id
        JOIN punishment_types pt ON p.type_id = pt.id
        WHERE s.id = ?
    """, (student_id,))
    
    result = cursor.fetchone()
    if result:
        print(f"学生ID: {result['id']}, 姓名: {result['name']}, 性别: {result['gender']}")
        print(f"年级: {result['grade_name']}, 专业班级: {result['class_name']}")
        print(f"处分ID: {result['punishment_id']}, 处分类型: {result['punishment_type']}")
    else:
        print("未找到添加的记录")
    
except Exception as e:
    conn.rollback()
    print(f"添加数据失败: {str(e)}")

# 关闭连接
conn.close()

print('\n操作完成。')