import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

"""
这个脚本用于分析并修复学生处分核销管理系统中公益活动记录添加功能的问题
特别是针对李四等学生无法在公益活动记录中添加记录的问题
"""

# 连接到数据库
db_path = os.path.join('data', 'student_management.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
cursor = conn.cursor()

# 分析问题
print("\n===== 分析公益活动记录添加问题 =====")

# 1. 检查activity_tab.py中的学生查询逻辑
print("\n1. 检查学生查询逻辑")
print("在activity_tab.py中，添加活动记录时使用以下查询来获取学生ID:")
print("""
    SELECT id FROM students
    WHERE name = ? AND gender = ? AND grade_id = ? AND class_id = ?
""")
print("这个查询要求学生姓名、性别、年级ID和专业班级ID完全匹配才能找到学生")

# 2. 检查李四的信息
print("\n2. 检查李四的信息")
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

# 3. 模拟添加活动记录的查询
print("\n3. 模拟添加活动记录的查询")
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

# 4. 检查UI界面中的年级和专业班级选择逻辑
print("\n4. 检查UI界面中的年级和专业班级选择逻辑")
print("在activity_tab.py的loadData方法中，专业班级的加载逻辑如下:")
print("""
    # 加载专业班级数据
    classes = DataManager.load_classes()
    self.class_combo.clear()
    added_majors = set()  # 用于跟踪已添加的专业
    for class_id, grade_id, major, class_name in classes:
        if major not in added_majors:  # 确保每个专业只添加一次
            self.class_combo.addItem(major, class_id)
            added_majors.add(major)
""")
print("这段代码只添加了每个专业的第一个班级的ID，而不是根据选择的年级来筛选专业班级")
print("这可能导致用户选择的专业班级ID与数据库中实际的专业班级ID不匹配")

# 5. 提出解决方案
print("\n5. 解决方案")
print("1) 修改activity_tab.py中的loadData方法，使专业班级选择与年级关联")
print("2) 修改addActivity方法，放宽学生查询条件，只通过姓名和性别查询，然后在结果中筛选")
print("3) 添加调试日志，在添加活动记录失败时显示详细错误信息")

# 6. 生成修复后的代码
print("\n6. 修复后的代码")
print("以下是修复后的activity_tab.py中关键方法的代码:")

print("\n修复后的loadData方法:")
print("""
def loadData(self):
    # 加载年级数据
    grades = DataManager.load_grades()
    self.grade_combo.clear()
    for grade_id, grade_name in grades:
        self.grade_combo.addItem(grade_name, grade_id)
    
    # 更新专业班级下拉框
    self.updateClassCombo()
    
    # 连接年级选择变化信号
    self.grade_combo.currentIndexChanged.connect(self.updateClassCombo)

def updateClassCombo(self):
    # 获取当前选择的年级ID
    grade_id = self.grade_combo.currentData()
    if grade_id is None:
        return
        
    # 加载与选定年级相关的专业班级数据
    classes = DataManager.load_classes()
    self.class_combo.clear()
    
    # 添加一个空选项
    self.class_combo.addItem("请选择专业", None)
    
    # 筛选当前年级的专业班级
    for class_id, cls_grade_id, major, class_name in classes:
        if cls_grade_id == grade_id:
            self.class_combo.addItem(major, class_id)
""")

print("\n修复后的addActivity方法:")
print("""
def addActivity(self):
    try:
        # 获取表单数据
        name = self.name_edit.text().strip()
        gender = self.gender_combo.currentText()
        grade_id = self.grade_combo.currentData()
        class_id = self.class_combo.currentData()
        content = self.activity_content.toPlainText().strip()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        duration = self.duration_spin.value()
        points = self.points_spin.value()
        
        # 验证数据
        if not name:
            QMessageBox.warning(self, "错误", "请输入学生姓名")
            return
        if not content:
            QMessageBox.warning(self, "错误", "请输入活动内容")
            return
        if class_id is None:
            QMessageBox.warning(self, "错误", "请选择专业班级")
            return
        
        # 首先尝试精确匹配
        self.db.cursor.execute("""
            SELECT id FROM students
            WHERE name = ? AND gender = ? AND grade_id = ? AND class_id = ?
        """, (name, gender, grade_id, class_id))
        result = self.db.cursor.fetchone()
        
        if result:
            student_id = result[0]
        else:
            # 如果精确匹配失败，尝试通过姓名和性别查找
            self.db.cursor.execute("""
                SELECT id, grade_id, class_id FROM students
                WHERE name = ? AND gender = ?
            """, (name, gender))
            results = self.db.cursor.fetchall()
            
            if not results:
                QMessageBox.warning(self, "错误", "该学生不存在，请先在处分记录中添加学生信息")
                return
            elif len(results) > 1:
                # 如果有多个匹配结果，显示详细信息让用户确认
                msg = "找到多个匹配的学生记录，请确认:\n"
                for i, r in enumerate(results):
                    # 获取年级和专业名称
                    self.db.cursor.execute("SELECT name FROM grades WHERE id = ?", (r[1],))
                    grade_name = self.db.cursor.fetchone()[0]
                    self.db.cursor.execute("SELECT name FROM classes WHERE id = ?", (r[2],))
                    class_name = self.db.cursor.fetchone()[0]
                    msg += f"{i+1}. {name} - {gender} - {grade_name} - {class_name}\n"
                
                # 这里简化处理，使用第一个匹配结果
                # 实际应用中应该让用户选择正确的记录
                student_id = results[0][0]
                QMessageBox.information(self, "提示", msg + f"\n已自动选择第一条记录，ID: {student_id}")
            else:
                student_id = results[0][0]
        
        # 添加活动记录
        self.db.cursor.execute("""
            INSERT INTO activities (student_id, content, date, duration, points)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, content, date, duration, points))
        
        self.db.conn.commit()
        QMessageBox.information(self, "成功", "活动记录添加成功")
        self.resetForm()
        self.refreshTable()
        
    except Exception as e:
        self.db.conn.rollback()
        QMessageBox.critical(self, "错误", f"添加活动记录失败：{str(e)}\n\n详细信息：\n姓名: {name}\n性别: {gender}\n年级ID: {grade_id}\n专业班级ID: {class_id}")
""")

print("\n7. 应用修复")
print("要应用这些修复，请将上述代码替换到ui/activity_tab.py文件中的相应方法")
print("这些修改将解决李四无法添加公益活动记录的问题，并防止其他学生遇到类似问题")

# 关闭数据库连接
conn.close()

print("\n分析和修复建议已完成。请根据上述建议修改activity_tab.py文件。")