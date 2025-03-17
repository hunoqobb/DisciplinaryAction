import sqlite3

def clear_database():
    try:
        # 连接数据库
        conn = sqlite3.connect('data/student_management.db')
        cursor = conn.cursor()
        
        # 开始事务
        cursor.execute('BEGIN')
        
        # 删除处分记录
        cursor.execute('DELETE FROM punishments')
        
        # 删除公益活动记录
        cursor.execute('DELETE FROM activities')
        
        # 提交事务
        conn.commit()
        print('数据清理成功')
        
    except Exception as e:
        # 如果出现错误，回滚事务
        conn.rollback()
        print(f'错误：{e}')
        
    finally:
        # 关闭数据库连接
        cursor.close()
        conn.close()

if __name__ == '__main__':
    clear_database()