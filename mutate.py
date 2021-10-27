import ast
import sys
import astor
import copy
import random


def main():
    with open(sys.argv[1], "r") as source:
        tree = ast.parse(source.read())

    analyzer = Analyzer()
    analyzer.visit(tree)
    random.seed(38473)
    random.shuffle(analyzer.mutate_node)
    num_mutations = 100
    for(index, node_id) in enumerate(analyzer.mutate_node[:num_mutations]):
        with open(sys.argv[1], "r") as s:
            t = ast.parse(s.read())
        
        mutate = Mutate(node_id).visit(t)
        new_code = astor.to_source(mutate)
        fname = str(index) + ".py"
        with open(fname, "w") as f:
            f.write(new_code)


'''
    ast.fix_missing_locations(tree)
    co = compile(tree, "<ast>", "exec")
    exec(co)
'''

class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.node_id = 0
        self.mutate_node = []
    
    def visit_Assign(self, node):
        self.generic_visit(node)
        self.mutate_node.append(self.node_id)
        self.node_id += 1
    
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Add):
            self.mutate_node.append(self.node_id)
        if isinstance(node.op, ast.Sub):
            self.mutate_node.append(self.node_id)
        if isinstance(node.op, ast.Mult):
            self.mutate_node.append(self.node_id)
        if isinstance(node.op, ast.Div):
            self.mutate_node.append(self.node_id)
        self.node_id += 1
    
    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.And):
            self.mutate_node.append(self.node_id)
        if isinstance(node.op, ast.Or):
            self.mutate_node.append(self.node_id)
        self.node_id += 1
    
    
    def visit_Compare(self, node):
        self.generic_visit(node)
        if isinstance(node.ops[0], ast.Gt):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.Lt):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.Eq):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.NotEq):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.GtE):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.LtE):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.In):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.NotIn):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.Is):
            self.mutate_node.append(self.node_id)
        if isinstance(node.ops[0], ast.IsNot):
            self.mutate_node.append(self.node_id)
        self.node_id += 1
    
    def visit_If(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.If):
            self.mutate_node.append(self.node_id)
        self.node_id += 1
    
    def visit_While(self, node):
        self.generic_visit(node)
        if isinstance(node, ast.While):
            self.mutate_node.append(self.node_id)
        self.node_id += 1

    
        
        
class Mutate(ast.NodeTransformer):
    def __init__(self, num_mutations):
        self.num_mutations = num_mutations
        self.counter = 0
    
    def visit_Assign(self, node):
        self.generic_visit(node)
        self.counter += 1
        mutated_node = copy.deepcopy(node)
        if self.counter == self.num_mutations:
            if isinstance(node, ast.Assign):
                return ast.copy_location(ast.Assign(targets=node.targets, value=ast.NameConstant(value=None)), node)
            elif isinstance(node, ast.AugAssign):
                return ast.copy_location(ast.Assign(targets=node.targets, value=ast.NameConstant(value=node.value)), node)
        return mutated_node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        self.counter += 1
        if self.counter == self.num_mutations:
            if isinstance(node.op, ast.Add):
                print("replacing ADD")
                return ast.Expression(ast.BinOp(
                    node.left,
                    ast.Sub(),
                    node.right))
            elif isinstance(node.op, ast.Sub):
                print("replacing Sub")
                return ast.Expression(ast.BinOp(
                    node.left,
                    ast.Add(),
                    node.right))
            elif isinstance(node.op, ast.Mult):
                print("replacing MULT")
                return ast.Expression(ast.BinOp(
                    node.left,
                    ast.Div(),
                    node.right))
            elif isinstance(node.op, ast.Div):
                print("replacing DIV")
                return ast.Expression(ast.BinOp(
                    node.left,
                    ast.Mult(),
                    node.right))
        return node
    
    def visit_Compare(self, node):
        self.generic_visit(node)
        mutated_node = copy.deepcopy(node)
        self.counter += 1
        if self.counter == self.num_mutations:
            if isinstance(node.ops[0], ast.Eq):
                print("replacing Eq")
                mutated_node.ops[0] = ast.NotEq()
            elif isinstance(node.ops[0], ast.NotEq):
                print("replacing GtE")
                mutated_node.ops[0] = ast.Eq()      
            elif isinstance(node.ops[0], ast.Lt):
                print("replacing Lt")
                mutated_node.ops[0] = ast.GtE()          
            elif isinstance(node.ops[0], ast.LtE):
                print("replacing LtE")
                mutated_node.ops[0] = ast.Gt()  
            elif isinstance(node.ops[0], ast.Gt):
                print("replacing Gt")
                mutated_node.ops[0] = ast.LtE()
            elif isinstance(node.ops[0], ast.GtE):
                print("replacing GtE")
                mutated_node.ops[0] = ast.Lt()
            elif isinstance(node.ops[0], ast.In):
                print("replacing In")
                mutated_node.ops[0] = ast.NotIn()
            elif isinstance(node.ops[0], ast.NotIn):
                print("replacing In")
                mutated_node.ops[0] = ast.In()
            elif isinstance(node.ops[0], ast.Is):
                print("replacing GtE")
                mutated_node.ops[0] = ast.IsNot()
            elif isinstance(node.ops[0], ast.IsNot):
                print("replacing GtE")
                mutated_node.ops[0] = ast.Is()
        return mutated_node
    
    def visit_BoolOp(self, node):
        self.generic_visit(node)
        self.counter += 1
        mutated_node = copy.deepcopy(node)
        if self.counter == self.num_mutations:
            if isinstance(node.op, ast.And):
                mutated_node.op = ast.Or()
            elif isinstance(node.op, ast.Or):
                mutated_node.op = ast.And()
        return mutated_node

    def visit_If(self, node):
        self.generic_visit(node)
        self.counter += 1
        mutated_node = copy.deepcopy(node)
        if self.counter == self.num_mutations:
            if isinstance(node, ast.If):
                print("if always true")
                mutated_node.value = True
        return mutated_node
    
    def visit_While(self, node):
        self.generic_visit(node)
        self.counter += 1
        mutated_node = copy.deepcopy(node)
        if self.counter == self.num_mutations:
            if isinstance(node, ast.While):
                print("if always true")
                mutated_node.value = False
        return mutated_node


if __name__ == "__main__":
    main()


'''
class AssertCmpTransformer(ast.NodeTransformer):
    def visit_Assert(self, node):
        if isinstance(node.test, ast.Compare) and \
                len(node.test.ops) == 1 and \
                isinstance(node.test.ops[0], ast.Eq):
            call = ast.Call(func=ast.Name(id='assert_equal', ctx=ast.Load()),
                            args=[node.test.left, node.test.comparators[0]],
                            keywords=[])
            # Wrap the call in an Expr node, because the return value isn't used.
            newnode = ast.Expr(value=call)
            ast.copy_location(newnode, node)
            ast.fix_missing_locations(newnode)
            return newnode

        # Remember to return the original node if we don't want to change it.
        return node
'''