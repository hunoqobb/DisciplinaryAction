from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QSpinBox, QDoubleSpinBox, QFileDialog)
from PyQt5.QtCore import Qt, QDate
import pandas as pd
import os
from utils.data_manager import DataManager

class ActivityTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.loadData()
        self.refreshTable()
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # 创建表单
        form_layout = QFormLayout()
        
        # 学生信息
        self.name_edit = QLineEdit()
        form_layout.addRow("姓名:", self.name_edit)
        
        # 添加性别下拉框
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        form_layout.addRow("性别:", self.gender_combo)
        
        self.grade_combo = QComboBox()
        form_layout.addRow("年级:", self.grade_combo)
        
        self.class_combo = QComboBox()
        form_layout.addRow("专业班级:", self.class_combo)
        
        # 活动信息
        self.activity_content = QTextEdit()
        self.activity_content.setMaximumHeight(100)
        form_layout.addRow("活动内容:", self.activity_content)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("活动日期:", self.date_edit)
        
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 24)
        self.duration_spin.setSingleStep(0.5)
        self.duration_spin.setDecimals(1)
        form_layout.addRow("活动时长(小时):", self.duration_spin)
        
        self.points_spin = QSpinBox()
        self.points_spin.setRange(0, 100)
        form_layout.addRow("获得积分:", self.points_spin)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.addActivity)
        button_layout.addWidget(self.add_btn)
        
        self.modify_btn = QPushButton("修改")
        self.modify_btn.clicked.connect(self.modifyActivity)
        button_layout.addWidget(self.modify_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.deleteActivity)
        button_layout.addWidget(self.delete_btn)
        
        self.reset_btn = QPushButton("清空")
        self.reset_btn.clicked.connect(self.resetForm)
        button_layout.addWidget(self.reset_btn)
        
        # 添加导出Excel按钮
        self.export_btn = QPushButton("导出Excel")
        self.export_btn.clicked.connect(self.exportToExcel)
        button_layout.addWidget(self.export_btn)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)  # 增加一列用于显示性别
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "年级", "专业班级", "活动内容", "活动日期", "活动时长", "获得积分"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemClicked.connect(self.onTableItemClicked)
        # 启用表格排序
        self.table.setSortingEnabled(True)
        # 隐藏ID列
        self.table.hideColumn(0)
        
        # 添加到主布局
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
    
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
    
    def refreshTable(self):
        try:
            # 临时禁用排序，以便快速填充数据
            self.table.setSortingEnabled(False)
            
            # 获取活动记录数据
            self.db.cursor.execute("""
                SELECT a.id, s.name, s.gender, s.grade_id, s.class_id, a.content, a.date, a.duration, a.points
                FROM activities a
                JOIN students s ON a.student_id = s.id
                ORDER BY a.date DESC
            """)
            records = self.db.cursor.fetchall()
            
            # 加载年级和专业数据，确保与处分记录管理中一致
            grades_dict = {grade_id: grade_name for grade_id, grade_name in DataManager.load_grades()}
            classes_dict = {class_id: major for class_id, _, major, _ in DataManager.load_classes()}
            
            self.table.setRowCount(len(records))
            for row, record in enumerate(records):
                # 解包记录
                activity_id, name, gender, grade_id, class_id, content, date, duration, points = record
                
                # 获取年级和专业名称
                grade_name = grades_dict.get(grade_id, "未知年级")
                class_name = classes_dict.get(class_id, "未知专业")
                
                # 设置表格数据
                id_item = QTableWidgetItem(str(activity_id))
                id_item.setData(Qt.DisplayRole, activity_id)  # 设置为数字以便正确排序
                self.table.setItem(row, 0, id_item)
                
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(gender))
                self.table.setItem(row, 3, QTableWidgetItem(grade_name))
                self.table.setItem(row, 4, QTableWidgetItem(class_name))
                self.table.setItem(row, 5, QTableWidgetItem(content))
                
                # 设置日期项，确保可以正确排序
                date_item = QTableWidgetItem()
                date_item.setData(Qt.DisplayRole, QDate.fromString(date, "yyyy-MM-dd"))
                self.table.setItem(row, 6, date_item)
                
                # 设置数值项，确保可以正确排序
                duration_item = QTableWidgetItem()
                duration_item.setData(Qt.DisplayRole, float(duration))
                self.table.setItem(row, 7, duration_item)
                
                points_item = QTableWidgetItem()
                points_item.setData(Qt.DisplayRole, int(points))
                self.table.setItem(row, 8, points_item)
            
            # 重新启用排序
            self.table.setSortingEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载活动记录失败：{str(e)}")
    
    def exportToExcel(self):
        try:
            # 获取保存文件路径
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出Excel", os.path.expanduser("~/公益活动记录.xlsx"),
                "Excel文件 (*.xlsx);;所有文件 (*)"
            )
            
            if not file_path:
                return  # 用户取消了保存
            
            # 如果文件名没有.xlsx后缀，添加它
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # 创建数据框
            data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
                data.append(row_data)
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=[self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())])
            
            # 导出到Excel
            df.to_excel(file_path, index=False)
            
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出Excel失败：{str(e)}")
    
    def modifyActivity(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "错误", "请选择要修改的记录")
                return
            
            activity_id = int(self.table.item(selected_items[0].row(), 0).text())
            
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
            
            # 获取学生ID
            self.db.cursor.execute("""
                SELECT id FROM students
                WHERE name = ? AND gender = ? AND grade_id = ? AND class_id = ?
            """, (name, gender, grade_id, class_id))
            result = self.db.cursor.fetchone()
            
            if not result:
                QMessageBox.warning(self, "错误", "该学生不存在")
                return
            
            student_id = result[0]
            
            # 更新活动记录
            self.db.cursor.execute("""
                UPDATE activities
                SET student_id = ?, content = ?, date = ?, duration = ?, points = ?
                WHERE id = ?
            """, (student_id, content, date, duration, points, activity_id))
            
            self.db.conn.commit()
            QMessageBox.information(self, "成功", "活动记录修改成功")
            self.resetForm()
            self.refreshTable()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"修改活动记录失败：{str(e)}")
    
    def deleteActivity(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "错误", "请选择要删除的记录")
                return
            
            activity_id = int(self.table.item(selected_items[0].row(), 0).text())
            
            # 确认删除
            reply = QMessageBox.question(self, "确认", "确定要删除选中的活动记录吗？",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
            
            # 删除活动记录
            self.db.cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
            
            self.db.conn.commit()
            QMessageBox.information(self, "成功", "活动记录删除成功")
            self.resetForm()
            self.refreshTable()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"删除活动记录失败：{str(e)}")
    
    def resetForm(self):
        # 清空表单
        self.name_edit.clear()
        self.gender_combo.setCurrentIndex(0)
        self.grade_combo.setCurrentIndex(0) if self.grade_combo.count() > 0 else None
        self.class_combo.setCurrentIndex(0) if self.class_combo.count() > 0 else None
        self.activity_content.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.duration_spin.setValue(0)
        self.points_spin.setValue(0)
    
    def onTableItemClicked(self, item):
        # 获取选中行的数据
        row = item.row()
        activity_id = int(self.table.item(row, 0).text())
        
        # 查询活动记录详细信息
        self.db.cursor.execute("""
            SELECT s.name, s.gender, s.grade_id, s.class_id, a.content, a.date, a.duration, a.points
            FROM activities a
            JOIN students s ON a.student_id = s.id
            WHERE a.id = ?
        """, (activity_id,))
        record = self.db.cursor.fetchone()
        
        if record:
            # 解包记录
            name, gender, grade_id, class_id, content, date, duration, points = record
            
            # 填充表单
            self.name_edit.setText(name)
            self.gender_combo.setCurrentText(gender)
            
            # 设置年级
            index = self.grade_combo.findData(grade_id)
            if index >= 0:
                self.grade_combo.setCurrentIndex(index)
            
            # 设置专业班级
            index = self.class_combo.findData(class_id)
            if index >= 0:
                self.class_combo.setCurrentIndex(index)
            
            self.activity_content.setText(content)
            self.date_edit.setDate(QDate.fromString(date, "yyyy-MM-dd"))
            self.duration_spin.setValue(float(duration))
            self.points_spin.setValue(int(points))