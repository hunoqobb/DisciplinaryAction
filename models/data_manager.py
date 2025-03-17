class DataManager:
    @staticmethod
    def load_grades():
        """从年级.txt文件中加载年级数据"""
        grades = []
        try:
            with open('data/年级.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        grade_id = parts[0]
                        grade_name = parts[1]
                        grades.append((grade_id, grade_name))
                    elif len(parts) == 1:
                        # 如果只有一个值，则使用相同的值作为ID和名称
                        grade_name = parts[0]
                        grades.append((grade_name, grade_name))
        except FileNotFoundError:
            print("年级.txt文件不存在")
        except Exception as e:
            print(f"加载年级数据时出错：{str(e)}")
        return grades

    @staticmethod
    def load_classes():
        """从专业.txt文件中加载专业班级数据"""
        classes = []
        try:
            with open('data/专业.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >= 2:
                        major = parts[0]
                        class_name = parts[1]
                        # 使用专业名称作为ID
                        class_id = major
                        # 使用空字符串作为年级ID，因为专业不依赖于年级
                        grade_id = ''
                        classes.append((class_id, grade_id, major, class_name))
                    elif len(parts) == 1:
                        # 如果只有一个值，则使用该值作为专业名称
                        major = parts[0]
                        class_id = major
                        grade_id = ''
                        class_name = major
                        classes.append((class_id, grade_id, major, class_name))
        except FileNotFoundError:
            print("专业.txt文件不存在")
        except Exception as e:
            print(f"加载专业数据时出错：{str(e)}")
        return classes