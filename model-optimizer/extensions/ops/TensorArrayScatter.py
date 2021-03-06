"""
 Copyright (c) 2018 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import networkx as nx
import numpy as np

from mo.graph.graph import Node
from mo.ops.op import Op
from mo.utils.utils import match_shapes


class TensorArrayScatter(Op):
    op = "TensorArrayScatterV3"

    def __init__(self, graph: nx.MultiDiGraph, attrs: dict):
        mandatory_props = {
            'type': __class__.op,
            'op': __class__.op,
            'infer': TensorArrayScatter.array_infer,
        }
        super().__init__(graph, mandatory_props, attrs)

    @staticmethod
    def array_infer(node: Node):
        handle = node.in_node(0)
        indices = node.in_node(1)
        value = node.in_node(2)
        flow_in = node.in_node(3)

        ta_node = Node(node.graph, str(handle.value))
        if ta_node.has_valid('element_shape') and len(ta_node.element_shape) > 0:
            assert match_shapes(ta_node['element_shape'], value.shape[1:]), \
                'Shapes are not compatible: {} and {}'.format(ta_node['element_shape'], value.shape[1:])
        else:
            ta_node['element_shape'] = value.shape[1:]

        # Assign element_shape anyway, because the original element_shape can contain -1
        ta_node['element_shape'] = value.shape[1:]
        #TODO: add smart check that indices and value.shape[0] is compatible

        output_shape = flow_in.shape
        output_value = flow_in.value
        #flow_out
        for _, out_node in node.graph.out_edges(node.id):
            node.graph.node[out_node]['shape'] = np.array(output_shape)
            node.graph.node[out_node]['value'] = None if output_value is None else np.array(output_value)
