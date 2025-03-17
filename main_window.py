from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QDesktopWidget, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor
from PyQt5.QtCore import Qt, QTimer, QLocale
import win32api, win32con, win32gui

from ui.punishment_tab import PunishmentTab
from ui.activity_tab import ActivityTab
from ui.statistics_tab import StatisticsTab

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标志，移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("帮助")
        self.setGeometry(200, 200, 400, 300)
        
        # 将对话框移动到屏幕中央
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move(int((screen.width() - window.width()) / 2),
                 int((screen.height() - window.height()) / 2))
        
        layout = QVBoxLayout()
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 帮助标签页
        help_tab = QWidget()
        help_layout = QVBoxLayout(help_tab)
        help_text = QLabel("""
        系统使用说明：

        1. 处分记录管理：用于管理学生处分信息
           - 添加、修改、删除学生处分记录
           - 查看处分记录详情
           - 处分核销管理
        
        2. 公益活动记录：记录学生参与的公益活动
           - 添加、修改、删除公益活动记录
           - 记录活动时长和获得的积分
        
        3. 积分统计：统计学生的核销积分情况
           - 查看学生积分统计
           - 处分核销进度跟踪
           - 双击记录查看详情
        """)
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        # 关于标签页
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        about_text = QLabel("""
        学生处分核销管理系统 V1.0

        免责声明：
        1. 本软件为免费开源软件，仅供学习和参考使用。
        2. 使用者在使用本软件时需自行承担风险，作者不对使用本软件所导致的任何直接或间接损失负责。
        3. 本软件不提供任何形式的保证，包括但不限于适销性、特定用途适用性的默示保证。
        4. 使用者应自行负责数据的备份和安全，作者不对数据丢失或损坏承担责任。
        5. 作者保留对本软件进行更新、修改或终止的权利，且无需事先通知。
        6. 使用本软件即表示同意本免责声明的所有条款。
        
        作者：奋 青
        邮箱：fzlfq@qq.com
        
        版权所有 © 2025
        """)
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignLeft)
        about_text.setStyleSheet("font-size: 14px;")
        about_layout.addWidget(about_text)
        
        # 添加标签页
        tab_widget.addTab(help_tab, "帮助")
        tab_widget.addTab(about_tab, "关于")
        
        layout.addWidget(tab_widget)
        
        # 添加关闭按钮
        button_layout = QHBoxLayout()
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button, alignment=Qt.AlignRight)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        # 设置全局样式
        self.setStyleSheet("""
            QComboBox {
                padding: 3px;
                height: 20px;
            }
            QComboBox QAbstractItemView {
                padding: 3px;
                selection-background-color: #0078d7;
            }
            QComboBox::item {
                height: 20px;
                padding: 3px;
            }
            QLineEdit {
                padding: 3px;
                height: 20px;
            }
            QSpinBox {
                padding: 3px;
                height: 18px;
                border: 1px solid #c0c0c0;
                background: #ffffff;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px;
                border: none;
            }
            QDateEdit {
                padding: 3px;
                height: 18px;
                border: 1px solid #c0c0c0;
                background: #ffffff;
                min-width: 60px;
            }
            QDateEdit::up-button, QDateEdit::down-button {
                width: 16px;
                border: none;
            }
        """)
        # 设置窗口标志，移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("学生处分核销管理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 将窗口移动到屏幕中央
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move(int((screen.width() - window.width()) / 2),
                 int((screen.height() - window.height()) / 2))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题栏
        title_layout = QVBoxLayout()
        
        # 添加Logo和标题
        header_layout = QVBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("Logo")
        
        title_label = QLabel("学生处分核销管理系统")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        header_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(header_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.punishment_tab = PunishmentTab(self.db)
        self.activity_tab = ActivityTab(self.db)
        self.statistics_tab = StatisticsTab(self.db)
        
        self.tab_widget.addTab(self.punishment_tab, "处分记录管理")
        self.tab_widget.addTab(self.activity_tab, "公益活动记录")
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.onTabChanged)
        
        # 创建帮助按钮
        help_button = QPushButton("帮助")
        help_button.setFixedSize(40, 20)
        help_button.clicked.connect(self.show_help)
        
        # 创建退出按钮
        exit_button = QPushButton("退出")
        exit_button.setFixedSize(40, 20)
        exit_button.clicked.connect(self.close)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(help_button)
        button_layout.addWidget(exit_button)
        button_layout.setAlignment(Qt.AlignRight)
        
        # 添加积分统计标签页
        self.tab_widget.addTab(self.statistics_tab, "积分统计")
        
        # 将按钮布局添加到主布局
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.tab_widget)
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("logo.png"))
        
        # 设置初始焦点到姓名输入框
        self.tab_widget.setCurrentIndex(0)  # 确保处分记录管理标签页是当前页
        QTimer.singleShot(100, self.setInitialFocus)
    
    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec_()
    
    def closeEvent(self, event):
        # 关闭所有子窗口
        for child in self.findChildren(QDialog):
            child.close()
        # 确保在关闭主窗口时退出整个应用程序
        import sys
        sys.exit(0)
        
    def onTabChanged(self, index):
        # 当切换到积分统计标签页时，自动加载数据
        if index == 2:  # 积分统计标签页的索引是2
            self.statistics_tab.searchRecords()
    
    def setInitialFocus(self):
        # 设置焦点到姓名输入框
        self.punishment_tab.name_edit.setFocus()
        
        # 设置输入法为中文
        # 获取当前窗口句柄
        hwnd = self.winId().__int__()
        
        # 设置输入法为中文
        # 0x0804是中文（中国）的语言ID
        win32api.SendMessage(hwnd, win32con.WM_INPUTLANGCHANGEREQUEST, 0, 0x0804)