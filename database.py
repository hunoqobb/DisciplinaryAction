import sqlite3
import os

class Database:
    def __init__(self, db_path):
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # 连接到数据库
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.create_tables()
            self.initialize_data()
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            raise
    
    def create_tables(self):
        try:
            # 创建年级表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            ''')
            
            # 创建专业班级表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            ''')
            
            # 创建学生表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                grade_id INTEGER,
                class_id INTEGER,
                FOREIGN KEY (grade_id) REFERENCES grades (id),
                FOREIGN KEY (class_id) REFERENCES classes (id)
            )
            ''')
            
            # 创建处分类型表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS punishment_types (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                required_points INTEGER NOT NULL,
                display_order INTEGER NOT NULL DEFAULT 0
            )
            ''')
            
            # 创建处分记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS punishments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                type_id INTEGER,
                reason TEXT,
                date TEXT,
                required_points INTEGER,
                is_cleared INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (type_id) REFERENCES punishment_types (id)
            )
            ''')
            
            # 创建公益活动记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                content TEXT,
                date TEXT,
                duration REAL,
                points INTEGER,
                punishment_id INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (punishment_id) REFERENCES punishments (id)
            )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"创建数据表失败: {str(e)}")
            self.conn.rollback()
            raise
    
    def initialize_data(self):
        try:
            # 初始化年级数据
            grades = ["2020级", "2021级", "2022级", "2023级"]
            for grade in grades:
                self.cursor.execute("INSERT OR IGNORE INTO grades (name) VALUES (?)", (grade,))
            
            # 初始化专业班级数据
            classes = ["计算机科学与技术1班", "计算机科学与技术2班", 
                      "软件工程1班", "软件工程2班",
                      "人工智能1班", "人工智能2班",
                      "数据科学与大数据技术1班", "数据科学与大数据技术2班"]
            for cls in classes:
                self.cursor.execute("INSERT OR IGNORE INTO classes (name) VALUES (?)", (cls,))
            
            # 初始化处分类型数据
            punishment_types = [
                ("警告", 20),
                ("严重警告", 40),
                ("记过", 60),
                ("留校察看一学期", 80),
                ("留校察看一学年", 100),
                ("留校察看两学年", 120),
                ("开除学籍", 0)  # 开除学籍不需要核销
            ]
            for i, (name, points) in enumerate(punishment_types):
                self.cursor.execute("INSERT OR IGNORE INTO punishment_types (name, required_points, display_order) VALUES (?, ?, ?)", 
                                   (name, points, i))
            
            self.conn.commit()
        except Exception as e:
            print(f"初始化数据失败: {str(e)}")
            self.conn.rollback()
            raise
    
    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            print(f"关闭数据库连接失败: {str(e)}")
            raise