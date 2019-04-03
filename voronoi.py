import sys
import numpy as np
import matplotlib.tri
import time
import const

def get_delanay_circles_centers(triangles):
    """
    Takes an array of triangles in format where [[pt1], [pt2], [pt3]] is a triangles
    and returns an np.array of centers of circles circumscribed around given triangles.
    """
    points1, points2, points3 = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    # Vectors
    sides1 = points2 - points1
    sides2 = points3 - points1
    # Length of vector of cross product * 2
    area = 2 * (sides1[:, 0] * sides2[:, 1] - sides1[:, 1] * sides2[:, 0])

    # (y_2(x_1^2 + y_1^2) - y_1(x_2^2 + y_2^2)) / area + x
    centers_x = (sides2[:, 1] * (np.square(sides1[:, 0]) + np.square(sides1[:, 1])) -
                 sides1[:, 1] * (np.square(sides2[:, 0]) + np.square(sides2[:, 1]))) / area + points1[:, 0]
    centers_y = (sides1[:, 0]*(np.square(sides2[:, 0])+np.square(sides2[:, 1])) -
                 sides2[:, 0]*(np.square(sides1[:, 0])+np.square(sides1[:, 1])))/area + points1[:, 1]

    # Transportated.
    return np.array((centers_x, centers_y)).T


def check_inside(point, bbox):
    """
    Returns True if point is within a given bbox, False -- otherwise.
    """
    return bbox[0] < point[0] < bbox[2] and bbox[1] < point[1] < bbox[3]


def move_point(start, end, bbox):
    """
    Returns moved start point towards end that lies on bbox if it's possible, None -- otherwise.
    """
    vector = end - start
    shift = calculate_shift(start, vector, bbox)
    if shift is not None and 0 < shift < 1:
        start = start + shift * vector
        return start


def calculate_shift(point, vector, bbox):
    """
    Returns modifier, that point + vector * modifier == projected point on bbox if it's possible, None -- otherwise.
    """
    shift = sys.float_info.max

    # Dividing problem into 4 separate for each component of
    # bbox points and choosing the minimal modifier
    for i, comp in enumerate(bbox):
        modifier = (float(comp) - point[i % 2]) / vector[i % 2]
        if modifier > 0:
            if abs(modifier) < abs(shift):
                shift = modifier
    return shift if shift < sys.float_info.max else None


def get_voronoi_polygons(input_pts, bbox=None):
    """
    Calculates Voronoi diagram using Delaunay triangulation (https://en.wikipedia.org/wiki/Delaunay_triangulation) function in matplotlib and using numpy for numerical calculations.
    """
    if not isinstance(input_pts, np.ndarray):
        input_pts = np.array(input_pts)

    if bbox == None:
        x_min = input_pts[:, 0].min()
        x_max = input_pts[:, 0].max()
        y_min = input_pts[:, 1].min()
        y_max = input_pts[:, 1].max()
        x_range = (x_max - x_min) * const.BBOX_MODIFIER
        y_range = (y_max - y_min) * const.BBOX_MODIFIER
        bbox = (x_min - x_range, y_min - y_range, x_max + x_range, y_max + y_range)

    # Constructing Delaunay triangulation, consisting of points and triangles.
    # (triangles are arrays of indexes of points)
    triangulation = matplotlib.tri.Triangulation(input_pts[:, 0], input_pts[:, 1])
    triangles = triangulation.triangles
    triangles_count = triangles.shape[0]

    # input_pts[triangles] = array of triangles: [[pt1], ..., ...] -- triangle.
    circle_centers = get_delanay_circles_centers(input_pts[triangles])

    segments = []
    for i in range(triangles_count):
        for j in range(3):
            neighbor = triangulation.neighbors[i][j]

            if neighbor != -1: # Trying to connect circle centers
                # Fitting centers to bbox.
                start, end = circle_centers[i], circle_centers[neighbor]

                if not check_inside(start, bbox):
                    start = move_point(start, end, bbox)
                    if start is None:
                        continue

                if not check_inside(end, bbox):
                    end = move_point(end, start, bbox)
                    if end is None:
                        continue

                segments.append([start, end])

            else: # Trying to create line leading to the bbox.
                # Ignore center outside of bbox
                if not check_inside(circle_centers[i], bbox):
                    continue

                first, second, third = input_pts[triangles[i, j]
                ], input_pts[triangles[i, (j+1) % 3]
                ], input_pts[triangles[i, (j+2) % 3]]
                # Looks horrendous but otherwise python thinks we are doing smth like 3 elem = 1 elem.

                edge = np.array([first, second])
                vector = np.array([[0, 1], [-1, 0]]).dot(edge[1] - edge[0])
                def line(pt):
                    return (pt[0] - first[0]) * (second[1] - first[1]) / (second[0] - first[0]) - pt[1] + first[1]
                orientation = np.sign(line(third)) * np.sign(line(first + vector))
                if orientation > 0:
                    vector = -orientation * vector
                shift = calculate_shift(circle_centers[i], vector, bbox)
                if shift is not None:
                    segments.append([circle_centers[i], circle_centers[i] + shift * vector])

    return segments
