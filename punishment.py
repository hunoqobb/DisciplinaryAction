class Punishment:
    def __init__(self, id=None, student_id=None, type_id=None, reason="", date="", required_points=0, is_cleared=0):
        self.id = id
        self.student_id = student_id
        self.type_id = type_id
        self.reason = reason
        self.date = date
        self.required_points = required_points
        self.is_cleared = is_cleared
        self.type_name = ""