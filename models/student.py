class Student:
    def __init__(self, id=None, name="", gender="", grade_id=None, class_id=None):
        self.id = id
        self.name = name
        self.gender = gender
        self.grade_id = grade_id
        self.class_id = class_id
        self.grade_name = ""
        self.class_name = ""