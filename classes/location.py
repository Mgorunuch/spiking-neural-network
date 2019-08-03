class Location:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_caret(self):
        return (
            self.x,
            self.y,
            self.z,
        )