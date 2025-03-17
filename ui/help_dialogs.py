from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("帮助")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 帮助标签页
        help_widget = QWidget()
        help_layout = QVBoxLayout(help_widget)
        help_text = QLabel("""
        学生处分核销管理系统使用说明：
        
        
        1. 处分记录管理
           - 添加、修改和删除学生处分记录
           - 查看处分详细信息
           - 管理处分状态
        
        2. 公益活动记录
           - 记录学生参与的公益活动
           - 计算活动获得的积分
           - 查看活动历史记录
        
        3. 积分统计
           - 查看学生积分情况
           - 统计处分核销进度
           - 管理核销状态
        
        4. 核销规则
           - 不同类型处分需要不同的积分
           - 积分通过参与公益活动获得
           - 积分满足要求后可进行核销
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        # 关于标签页
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_text = QLabel("""
        学生处分核销管理系统 V1.0
                
        作者：奋 青
        邮箱：fzlfq@qq.com
        
        版权所有 © 2025
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setStyleSheet("QLabel { font-family: '微软雅黑'; font-size: 14px; color: #333333; line-height: 1.5; }")
        about_layout.addWidget(about_text)
        
        # 添加标签页
        tab_widget.addTab(help_widget, "帮助")
        tab_widget.addTab(about_widget, "关于")
        
        layout.addWidget(tab_widget)
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
    def closeEvent(self, event):
        self.close()
        event.accept()