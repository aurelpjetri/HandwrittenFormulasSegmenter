import xml.etree.ElementTree as ET
from mathExpression import MathExpression

# python class parser from inkml file to math expression

class ParserXml:
    def __init__(self):
        return None

    def parse_xml(self, path):
        root = ET.parse(path).getroot()
        coordinates_list = []
        trace_dictionary = {}
        for child in root:
            if child.tag == '{http://www.w3.org/2003/InkML}trace':
                trace_coordinates = []
                float_trace_coordinates = []
                trace_coordinates.append(child.text)
                txt = child.text
                tmp_list = txt.split(",")
                splitted_cc = []
                for raw_couple in tmp_list:
                    local_tmp = raw_couple.rsplit()
                    splitted_cc.append(local_tmp)
                for couple in splitted_cc:
                    float_couple = []
                    for str_c in couple:
                        local_float = float(str_c)
                        float_couple.append(local_float)
                    float_trace_coordinates.append(float_couple)
                coordinates_list.append(float_trace_coordinates)
                trace_id = int(child.get('id'))
                trace_dictionary[trace_id] = float_trace_coordinates

        expression = MathExpression(coordinates_list, trace_dictionary)
        return expression
