import itertools
import random
class Node:
    def __init__(self, name, accepted = False):
        self.name = name
        self.transitions = list()
        self.marked = False
        self.accepted = accepted

    def __str__(self):
        return f"[{self.name}]"


class Transition:
    def __init__(self,value ,source, target):
        self.source = source
        self.target = target
        self.value = value

    def __str__(self):
        return f" {self.value} : {self.source} -> {self.target}"



class Automat:
    def __init__(self, nodes : list, transitions : list):
        self.nodes = nodes
        self.transitions = transitions
        for t in transistion:
            t.source.transitions.append(t)
        self.big_nodes = dict()
        self.reachable_nodes = list()


    def __str__(self):
        res = "non deterministic automat:\n"
        for node in self.nodes:
            res += f"{node} :\n"
            for t in node.transitions:
                res += f"\t{t}\n"

        res += "deterministic automat:\n"
        for node in self.reachable_nodes:
            res += f"{node} :\n"
            for t in node.transitions:
                res += f"\t{t}\n"
        return res

    def determinize(self, start : Node, accepted : list):
        self.det_nodes = dict()
        self.accepted_set = (node.name for node in accepted)
        self.find_transistions()
        self.find_reachable(start)
        self.build_reachable()
        

    def get_node(self,name):
        if name in self.big_nodes:
            return self.big_nodes[name]
        else:
            node = Node(name, accepted = self.is_name_accepted(name))
            self.big_nodes[name] = node
            return node

    def is_name_accepted(self,name):
        for accepted in self.accepted_set:
            if accepted in name:
                return True
        return False

    def find_transistions(self):
        for x in map(''.join, itertools.product('01', repeat=len(self.nodes))):
            node_name = "".join(sorted([node.name for node, bit in zip(nodes, x) if bit == "1"]))
            node = self.get_node(node_name)

            next_nodes = dict()
            for i, char in enumerate(x):
                if char == '1':
                    for transition in nodes[i].transitions:
                        if transition.value not in next_nodes:
                            next_nodes[transition.value] = set()
                        next_nodes[transition.value].add(transition.target)
            
            for value, targets in next_nodes.items():
                target_name = "".join(sorted([node.name for node in targets]))
                target = self.get_node(target_name)
                node.transitions.append(Transition(value, node, target))

    def find_reachable(self, start : Node):
        queue = [self.get_node(start.name)]

        while queue:
            node = queue.pop(0)
            if node.marked:
                continue
            node.marked = True
            for t in node.transitions:
                queue.append(t.target)

    def build_reachable(self):
        for name, node in self.big_nodes.items():
            if node.marked:
                self.reachable_nodes.append(node)

    def generate_edges(self):
        for node in self.reachable_nodes:
            for t in node.transitions:
                yield t

    def condese_transitions(self):
        for node in self.reachable_nodes:
            condenser = dict()
            to_remove = list()
            for t in node.transitions:
                name = f"{t.source.name} -> {t.target.name}"
                if name not in condenser:
                    condenser[name] = t
                    continue
                condenser[name].value += f", {t.value}"
                to_remove.append(t)
            for t in to_remove:
                node.transitions.remove(t)

    def both_ways(self, transition):
        dst_transistions = self.get_node(transition.target.name).transitions
        for t in dst_transistions:
            if t.target.name == transition.source.name:
                return True
        return False


    def write_latex(self, vertical_spaceing = 2, horizontal_spaceing = 4):
        #num_with_length = [(lambda i: count([node for self.reachable_node, if len(node) == i])) for i in range(len(self.nodes))]
        # count how many nodes have a certain length
        num_with_length = [len([node for node in self.reachable_nodes if len(node.name) == i]) for i in range(len(self.nodes)+1)]
        max_length = max(num_with_length)
        with open("automat.tex", "w") as f:
            f.write("\\begin{tikzpicture}\n")
            f.write("\\tikzset{vertex/.style = {shape=circle,draw,minimum size=1.5em}} \n\\tikzset{edge/.style = {->,> = latex'}}")

            for node in self.reachable_nodes:
                print(len(node.name))
                f.write(f"\\node[vertex] ({node.name}) at ({len(node.name)*horizontal_spaceing},{(max_length - num_with_length[len(node.name)])*vertical_spaceing}) {{ $ {node.name} $}};\n")
                num_with_length[len(node.name)] -= 1
            for t in self.generate_edges():
                if (t.source != t.target and (len(t.source.name) == len(t.target.name) or self.both_ways(t))):
                    bending = "bend right"
                elif (t.source==t.target):
                    bending = "loop above"
                else:
                    bending = ""
                description = f"node[near start, {'left' if len(t.source.name) == len(t.target.name) else 'above'}] {{${t.value}$}}"
                
                
                f.write(f"\\draw[edge] ({t.source.name}) to[{bending}] {description} ({t.target.name}) ;\n")

            f.write("\\end{tikzpicture}")

p = Node("p")
q = Node("q")
s = Node("s", accepted=True)
r = Node("r")

nodes = [p, q, s, r]

start = p

transistion = [
    Transition("a", p, q),
    Transition("a", p, r),
    Transition("b", p, r),

    Transition("b", r, p),
    Transition("a", r, r),
    Transition("a", r, s),

    Transition("b", q, q),
    Transition("b", q, s),

    Transition("a", s, s),
    Transition("a", s, r),
    Transition("b", s, r)
]


automat = Automat(nodes, transistion)
automat.determinize(start, [s])
automat.condese_transitions()
automat.write_latex()