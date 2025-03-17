import os
import sqlite3

# 连接到数据库
db_path = os.path.join('data', 'student_management.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询2023级年级ID
cursor.execute("SELECT * FROM grades WHERE name LIKE '%2023%'")
grades = cursor.fetchall()
print('2023级年级:', grades)

# 查询幼教专业班级ID
cursor.execute("SELECT * FROM classes WHERE name LIKE '%幼教%'")
classes = cursor.fetchall()
print('幼教专业班级:', classes)

# 如果没有幼教专业，则添加一个幼教专业班级
if not classes:
    cursor.execute("INSERT INTO classes (name) VALUES (?)", ('幼教1班',))
    conn.commit()
    print('已添加幼教专业班级')
    
    # 重新查询班级，获取新添加的幼教班级ID
    cursor.execute("SELECT * FROM classes WHERE name='幼教1班'")
    classes = cursor.fetchall()
    print('幼教专业班级:', classes)

# 添加学生李四
if grades and classes:
    grade_id = grades[0][0]  # 获取2023级的ID
    class_id = classes[0][0]  # 获取幼教专业的ID
    
    # 使用INSERT OR IGNORE避免重复添加
    cursor.execute(
        "INSERT OR IGNORE INTO students (name, gender, grade_id, class_id) VALUES (?, ?, ?, ?)", 
        ('李四', '女', grade_id, class_id)
    )
    
    # 提交事务
    conn.commit()
    print('学生李四添加成功!')
    
    # 验证添加结果
    cursor.execute("SELECT * FROM students WHERE name='李四'")
    print('验证结果:', cursor.fetchall())
else:
    print('未找到对应的年级或专业班级')

# 关闭数据库连接
conn.close()

print('\n脚本执行完毕，请重新启动应用程序以使更改生效。')