from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import numpy as np
import sys
import math


def get_bounding_box(trace):
    x = []
    y = []
    for p in trace:
        x.append(p[0])
        y.append(p[1])
    xmin = min(x)
    xmax = max(x)
    ymin = min(y)
    ymax = max(y)
    return [xmin, xmax, ymin, ymax]


def get_bounding_box_center(trace):
    xs = []
    ys = []
    for couple in trace:
        xs.append(couple[0])
        ys.append(couple[1])
    xmax = max(xs)
    xmin = min(xs)
    ymax = max(ys)
    ymin = min(ys)
    bounding_box_c = [(xmax + xmin) / 2, (ymax + ymin) / 2]
    return bounding_box_c


def get_convex_hull(trace):
    x = np.array(trace)
    hull = ConvexHull(x, qhull_options="QJ")
    return hull


def plot_convex_hulls(traces):
    for trace in traces:
        x = np.array(trace)
        hull = ConvexHull(x)
        plt.plot(x[hull.vertices, 0], x[hull.vertices, 1], 'k--', lw=0.3)  # plot the convex hull's vertices
        for v in hull.vertices:
            plt.plot(x[v, 0], x[v, 1], 'k+', lw=0.3)


def plot_expression(traces, color='k'):
    for trace in traces:
        xtab = []
        ytab = []
        for point in trace:
            xtab.append(point[0])
            ytab.append(point[1])
        plt.plot(xtab, ytab, color + '-', lw=2)
    # plt.show()


def compute_distances(traces, trace):
    # compute distaces from other traces
    distances = []
    for other_trace in traces:
        if other_trace == trace:
            distances.append('NULL')
        else:
            tmp_dist = []
            for point in trace:
                for other_point in other_trace:
                    d = math.sqrt((point[0] - other_point[0]) ** 2 + (point[1] - other_point[1]) ** 2)
                    tmp_dist.append(d)
            distances.append(min(tmp_dist))
    return distances


def find_blocked_view(point_of_view, destination_trace):
    angles = []
    hull = get_convex_hull(destination_trace)
    for vertex in hull.vertices:
        destination_point = destination_trace[vertex]
        if destination_point == point_of_view:  # if the two points have the same positions we consider the angle 0
            angle = 0
            angles.append(angle)
        else:
            if destination_point[1] > point_of_view[1]:
                angle = math.degrees(math.acos((destination_point[0] - point_of_view[0]) / math.sqrt(
                    (destination_point[0] - point_of_view[0]) ** 2 + (destination_point[1] - point_of_view[1]) ** 2)))
                angles.append(angle)
            else:
                angle = - math.degrees(math.acos((destination_point[0] - point_of_view[0]) / math.sqrt(
                    (destination_point[0] - point_of_view[0]) ** 2 + (destination_point[1] - point_of_view[1]) ** 2)))
                angles.append(angle)
    if get_bounding_box_center(destination_trace)[0] <= point_of_view[0] and min(angles) < 0 < max(angles):
        positive_angles = []
        negative_angles = []
        for a in angles:
            if a >= 0:
                positive_angles.append(a)
            else:
                negative_angles.append(a)
        blocked_view = [[-180.0, max(negative_angles)], [min(positive_angles), 180.0]]
    else:
        blocked_view = [[min(angles), max(angles)]]
    return blocked_view


def edge_check(source, destination, edges):
    for edge in edges:
        if edge[0] == source and edge[1] == destination:
            return True
        if edge[0] == destination and edge[1] == source:
            return True
    return False


def plot_graph(edges, math_expression):
    for edge in edges:
        s = math_expression.get_traces_dictionary()[edge[0]]
        d = math_expression.get_traces_dictionary()[edge[1]]
        bbc_s = get_bounding_box_center(s)
        bbc_d = get_bounding_box_center(d)
        plt.plot([bbc_s[0], bbc_d[0]], [bbc_s[1], bbc_d[1]], 'g-', lw=0.2)


def get_index_graph(edges, expression):
    index_representation = []
    for edge in edges:
        index_edge = []
        for point in edge:
            for trace in expression:
                if point == get_bounding_box_center(trace):
                    index_edge.append(expression.index(trace))
        index_representation.append(index_edge)
    return index_representation
