import os

class DataManager:
    @staticmethod
    def load_grades():
        """从文本文件加载年级数据"""
        grades = []
        try:
            grade_file = os.path.join('data', '年级.txt')
            with open(grade_file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines(), 1):
                    grade_name = line.strip()
                    if grade_name:
                        grades.append((i, grade_name))
        except Exception as e:
            print(f"加载年级数据失败：{str(e)}")
        return grades

    @staticmethod
    def load_classes():
        """从文本文件加载专业班级数据"""
        classes = []
        try:
            # 加载专业班级数据
            major_file = os.path.join('data', '专业.txt')
            with open(major_file, 'r', encoding='utf-8') as f:
                class_id = 1
                # 获取所有年级
                grades = DataManager.load_grades()
                grade_ids = [grade_id for grade_id, _ in grades]
                
                for line in f.readlines():
                    major = line.strip()
                    if major:
                        # 为每个专业创建与所有年级的关联
                        for grade_id in grade_ids:
                            class_name = f"{major}"
                            classes.append((class_id, grade_id, major, class_name))
                            class_id += 1
                    
        except Exception as e:
            print(f"加载专业班级数据失败：{str(e)}")
        return classes