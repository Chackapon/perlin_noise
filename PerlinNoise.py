from PIL import Image
import numpy

# import EpixVector
import random
import math
import warnings

def Broken(f):
    def wrapper(*args):
        print("Function " + f.__name__ + "() is broken at the moment!")
    return wrapper

class Vector2D:
    def __init__(self, y, x):
        self.x = x
        self.y = y

    def size(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __mul__(self, other):
        if isinstance(other, Vector2D):
            return self.x * other.x + self.y * other.y
        else:
            raise NotImplementedError

def randomUnitaryVector():
    # angle = random.uniform(0, 2 * math.pi)
    # result = Vector2D(math.sin(angle), math.cos(angle))
    x = random.random()
    y = math.sqrt(1 - x**2)
    if random.random() > 0.5:
        x *= -1
    if random.random() > 0.5:
        y *= -1
    result = Vector2D(y,x)

    try:
        assert numpy.isclose(result.size(), 1)
    except NameError:
        print("WARNING: numpy not available, not checking the size of the generated unit vector")
    return result


def smoothstep(x: float) -> float:
    if x < 0: return 0
    if x > 1: return 1
    return (x**3) * (x * (6.0*x - 15.0) + 10.0)

class Perlin:

    GRID_HEIGHT = None
    GRID_WIDTH = None
    CELL_SIZE = None
    VECTOR_LIST = None
    OCTAVES = None
    DAMP = None

    def __init__(self, grid_height: int, grid_weight: int, octaves: int, damp: float, cell_size = 0):
        self.GRID_HEIGHT = grid_height
        self.GRID_WIDTH = grid_weight
        assert self.GRID_HEIGHT and self.GRID_WIDTH

        self.OCTAVES = octaves
        self.DAMP = damp
        assert self.OCTAVES >= 1 and 0 < self.DAMP < 1

        self.CELL_SIZE = cell_size
        self.VECTOR_LIST = None

    def setCellSize(self, cell_size: int):
        self.CELL_SIZE = cell_size

    def generateVectorGrid(self):
        VECTORS_HEIGHT = self.GRID_HEIGHT * 2 ** (self.OCTAVES - 1) + 1
        VECTORS_WIDTH = self.GRID_WIDTH * 2 ** (self.OCTAVES - 1) + 1
        self.VECTOR_LIST = [[randomUnitaryVector() for x in range(VECTORS_WIDTH)] for y in range(VECTORS_HEIGHT)]


    def perlinChunkValue(self, x, y, offset_x, offset_y, offset_octave):
        vector_x_index = offset_octave * (int(x) + offset_x)
        vector_y_index = offset_octave * (int(y) + offset_y)

        gradient_vector = self.VECTOR_LIST[vector_y_index][vector_x_index]

        relative_x = x - int(x) - offset_x
        relative_y = y - int(y) - offset_y
        pos_vector = Vector2D(relative_y, relative_x)

        perlin_value = gradient_vector * pos_vector
        return perlin_value

    def perlinSum(self, x: float, y: float, offset_octave):
        left_upper = self.perlinChunkValue(x, y, 0, 0, offset_octave)
        right_upper = self.perlinChunkValue(x, y, 1, 0, offset_octave)
        left_lower = self.perlinChunkValue(x, y, 0, 1, offset_octave)
        right_lower = self.perlinChunkValue(x, y, 1, 1, offset_octave)

        relative_x = x - int(x)
        relative_y = y - int(y)

        upper = left_upper + smoothstep(relative_x) * (right_upper - left_upper)
        lower = left_lower + smoothstep(relative_x) * (right_lower - left_lower)
        value = upper + smoothstep(relative_y) * (lower - upper)

        # linear interpolation
        # upper = (1-relative_x)*left_upper + relative_x*right_upper
        # lower = (1-relative_x)*left_lower + relative_x*right_lower
        # value = (1-relative_y)*upper + relative_y*lower
        return value

    def perlinValue(self, x: int, y: int):
        assert self.CELL_SIZE
        # musze znac size by wiedziec jak konwertowac wspolrzedne
        value = 0
        for i in range(1, self.OCTAVES + 1):
            size = self.CELL_SIZE / 2 ** (i - 1)
            value += self.perlinSum(x / size, y / size, 2 ** (self.OCTAVES - i)) * (self.DAMP ** (i - 1))
        return value

    def toImage(self) -> Image.Image:
        assert self.CELL_SIZE
        try:
            image = Image.new('L', (self.GRID_WIDTH * self.CELL_SIZE, self.GRID_HEIGHT * self.CELL_SIZE), "black")
            for y in range(self.GRID_HEIGHT * self.CELL_SIZE):
                for x in range(self.GRID_WIDTH * self.CELL_SIZE):
                    perlin_value = self.perlinValue(x, y)
                    perlin_color = int((perlin_value + 1) / 2 * 255)

                    image.putpixel((x, y), perlin_color)

            return image
        except NameError:
            print("PIL not available, image generation is not possible")
            return None

    @Broken
    def stepByStep(self, image):
        for self.OCTAVES in range(1, self.OCTAVES + 1):
            image = self.toImage()
            image.show()


@Broken
def drawVectors(grid_size, cell_size, vector_list, image, img):
    # vector_list = [[EpixVector.Vector2D(math.sqrt(2)/2, math.sqrt(2)/2) for i in range(GRID_WIDTH+1)] for j in range(GRID_SIZE+1)]
    # vector_list = VECTORS
    # img = grid(height, size, width)

    for i in range(len(vector_list) * len(vector_list[0])):
        origin_x = i % (grid_size+1)
        origin_y = i // (grid_size + 1)
        vector =  vector_list[origin_x][origin_y]

        for j in range(cell_size//2):
            draw_x = int(origin_x * cell_size + j * vector.x)
            draw_y = int(origin_y * cell_size + j * vector.y)

            if draw_x in range(0, img.size[0]) and draw_y in range(0, img.size[1]):
                image.putpixel((draw_x, draw_y), (255, 0, 0))

    return image


if __name__ == "__main__":

    GRID_SIZE = 9
    CELL_SIZE = 50
    OCTAVES = 1
    DAMP = 0.5

    perlin = Perlin(GRID_SIZE, GRID_SIZE, OCTAVES, DAMP)
    perlin.setCellSize(CELL_SIZE)

    for i in range(1):
        perlin.generateVectorGrid()
        # perlin.toImage().save("img/perlin_noise_"+str(i)+".png")
        perlin.toImage().show()
        print("img_v4/perlin_noise_"+str(i)+".png completed")

