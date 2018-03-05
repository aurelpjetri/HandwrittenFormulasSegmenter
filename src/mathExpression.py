import math

import numpy as np
import scipy.interpolate
import sys

import util


class MathExpression:
    def __init__(self, traces, traces_dictionary):
        self.traces = traces
        self.traces_dictionary = traces_dictionary
        # self.reverse_dictionary = {}
        # for key, value in self.traces_dictionary.items():
        #     self.reverse_dictionary[value] = key

    def get_traces(self):
        return self.traces

    def get_traces_dictionary(self):
        return self.traces_dictionary

    # def get_reversed_dictionary(self):
    #     return self.reverse_dictionary

    def get_trace_id(self, trace):
        for key, value in self.traces_dictionary.items():
            if value == trace:
                return key
        return 'NULL'

    # PREPROCESSING:

    # 0) ribalta l'espressione
    def fix_expression(self):
        max_ordinate = -sys.maxint
        for tr in self.traces:
            for point in tr:
                if point[1] > max_ordinate:
                    max_ordinate = point[1]
        for i in range(len(self.traces)):
            id_trace = self.get_trace_id(self.traces[i])
            for j in range(len(self.traces[i])):
                self.traces[i][j][1] = max_ordinate - self.traces[i][j][1]
            # update the dictionaries
            self.traces_dictionary[id_trace] = self.traces[i]

    # 1) remove duplicate points
    def remove_duplicate_points(self):
        for trace in self.traces:
            i = 0
            trace_id = self.get_trace_id(trace)
            while i < len(trace):
                j = i + 1
                while j < len(trace):
                    if trace[i] == trace[j]:
                        del trace[j]
                    else:
                        j += 1
                i += 1

            # check if the trace has at least 3 point in order to compute the convex hull
            if len(trace) < 3:
                i = 1
                while len(trace) < 3:
                    trace.append([trace[-1][0] + (0.001 * i), trace[-1][1] + (0.001 * i)])
                    i += 1

            # update the dictionaries
            self.traces_dictionary[trace_id] = trace

    # 2) normalize coordinates
    def normalize_coordinates(self):
        expression_box = [sys.maxint, -sys.maxint, sys.maxint, -sys.maxint]
        for stroke in self.traces:
            for point in stroke:
                if point[0] < expression_box[0]:
                    expression_box[0] = point[0]
                if point[0] > expression_box[1]:
                    expression_box[1] = point[0]
                if point[1] < expression_box[2]:
                    expression_box[2] = point[1]
                if point[1] > expression_box[3]:
                    expression_box[3] = point[1]
        exp_width = abs(expression_box[1] - expression_box[0])
        exp_height = abs(expression_box[3] - expression_box[2])
        for i in range(len(self.traces)):
            trace_id = self.get_trace_id(self.traces[i])
            for j in range(len(self.traces[i])):
                x = ((self.traces[i][j][0] - expression_box[0]) / exp_height)
                y = ((self.traces[i][j][1] - expression_box[2]) / exp_height)
                self.traces[i][j][0] = x
                self.traces[i][j][1] = y
            # update the dictionaries
            self.traces_dictionary[trace_id] = self.traces[i]

    # 3) smooth strokes:
    #       repleace each point with the average of previous, current and following point
    def smooth_trace(self):
        for trace in self.traces:
            trace_id = self.get_trace_id(trace)
            for i in range(len(trace)):
                x = (trace[i - 1][0] + trace[i][0] + trace[i + 1][0]) / 3
                y = (trace[i - 1][1] + trace[i][1] + trace[i + 1][1]) / 3
                trace[i] = [x, y]
            # update the dictionaries
            self.traces_dictionary[trace_id] = trace

    # lo faccio sugli ultimi 3 punti e sui primi 3
    def remove_hooks(self):
        for trace in self.traces:
            minX, maxX, minY, maxY = util.get_bounding_box(trace)
            diagonal = math.sqrt(math.pow(maxX - minX, 2) + math.pow(maxY - minY, 2))

            if len(trace) > 4:
                # at the beginning of the trace..
                x_b_1 = trace[1][0] - trace[0][0]
                y_b_1 = trace[1][1] - trace[0][1]
                angle_b_1 = math.atan2(y_b_1, x_b_1)
                distance_b = math.sqrt(math.pow(x_b_1, 2) + math.pow(y_b_1, 2))
                x_b_2 = trace[2][0] - trace[1][0]
                y_b_2 = trace[2][1] - trace[1][1]
                angle_b_2 = math.atan2(y_b_2, x_b_2)
                angle_diff_b = abs(angle_b_1 - angle_b_2)

                while angle_diff_b > math.pi:
                    angle_diff_b = math.pi * 2 - angle_diff_b
                if angle_diff_b > math.pi / 4 and distance_b < 0.07 * diagonal:
                    trace_id = self.get_trace_id(trace)
                    del trace[0]
                    # update the dictionaries
                    self.traces_dictionary[trace_id] = trace

                # ..and at the end of the trace.
                x_e_1 = trace[-2][0] - trace[-1][0]
                y_e_1 = trace[-2][1] - trace[-1][1]
                angle_e_1 = math.atan2(y_e_1, x_e_1)
                distance_e = math.sqrt(math.pow(x_e_1, 2) + math.pow(y_e_1, 2))
                x_e_2 = trace[-3][0] - trace[-2][0]
                y_e_2 = trace[-3][1] - trace[-2][1]
                angle_e_2 = math.atan2(y_e_2, x_e_2)
                angle_diff_e = abs(angle_e_1 - angle_e_2)
                while angle_diff_e > math.pi:
                    angle_diff_e = math.pi * 2 - angle_diff_e
                if angle_diff_e > math.pi / 4 and distance_e < 0.07 * diagonal:
                    trace_id = self.get_trace_id(trace)
                    del trace[-1]
                    # update the dictionaries
                    self.traces_dictionary[trace_id] = trace

    # per ora non produce side effects sulla traccia ma ne ritorna un'altra
    def interpolate_traces(self):
        int_expression = []
        for trace in self.traces:
            tr_x = np.array([])
            tr_y = np.array([])
            for point in trace:
                tr_x = np.append(tr_x, [point[0]])
                tr_y = np.append(tr_y, [point[1]])
            # get the cumulative distance along the contour
            dist = np.sqrt((tr_x[:-1] - tr_x[1:]) ** 2 + (tr_y[:-1] - tr_y[1:]) ** 2)
            dist_along = np.concatenate(([0], dist.cumsum()))

            spline, u = scipy.interpolate.splprep([tr_x, tr_y], u=dist_along, s=0)
            interp_d = np.linspace(dist_along[0], dist_along[-1], len(trace) * 10)

            interp_x, interp_y = scipy.interpolate.splev(interp_d, spline)

            int_trace = []
            for i in range(len(interp_x)):
                int_trace.append([interp_x[i], interp_y[i]])
            int_expression.append(int_trace)
        return int_expression

    def preprocess(self):
        self.fix_expression()
        self.normalize_coordinates()
        self.remove_duplicate_points()
        self.remove_hooks()
        # self.interpolate_traces(self)

    # FEATURE EXTRACTION:

    def get_2d_histogram(self, edge):
        traces_dictionary = self.get_traces_dictionary()
        trace_a = traces_dictionary[edge[0]]
        trace_b = traces_dictionary[edge[1]]

        bb_a = util.get_bounding_box(trace_a)
        bb_b = util.get_bounding_box(trace_b)

        # bb_center_a = util.get_bounding_box_center(trace_a)
        # bb_center_b = util.get_bounding_box_center(trace_b)

        trace_a_x = []
        trace_a_y = []
        for p in trace_a:
            trace_a_x.append(p[0])
            trace_a_y.append(p[1])

        ymax = max(bb_a[3], bb_b[3])
        ymin = min(bb_a[2], bb_b[2])

        # xmin = min(bb_center_a[0], bb_center_b[0])
        # xmax = max(bb_center_a[0], bb_center_b[0])
        xmin = min(bb_a[0], bb_b[0])
        xmax = max(bb_a[1], bb_b[1])

        H1, xedges, yedges = np.histogram2d(trace_a_x, trace_a_y, bins=(5, 6), range=[[xmin, xmax], [ymin, ymax]])

        trace_b_x = []
        trace_b_y = []
        for p2 in trace_b:
            trace_b_x.append(p2[0])
            trace_b_y.append(p2[1])

        H2, xedges, yedges = np.histogram2d(trace_b_x, trace_b_y, bins=(5, 6), range=[[xmin, xmax], [ymin, ymax]])

        # print "H2",H2
        trace_c_x = []
        trace_c_y = []
        for id, otrc in traces_dictionary.items():
            if id != edge[0] and edge[1]:
                for otrc_point in otrc:
                    trace_c_x.append(otrc_point[0])
                    trace_c_y.append(otrc_point[1])

        H3, xedges, yedges = np.histogram2d(trace_c_x, trace_c_y, bins=(5, 6), range=[[xmin, xmax], [ymin, ymax]])

        return H1, H2, H3

    def get_features(self, id_a, id_b, get_dictionary_flag=False):
        a_trace = self.traces_dictionary[id_a]
        b_trace = self.traces_dictionary[id_b]
        features = []
        features_dictionary = {}
        bounding_box_a = util.get_bounding_box(a_trace)
        bounding_box_b = util.get_bounding_box(b_trace)

        # Horizontal distance
        average_x_a = 0
        average_x_b = 0
        for p in a_trace:
            average_x_a += p[0]
        for q in b_trace:
            average_x_b += q[0]
        average_x_a /= len(a_trace)
        average_x_b /= len(b_trace)
        horizontal_distance = abs(average_x_a - average_x_b)
        features.append(horizontal_distance)
        features_dictionary[len(features) - 1] = 'horizontal distance'

        # Size difference
        size_difference = abs(max(bounding_box_a[1]-bounding_box_a[0], bounding_box_a[3]-bounding_box_a[2]) - max(
            bounding_box_b[1]-bounding_box_b[0], bounding_box_b[3]-bounding_box_b[2]))
        features.append(size_difference)
        features_dictionary[len(features) - 1] = 'size difference'

        # 5) Minimum point distance
        tmp_dist = []
        for point in a_trace:
            for other_point in b_trace:
                d = math.sqrt((point[0] - other_point[0]) ** 2 + (point[1] - other_point[1]) ** 2)
                tmp_dist.append(d)
        min_distance = min(tmp_dist)
        features.append(min_distance)
        features_dictionary[len(features) - 1] = 'minimum point distance'

        # 6) Maximum distance
        max_distance = max(tmp_dist)
        features.append(max_distance)
        features_dictionary[len(features) - 1] = 'minimum point distance'

        # 6) Overlapping area (of the bounding boxes?)
        o_x = min(bounding_box_a[1], bounding_box_b[1]) - max(bounding_box_a[0], bounding_box_b[0])
        o_y = min(bounding_box_a[3], bounding_box_b[3]) - max(bounding_box_a[2], bounding_box_b[2])
        if o_x >= 0 and o_y >= 0:
            overlapping_area = o_x * o_y
        else:
            overlapping_area = 0
        bb_a = (bounding_box_a[1] - bounding_box_a[0])*(bounding_box_a[3] - bounding_box_a[2])
        bb_b = (bounding_box_b[1] - bounding_box_b[0])*(bounding_box_b[3] - bounding_box_b[2])
        # divide by the area of the smallest bounding box
        if overlapping_area != 0:
            overlapping_area = overlapping_area / min(bb_a, bb_b)
        features.append(overlapping_area)
        features_dictionary[len(features) - 1] = 'overlapping area'

        # 8) Horizontal overlapping
        if o_x > 0:
            horizontal_overlapping = o_x
        else:
            horizontal_overlapping = 0
        features.append(horizontal_overlapping)
        features_dictionary[len(features) - 1] = 'horizontal overlapping'

        # 9.a) distance between strokes fist points
        fist_points_distance = math.sqrt((a_trace[0][0] - b_trace[0][0]) ** 2 + (a_trace[0][1] - b_trace[0][1]) ** 2)
        features.append(fist_points_distance)
        features_dictionary[len(features) - 1] = 'fist points distance'

        # 9.b) last points distance
        last_points_distance = math.sqrt(
            (a_trace[-1][0] - b_trace[-1][0]) ** 2 + (a_trace[-1][1] - b_trace[-1][0]) ** 2)
        features.append(last_points_distance)
        features_dictionary[len(features) - 1] = 'last points distance'

        # 9.c) offset ????

        # 13) Centers of mass distance
        arr_a = np.array(a_trace)
        arr_b = np.array(b_trace)
        com_a = arr_a.sum(axis=0) / len(a_trace)
        com_b = arr_b.sum(axis=0) / len(b_trace)
        centers_of_mass_distance = math.sqrt((com_a[0] - com_b[0]) ** 2 + (com_a[1] - com_b[1]) ** 2)
        features.append(centers_of_mass_distance)
        features_dictionary[len(features) - 1] = 'centers of mass distance'
        # del arr_a, arr_b

        # 15) Horizontal offset between last point and first point
        #     tenendo conto che la traccia a ha identificatore minore della traccia b
        last_first_hor_offset = abs(a_trace[-1][0] - b_trace[-1][0])
        features.append(last_first_hor_offset)
        features_dictionary[len(features) - 1] = 'last-fist point horizontal offset'

        # 16) Distance of the bounding boxes centers
        bb_c_a = util.get_bounding_box_center(a_trace)
        bb_c_b = util.get_bounding_box_center(b_trace)
        distance_bb_center = math.sqrt((bb_c_a[0] - bb_c_b[0]) ** 2 + (bb_c_a[1] - bb_c_b[1]) ** 2)
        features.append(distance_bb_center)
        features_dictionary[len(features) - 1] = 'bounding box centers distance'

        # vertical distance between bounding box center
        vertical_bb_center_distance = abs(bb_c_a[1] - bb_c_b[1])
        features.append(vertical_bb_center_distance)
        features_dictionary[len(features) - 1] = 'vertical bounding box center distance'

        # Parallelity
        if a_trace[-1][0] == a_trace[0][0]:
            if a_trace[-1][1] == a_trace[0][1]:
                alpha = 0
            else:
                alpha = math.pi / 2
        else:
            alpha = math.atan((a_trace[-1][1] - a_trace[0][1]) / (a_trace[-1][0] - a_trace[0][0]))
        if b_trace[-1][0] == b_trace[0][0]:
            if b_trace[-1][1] == b_trace[0][1]:
                beta = 0
            else:
                beta = math.pi / 2
        else:
            beta = math.atan((b_trace[-1][1] - b_trace[0][1]) / (b_trace[-1][0] - b_trace[0][0]))
        parallelity = abs(alpha - beta)
        features.append(parallelity)
        features_dictionary[len(features) - 1] = 'parallelity'

        # Backward movement????

        # Writing slope
        if a_trace[-1][0] == b_trace[0][0]:
            if a_trace[-1][1] == b_trace[0][1]:
                slope = 0
            else:
                slope = math.pi / 2
        else:
            slope = math.atan((a_trace[-1][1] - b_trace[0][1]) / (a_trace[-1][0] - b_trace[0][0]))
        features.append(slope)
        features_dictionary[len(features) - 1] = 'writing slope'

        # Writing curvature
        if a_trace[0][0] == b_trace[0][0]:
            if a_trace[0][1] == b_trace[0][1]:
                alpha = 0
            else:
                alpha = math.pi / 2
        else:
            alpha = math.atan((a_trace[0][1] - b_trace[0][1]) / (a_trace[0][0] - b_trace[0][0]))
        if a_trace[-1][0] == b_trace[-1][0]:
            if a_trace[-1][1] == b_trace[-1][1]:
                beta = 0
            else:
                beta = math.pi / 2
        else:
            beta = math.atan((a_trace[-1][1] - b_trace[-1][1]) / (a_trace[-1][0] - b_trace[-1][0]))
        writing_curvature = abs(alpha - beta)
        features.append(writing_curvature)
        features_dictionary[len(features) - 1] = 'writing curvature'

        h1, h2, h3 = self.get_2d_histogram([id_a, id_b])

        for row1 in h1:
            for el in row1:
                features.append(el)
        for row2 in h2:
            for el2 in row2:
                features.append(el2)
        for row3 in h3:
            for el3 in row3:
                features.append(el3)

        if get_dictionary_flag:
            return features, features_dictionary
        else:
            return features

