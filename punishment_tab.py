from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate
from models.student import Student
from models.punishment import Punishment

class PunishmentTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.loadData()
    
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
        
        self.modify_btn = QPushButton("修改")
        self.modify_btn.clicked.connect(self.modifyPunishment)
        button_layout.addWidget(self.modify_btn)
        
        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self.deletePunishment)
        button_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("核销")
        self.clear_btn.clicked.connect(self.clearPunishment)
        button_layout.addWidget(self.clear_btn)
        
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
        
        # 添加到主布局
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)
        
        # 连接处分类型变化信号
        self.punishment_type_combo.currentIndexChanged.connect(self.updateRequiredPoints)
    
    def loadData(self):
        # 加载年级数据
        self.db.cursor.execute("SELECT id, name FROM grades ORDER BY name")
        grades = self.db.cursor.fetchall()
        self.grade_combo.clear()
        for grade_id, grade_name in grades:
            self.grade_combo.addItem(grade_name, grade_id)
        
        # 加载专业班级数据
        self.db.cursor.execute("SELECT id, name FROM classes ORDER BY name")
        classes = self.db.cursor.fetchall()
        self.class_combo.clear()
        for class_id, class_name in classes:
            self.class_combo.addItem(class_name, class_id)
        
        # 加载处分类型数据
        self.db.cursor.