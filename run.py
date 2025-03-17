import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from main_window import MainWindow
from database import Database

def main():
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置数据库路径
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "student_management.db")
    
    # 初始化数据库连接
    db = Database(db_path)
    
    # 创建并显示主窗口
    window = MainWindow(db)
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()