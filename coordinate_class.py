# coordinate class
class Coordinate:
    def __init__(self, x, y, dx, dy):
        self.__x = x
        self.__y = y
        self.__dx = dx
        self.__dy = dy

    # setters and getters for x,y,dx,dy
    def set_x(self, x):
        self.__x = x

    def set_y(self, y):
        self.__y = y

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def set_dx(self, x):
        self.__dx = x

    def set_dy(self, y):
        self.__dy = y

    def get_dx(self):
        return self.__dx

    def get_dy(self):
        return self.__dy

