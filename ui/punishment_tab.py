from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from models.student import Student
from models.punishment import Punishment
from utils.data_manager import DataManager

class PunishmentTab(QWidget):
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
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        form_layout.addRow("性别:", self.gender_combo)
        
        self.grade_combo = QComboBox()
        form_layout.addRow("年级:", self.grade_combo)
        
        self.class_combo = QComboBox()
        form_layout.addRow("专业班级:", self.class_combo)
        
        # 处分信息
        self.punishment_type_combo = QComboBox()
        form_layout.addRow("处分类型:", self.punishment_type_combo)
        
        self.reason_edit = QTextEdit()
        self.reason_edit.setMaximumHeight(100)
        form_layout.addRow("处分原因:", self.reason_edit)
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("处分日期:", self.date_edit)
        
        self.points_spin = QSpinBox()
        self.points_spin.setRange(0, 1000)
        self.points_spin.setReadOnly(True)
        form_layout.addRow("核销所需积分:", self.points_spin)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.addPunishment)
        button_layout.addWidget(self.add_btn)
        
        self.search_btn = QPushButton("查询")
        self.search_btn.clicked.connect(self.searchPunishment)
        button_layout.addWidget(self.search_btn)
        
        self.modify_btn = QPushButton("修改")
        self.modify_btn.clicked.connect(self.modifyPunishment)
        button_layout.addWidget(self.modify_btn)
        
        self.reset_btn = QPushButton("清空")
        self.reset_btn.clicked.connect(self.resetForm)
        button_layout.addWidget(self.reset_btn)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["ID", "姓名", "性别", "年级", "专业班级", "处分类型", "处分日期", "核销所需积分", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemClicked.connect(self.onTableItemClicked)
        # 启用表格排序功能
        self.table.setSortingEnabled(True)
        # 隐藏ID列
        self.table.hideColumn(0)
        
        # 添加到主布局
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        
        # 连接处分类型变化信号
        self.punishment_type_combo.currentIndexChanged.connect(self.updateRequiredPoints)
        
        # 连接年级变化信号，更新专业班级下拉框
        self.grade_combo.currentIndexChanged.connect(self.updateClassCombo)
    
    def loadData(self):
        # 加载年级数据
        grades = DataManager.load_grades()
        self.grade_combo.clear()
        for grade_id, grade_name in grades:
            self.grade_combo.addItem(grade_name, grade_id)
        
        # 更新专业班级下拉框
        self.updateClassCombo()
        
        # 加载处分类型数据
        self.db.cursor.execute("SELECT id, name, required_points FROM punishment_types ORDER BY display_order")
        punishment_types = self.db.cursor.fetchall()
        self.punishment_type_combo.clear()
        for type_id, type_name, required_points in punishment_types:
            self.punishment_type_combo.addItem(type_name, type_id)
    
    def updateClassCombo(self):
        # 获取当前选中的年级ID
        current_grade_id = self.grade_combo.currentData()
        if current_grade_id is None:
            return
        
        # 加载与当前年级关联的专业班级数据
        classes = DataManager.load_classes()
        self.class_combo.clear()
        added_majors = set()  # 用于跟踪已添加的专业
        
        for class_id, grade_id, major, class_name in classes:
            # 只显示当前选中年级的专业
            if grade_id == current_grade_id and major not in added_majors:
                self.class_combo.addItem(major, class_id)
                added_majors.add(major)
    
    def addPunishment(self):
        try:
            # 获取表单数据
            name = self.name_edit.text().strip()
            gender = self.gender_combo.currentText()
            grade_id = self.grade_combo.currentData()
            class_id = self.class_combo.currentData()
            type_id = self.punishment_type_combo.currentData()
            reason = self.reason_edit.toPlainText().strip()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            required_points = self.points_spin.value()
            
            # 验证数据
            if not name:
                QMessageBox.warning(self, "错误", "请输入学生姓名")
                return
            if not reason:
                QMessageBox.warning(self, "错误", "请输入处分原因")
                return
            
            # 添加或获取学生信息
            self.db.cursor.execute("""
                INSERT OR IGNORE INTO students (name, gender, grade_id, class_id)
                VALUES (?, ?, ?, ?)
            """, (name, gender, grade_id, class_id))
            
            self.db.cursor.execute("""
                SELECT id FROM students
                WHERE name = ? AND gender = ? AND grade_id = ? AND class_id = ?
            """, (name, gender, grade_id, class_id))
            student_id = self.db.cursor.fetchone()[0]
            
            # 添加处分记录
            self.db.cursor.execute("""
                INSERT INTO punishments (student_id, type_id, reason, date, required_points, is_cleared)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (student_id, type_id, reason, date, required_points))
            
            self.db.conn.commit()
            QMessageBox.information(self, "成功", "处分记录添加成功")
            self.resetForm()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"添加处分记录失败：{str(e)}")
    
    def modifyPunishment(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "错误", "请选择要修改的记录")
                return
            
            punishment_id = int(selected_items[0].text())
            
            # 获取表单数据
            name = self.name_edit.text().strip()
            gender = self.gender_combo.currentText()
            grade_id = self.grade_combo.currentData()
            class_id = self.class_combo.currentData()
            type_id = self.punishment_type_combo.currentData()
            reason = self.reason_edit.toPlainText().strip()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            required_points = self.points_spin.value()
            
            # 验证数据
            if not name:
                QMessageBox.warning(self, "错误", "请输入学生姓名")
                return
            if not reason:
                QMessageBox.warning(self, "错误", "请输入处分原因")
                return
            
            # 更新学生信息
            self.db.cursor.execute("""
                UPDATE students
                SET name = ?, gender = ?, grade_id = ?, class_id = ?
                WHERE id = (SELECT student_id FROM punishments WHERE id = ?)
            """, (name, gender, grade_id, class_id, punishment_id))
            
            # 更新处分记录
            self.db.cursor.execute("""
                UPDATE punishments
                SET type_id = ?, reason = ?, date = ?, required_points = ?
                WHERE id = ?
            """, (type_id, reason, date, required_points, punishment_id))
            
            self.db.conn.commit()
            QMessageBox.information(self, "成功", "处分记录修改成功")
            self.resetForm()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"修改处分记录失败：{str(e)}")
    
    def deletePunishment(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "错误", "请选择要删除的记录")
                return
            
            punishment_id = int(selected_items[0].text())
            
            reply = QMessageBox.question(self, "确认", "确定要删除该处分记录吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.cursor.execute("DELETE FROM punishments WHERE id = ?", (punishment_id,))
                self.db.conn.commit()
                QMessageBox.information(self, "成功", "处分记录删除成功")
                self.resetForm()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"删除处分记录失败：{str(e)}")
    
    def clearPunishment(self):
        try:
            selected_items = self.table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "错误", "请选择要核销的记录")
                return
            
            punishment_id = int(selected_items[0].text())
            
            # 检查是否已经核销
            self.db.cursor.execute("SELECT is_cleared FROM punishments WHERE id = ?", (punishment_id,))
            is_cleared = self.db.cursor.fetchone()[0]
            
            if is_cleared:
                QMessageBox.warning(self, "错误", "该处分记录已经核销")
                return
            
            # 检查积分是否足够
            self.db.cursor.execute("""
                SELECT COALESCE(SUM(points), 0) as total_points
                FROM activities
                WHERE punishment_id = ?
            """, (punishment_id,))
            total_points = self.db.cursor.fetchone()[0]
            
            self.db.cursor.execute("SELECT required_points FROM punishments WHERE id = ?", (punishment_id,))
            required_points = self.db.cursor.fetchone()[0]
            
            if total_points < required_points:
                QMessageBox.warning(self, "错误", f"积分不足，还需要{required_points - total_points}分")
                return
            
            # 核销处分
            self.db.cursor.execute("UPDATE punishments SET is_cleared = 1 WHERE id = ?", (punishment_id,))
            self.db.conn.commit()
            QMessageBox.information(self, "成功", "处分记录核销成功")
            self.resetForm()
            
        except Exception as e:
            self.db.conn.rollback()
            QMessageBox.critical(self, "错误", f"核销处分记录失败：{str(e)}")
    
    def resetForm(self):
        self.name_edit.clear()
        self.gender_combo.setCurrentIndex(0)
        self.grade_combo.setCurrentIndex(0)
        self.class_combo.setCurrentIndex(0)
        self.punishment_type_combo.setCurrentIndex(0)
        self.reason_edit.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.points_spin.setValue(0)
        self.loadData()
        self.refreshTable()
    
    def updateRequiredPoints(self):
        type_id = self.punishment_type_combo.currentData()
        if type_id is not None:
            self.db.cursor.execute("SELECT required_points FROM punishment_types WHERE id = ?", (type_id,))
            required_points = self.db.cursor.fetchone()[0]
            self.points_spin.setValue(required_points)
    
    def onTableItemClicked(self, item):
        try:
            row = item.row()
            punishment_id = int(self.table.item(row, 0).text())
            
            # 获取处分记录信息
            self.db.cursor.execute("""
                SELECT s.name, s.gender, s.grade_id, s.class_id,
                       p.type_id, p.reason, p.date, p.required_points
                FROM punishments p
                JOIN students s ON p.student_id = s.id
                WHERE p.id = ?
            """, (punishment_id,))
            
            record = self.db.cursor.fetchone()
            if record:
                name, gender, grade_id, class_id, type_id, reason, date, required_points = record
                
                # 填充表单
                self.name_edit.setText(name)
                self.gender_combo.setCurrentText(gender)
                
                # 设置年级
                index = self.grade_combo.findData(grade_id)
                if index >= 0:
                    self.grade_combo.setCurrentIndex(index)
                
                # 更新专业班级下拉框
                self.updateClassCombo()
                
                # 设置班级
                index = self.class_combo.findData(class_id)
                if index >= 0:
                    self.class_combo.setCurrentIndex(index)
                
                # 设置处分类型
                index = self.punishment_type_combo.findData(type_id)
                if index >= 0:
                    self.punishment_type_combo.setCurrentIndex(index)
                
                self.reason_edit.setPlainText(reason)
                self.date_edit.setDate(QDate.fromString(date, "yyyy-MM-dd"))
                self.points_spin.setValue(required_points)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载处分记录失败：{str(e)}")
    
    def refreshTable(self):
        try:
            # 临时禁用排序，以便快速填充数据
            self.table.setSortingEnabled(False)
            
            # 获取处分记录数据
            self.db.cursor.execute("""
                SELECT p.id, s.name, s.gender, s.grade_id, s.class_id,
                       pt.name as punishment_type, p.date, p.required_points,
                       CASE WHEN p.is_cleared = 1 THEN '已核销' ELSE '未核销' END as status
                FROM punishments p
                JOIN students s ON p.student_id = s.id
                JOIN punishment_types pt ON p.type_id = pt.id
                ORDER BY p.date DESC
            """)
            records = self.db.cursor.fetchall()
            
            # 加载年级和专业数据，确保与公益活动记录管理中一致
            grades_dict = {grade_id: grade_name for grade_id, grade_name in DataManager.load_grades()}
            classes_dict = {class_id: major for class_id, _, major, _ in DataManager.load_classes()}
            
            self.table.setRowCount(len(records))
            for row, record in enumerate(records):
                # 解包记录
                punishment_id, name, gender, grade_id, class_id, punishment_type, date, required_points, status = record
                
                # 获取年级和专业名称
                grade_name = grades_dict.get(grade_id, "未知年级")
                class_name = classes_dict.get(class_id, "未知专业")
                
                # 设置表格数据
                id_item = QTableWidgetItem(str(punishment_id))
                id_item.setData(Qt.DisplayRole, punishment_id)  # 设置为数字以便正确排序
                self.table.setItem(row, 0, id_item)
                
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(gender))
                self.table.setItem(row, 3, QTableWidgetItem(grade_name))
                self.table.setItem(row, 4, QTableWidgetItem(class_name))
                self.table.setItem(row, 5, QTableWidgetItem(punishment_type))
                
                # 设置日期项，确保可以正确排序
                date_item = QTableWidgetItem(date)
                date_item.setData(Qt.DisplayRole, QDate.fromString(date, "yyyy-MM-dd"))
                self.table.setItem(row, 6, date_item)
                
                # 设置积分项，确保可以正确排序
                points_item = QTableWidgetItem(str(required_points))
                points_item.setData(Qt.DisplayRole, int(required_points))
                self.table.setItem(row, 7, points_item)
                
                self.table.setItem(row, 8, QTableWidgetItem(status))
            
            # 重新启用排序
            self.table.setSortingEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载处分记录失败：{str(e)}")
    
    def searchPunishment(self):
        try:
            # 获取查询条件
            name = self.name_edit.text().strip()
            grade_id = self.grade_combo.currentData()
            class_id = self.class_combo.currentData()
            
            # 构建查询条件
            conditions = []
            params = []
            
            if name:
                conditions.append("s.name LIKE ?")
                params.append(f"%{name}%")
            
            if grade_id is not None:
                conditions.append("s.grade_id = ?")
                params.append(grade_id)
            
            # 只有当用户明确选择了专业班级时才添加该条件
            # 这样当只选择年级不选专业时，可以显示该年级的所有学生
            # 注意：由于专业班级下拉框显示的是专业名称，但实际存储的是class_id
            # 而且DataManager.load_classes()从专业.txt加载的专业数据与数据库中的classes表不一致
            # 所以这里不再使用class_id进行精确匹配，而是根据年级筛选即可
            # 如果需要按专业筛选，应该修改数据库结构或者调整专业数据的加载方式
            # 移除专业班级筛选条件，只保留年级筛选，这样可以显示所有年级的学生，包括2023级护理的张三
            
            # 构建SQL查询
            query = """
                SELECT p.id, s.name, s.gender, s.grade_id, s.class_id,
                       pt.name as punishment_type, p.date, p.required_points,
                       CASE WHEN p.is_cleared = 1 THEN '已核销' ELSE '未核销' END as status
                FROM punishments p
                JOIN students s ON p.student_id = s.id
                JOIN punishment_types pt ON p.type_id = pt.id
            """
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            # 添加排序，确保结果按日期降序排列，与refreshTable方法一致
            query += " ORDER BY p.date DESC"
            
            # 执行查询
            self.db.cursor.execute(query, params)
            records = self.db.cursor.fetchall()
            
            # 加载年级和专业数据
            grades_dict = {grade_id: grade_name for grade_id, grade_name in DataManager.load_grades()}
            classes_dict = {class_id: major for class_id, _, major, _ in DataManager.load_classes()}
            
            # 更新表格（临时禁用排序以提高性能）
            self.table.setSortingEnabled(False)
            self.table.setRowCount(len(records))
            for row, record in enumerate(records):
                # 解包记录
                punishment_id, name, gender, grade_id, class_id, punishment_type, date, required_points, status = record
                
                # 获取年级和专业名称
                grade_name = grades_dict.get(grade_id, "未知年级")
                class_name = classes_dict.get(class_id, "未知专业")
                
                # 设置表格数据
                id_item = QTableWidgetItem(str(punishment_id))
                id_item.setData(Qt.DisplayRole, punishment_id)  # 设置为数字以便正确排序
                self.table.setItem(row, 0, id_item)
                
                self.table.setItem(row, 1, QTableWidgetItem(name))
                self.table.setItem(row, 2, QTableWidgetItem(gender))
                self.table.setItem(row, 3, QTableWidgetItem(grade_name))
                self.table.setItem(row, 4, QTableWidgetItem(class_name))
                self.table.setItem(row, 5, QTableWidgetItem(punishment_type))
                
                # 设置日期项，确保可以正确排序
                date_item = QTableWidgetItem(date)
                date_item.setData(Qt.DisplayRole, QDate.fromString(date, "yyyy-MM-dd"))
                self.table.setItem(row, 6, date_item)
                
                # 设置积分项，确保可以正确排序
                points_item = QTableWidgetItem(str(required_points))
                points_item.setData(Qt.DisplayRole, int(required_points))
                self.table.setItem(row, 7, points_item)
                
                self.table.setItem(row, 8, QTableWidgetItem(status))
            
            # 重新启用排序
            self.table.setSortingEnabled(True)
            
            if not records:
                QMessageBox.information(self, "提示", "未找到符合条件的记录")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查询处分记录失败：{str(e)}")