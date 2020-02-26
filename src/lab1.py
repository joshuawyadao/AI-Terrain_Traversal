# Joshua Yadao
# Professor Jansen Orfan
# Introduction to Artificial Intelligence
# 18 October 2019

from PIL import Image
from queue import Queue
import sys
import math
import time

TERRAIN_IMAGE = ''
ELEVATION_FILE = ''
PATH_FILE = ''
SEASON = ''
OUTPUT_IMAGE_FILENAME = ''
IMAGE = Image.new('RGBA', (2, 2))
PIXELS = IMAGE.load()
ELEVATION = dict()
PATH_COLOR = (255, 0, 255, 255)
PATH_MULTI = {
    (248, 148, 18, 255):    1,      # open land
    (255, 192, 0, 255):     5,      # rough meadow
    (255, 255, 255, 255):   2,      # easy movement forest
    (2, 208, 60, 255):      3,      # slow run forest
    (2, 136, 40, 255):      4,      # walk forest
    (5, 73, 24, 255):       9,      # impassible vegetation
    (0, 0, 255, 255):       7,      # lake/swamp/marsh
    (71, 51, 3, 255):       1,      # paved road
    (0, 0, 0, 255):         1,      # footpath
    (205, 0, 101, 255):     10,     # out of bounds
    PATH_COLOR:             1,      # path taken
    (119, 136, 153, 255):   2,      # adjusted path (gray)
    (135, 206, 250, 255):   5,      # ice
    (160, 82, 45, 255):     4       # mud
}


def find_neighbors(current):
    """
    Find all neighboring pixels from the current one
    :param current: tuple point
    :return: all the valid neighbors
    """
    x, y = current
    neighbors = []
    if x != 0:
        neighbors.append((x - 1, y))
    if x != IMAGE.size[0] - 1:
        neighbors.append((x + 1, y))
    if y != 0:
        neighbors.append((x, y - 1))
    if y != IMAGE.size[1] - 1:
        neighbors.append((x, y + 1))
    if x != 0 and y != 0:
        neighbors.append((x - 1, y - 1))
    if x != 0 and y != IMAGE.size[1] - 1:
        neighbors.append((x - 1, y + 1))
    if x != IMAGE.size[0] - 1 and y != 0:
        neighbors.append((x + 1, y - 1))
    if x != IMAGE.size[0] - 1 and y != IMAGE.size[1] - 1:
        neighbors.append((x + 1, y + 1))
    return neighbors


def bfs(start, max_out, search_val, replace_val, elevation):
    """
    BFS for fall and spring search
    :param start: starting point
    :param max_out: max distance out from starting point
    :param search_val: desired colors to be selected
    :param replace_val: replaced color for selected color to switch
    :param elevation: elevation difference desired
    :return: every node that was replaced
    """
    global PIXELS, ELEVATION
    queue = Queue()
    queue.put([start])
    count = 0
    while not queue.empty():
        path = queue.get()
        pixel = path[-1]
        if count >= max_out * max_out:
            return path
        for child in find_neighbors(pixel):
            x, y = child
            if PIXELS[x, y] in search_val and ELEVATION[y][x] - ELEVATION[start[1]][start[0]] < elevation:
                PIXELS[x, y] = replace_val
                new_path = list(path)
                new_path.append(child)
                queue.put(new_path)
        count += 1


def find_pixels(search_val, neighbor_val):
    """
    Find all pixels where a chosen color surrounds the searched color
    :param search_val: color of pixel to be searched
    :param neighbor_val: color of surrounding pixel
    :return: every node found
    """
    global IMAGE, PIXELS
    width, height = IMAGE.size
    found = []
    for i in range(width):
        for j in range(height):
            if PIXELS[i, j] in search_val:
                neighbor = [PIXELS[child[0], child[1]] for child in find_neighbors((i, j))]
                if len(neighbor_val.intersection(neighbor)) != 0:
                    found.append((i, j))
    return found


def print_points(array):
    """
    Prints a 6x6 square above each specified point to visually represent where the points are
    :param array: the points on the IMAGE to show
    :return: nothing
    """
    global PIXELS, PATH_COLOR
    for pair in array:
        for i in range(pair[0] - 3, pair[0] + 3):
            for j in range(pair[1] - 3, pair[1] + 3):
                PIXELS[i, j] = PATH_COLOR


def print_path(array):
    """
    Print a bold line to visually represent where the generated path is
    :param array: the points in the path to draw
    :return: nothing
    """
    global PIXELS, PATH_COLOR
    for pair in array:
        neighbors = find_neighbors(pair)
        for child in neighbors:
            PIXELS[child[0], child[1]] = PATH_COLOR
        PIXELS[pair[0], pair[1]] = PATH_COLOR


def change_pixels(array, change_val):
    """
    Changes all the pixel's colors listed in the array to a color
    :param array: pixels whose color will be changed
    :param change_val: the RGBa value for the new color
    :return: nothing
    """
    global PIXELS
    for pair in array:
        PIXELS[pair[0], pair[1]] = change_val


def change_seasons():
    """
    Changes the IMAGE_FILE depending on the season specified by the user
    :return: the new Image
    """
    global SEASON, ELEVATION
    if SEASON == 'summer':
        return
    if SEASON == 'fall':
        pixels = find_pixels({(0, 0, 0, 255)}, {(255, 255, 255, 255)})  # find all black pixels near a white pixel
        change_pixels(pixels, (119, 136, 153, 255))
        return
    if SEASON == 'winter':
        search = {(2, 208, 60, 255), (248, 148, 18, 255), (255, 192, 0, 255), (255, 255, 255, 255), (2, 136, 40, 255),
                  (5, 73, 24, 255), (71, 51, 3, 255), (0, 0, 0, 255)}
        pixels = find_pixels({(0, 0, 255, 255)}, search)
        for pixel in pixels:
            bfs(pixel, 7, {(0, 0, 255, 255)}, (135, 206, 250, 255), sys.maxsize)
        return
    if SEASON == 'spring':
        search = {(2, 208, 60, 255), (248, 148, 18, 255), (255, 192, 0, 255), (255, 255, 255, 255), (2, 136, 40, 255),
                  (5, 73, 24, 255), (71, 51, 3, 255), (0, 0, 0, 255)}
        pixels = find_pixels(search, {(0, 0, 255, 255)})
        for pixel in pixels:
            bfs(pixel, 15, search, (160, 82, 45, 255), 5)
        return
    else:
        sys.exit("Season Must Be: ['spring', 'summer', 'fall', 'winter']")


def distance(current_x, current_y, goal_x, goal_y):
    """
    Calculate the distance between the current and goal point
    :param current_x: current x val
    :param current_y: current y val
    :param goal_x: goal x val
    :param goal_y: goal y val
    :return: the distance between current and goal point
    """
    x_dif = abs(goal_x - current_x) * 10.29
    y_dif = abs(goal_y - current_y) * 7.55
    return math.sqrt(math.pow(x_dif, 2) +
                     math.pow(y_dif, 2))


def heuristic(start_x, start_y, goal_x, goal_y):
    """
    Heuristic function to estimate distance from start to goal
    :param start_x: starting x val
    :param start_y: starting y val
    :param goal_x: goal x val
    :param goal_y: goal y val
    :return: the estimation
    """
    global PIXELS, ELEVATION
    weight = PATH_MULTI.get(PIXELS[start_x, start_y])
    return math.pow(weight, 2) * ELEVATION[start_y][start_x] * distance(start_x, start_y, goal_x, goal_y)


def reconstruct_path(came_from, current):
    """
    Recreate the path in order from start to finish,
        Print path found
    :param came_from: dictionary where the val is where the key came from
    :param current: tuple for current point
    :return: the path created
    """
    global PIXELS
    total_path = [current]
    while current in came_from.keys():
        current = came_from[current]
        total_path.insert(0, current)
    print_path(total_path)
    return total_path


def a_star(start, goal):
    """
    A* search algorithm implementation
    :param start: starting tuple: (start_x, start_y)
    :param goal: goal tuple: (goal_x, goal_y)
    :return: path between every point, or false
    """
    open_set = set()
    open_set.add(start)
    came_from = dict()
    g_score = dict()
    g_score[start] = 0
    closed_set = set()
    f_score = dict()
    f_score[start] = heuristic(start[0], start[1], goal[0], goal[1])

    while len(open_set) != 0:
        current = min(open_set, key=f_score.get)
        if current == goal:
            return reconstruct_path(came_from, current)
        open_set.remove(current)
        closed_set.add(current)
        for neighbor in find_neighbors(current):
            if neighbor in closed_set:
                continue
            tentative_gscore = g_score[current] + distance(current[0], current[1], neighbor[0], neighbor[1])
            if neighbor not in g_score or tentative_gscore < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_gscore
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor[0], neighbor[1], goal[0], goal[1])
                if neighbor not in open_set:
                    open_set.add(neighbor)
    return False


def main():
    start = time.time()
    if len(sys.argv) != 6:
        error_string = 'NOT ENOUGH ARGUMENTS!!!' \
                       '\nArguments must be:\n' \
                       '\t1: Terrain Image\n' \
                       '\t2: Elevation File\n' \
                       '\t3: Path File\n' \
                       '\t4: Season\n' \
                       '\t5: Output Image Filename\n'
        sys.exit(error_string)
    else:
        global TERRAIN_IMAGE, ELEVATION_FILE, PATH_FILE, SEASON, \
            OUTPUT_IMAGE_FILENAME, IMAGE, PIXELS, ELEVATION
        TERRAIN_IMAGE = sys.argv[1]
        ELEVATION_FILE = sys.argv[2]
        PATH_FILE = sys.argv[3]
        SEASON = sys.argv[4].lower()
        OUTPUT_IMAGE_FILENAME = sys.argv[5]

        print('lab1 running')
        print('Terrain Image:\t\t\t' + TERRAIN_IMAGE)
        print('Elevation File:\t\t\t' + ELEVATION_FILE)
        print('Path file:\t\t\t\t' + PATH_FILE)
        print('Season:\t\t\t\t\t' + SEASON)
        print('Output Image Filename:\t' + OUTPUT_IMAGE_FILENAME)

        with open(PATH_FILE, "r") as fp:
            content = fp.readlines()
            content = [x.strip().split() for x in content]
            content = [tuple(int(string) for string in inner) for inner in content]

        with open(ELEVATION_FILE, "r") as fp:
            ELEVATION = [line.split() for line in fp]
            ELEVATION = [[float(string) for string in inner] for inner in ELEVATION]

        IMAGE = Image.open(TERRAIN_IMAGE)
        PIXELS = IMAGE.load()
        change_seasons()

        prev = content[0]
        for count in range(1, len(content)):
            temp = time.time()
            current = content[count]
            print('finding path from: ' + str(prev) + ' to ' + str(current))
            path = a_star(prev, current)
            if not path:
                sys.exit("Could not find path")
            prev = current
            print('\telapsed time: ' + str(time.time() - temp))

        print_points(content)

        IMAGE.save(OUTPUT_IMAGE_FILENAME)
        fp.close()
        end = time.time()
        print("Runtime: " + str(end - start))


if __name__ == '__main__':
    main()
