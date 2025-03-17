class Activity:
    def __init__(self, id=None, student_id=None, content="", date="", duration=0, points=0, punishment_id=None):
        self.id = id
        self.student_id = student_id
        self.content = content
        self.date = date
        self.duration = duration
        self.points = points
        self.punishment_id = punishment_id