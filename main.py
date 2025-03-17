import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QDesktopWidget
from ui.punishment_tab import PunishmentTab
from utils.data_manager import DataManager
from database import Database

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('学生处分核销管理系统')
        self.resize(1000, 800)
        
        # 将窗口移动到屏幕中央
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # 初始化数据库
        self.db = Database('data/student_management.db')
        self.db.conn.row_factory = sqlite3.Row
        
        # 添加处分管理标签页
        self.punishment_tab = PunishmentTab(self.db)
        self.tabs.addTab(self.punishment_tab, '处分管理')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()