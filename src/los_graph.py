import util, sys
import matplotlib.pyplot as plt


def get_los_graph(math_expression, threshold=1):

    expression = math_expression.get_traces()

    edges = []
    # threshold = 1

    for trace in expression:
        field_of_view = [[-180.0, 180.0]]
        bounding_box_center = util.get_bounding_box_center(trace)
        distances = util.compute_distances(expression, trace)
        plt.plot(bounding_box_center[0], bounding_box_center[1], 'r+')

        for i in range(0, len(expression)-1):
            nearest_trace_index = distances.index(min(distances))
            distances[nearest_trace_index] = sys.maxint
            if nearest_trace_index == expression.index(trace):
                continue
            other_trace = expression[nearest_trace_index]
            blocked_intervals = util.find_blocked_view(bounding_box_center, other_trace)
            intersection_flag = False
            intersection_length = 0

            for blocked_view in blocked_intervals:
                to_remove = []
                to_add = []
                for visible_interval in field_of_view:
                    if blocked_view[0] <= min(visible_interval) < blocked_view[1]:
                        to_remove.append(visible_interval)
                        if blocked_view[1] < max(visible_interval):
                            intersection_flag = True
                            intersection_length += blocked_view[1] - min(visible_interval)
                            to_add.append([blocked_view[1], max(visible_interval)])
                        else:
                            intersection_flag = True
                            intersection_length += max(visible_interval) - min(visible_interval)
                    if min(visible_interval) < blocked_view[0] < max(visible_interval):
                        to_remove.append(visible_interval)
                        if blocked_view[1] < max(visible_interval):
                            intersection_flag = True
                            intersection_length += blocked_view[1] - blocked_view[0]
                            to_add.append([min(visible_interval), blocked_view[0]])
                            to_add.append([blocked_view[1], max(visible_interval)])
                        else:
                            intersection_flag = True
                            intersection_length += max(visible_interval) - blocked_view[0]
                            to_add.append([min(visible_interval), blocked_view[0]])
                for r in to_remove:
                    field_of_view.remove(r)
                for a in to_add:
                    field_of_view.append(a)
            if intersection_flag and intersection_length >= threshold:
                # source = bounding_box_center
                # destination = util.get_bounding_box_center(other_trace)

                # CHANGED!! NOW THE EDGES ARE DEFINED THROUGH TRACES IDENTIFIERS FROM THE INKML!!
                source = math_expression.get_trace_id(trace)
                destination = math_expression.get_trace_id(other_trace)
                if util.edge_check(source, destination, edges) == False:
                    edges.append([source, destination])
    return edges

