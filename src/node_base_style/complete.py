import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, FuncTriple, TryTriple, pprint_cmd
from node_base_style.general import complete_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.function_definition import complete_func_triple, get_func_def
from node_base_style.loop import complete_loop_triple, get_while_head, ForToWhileTransformer
from node_base_style.loop_condition import get_precondition
from node_base_style.try_statement import complete_try_triple


class PostconditionAnalyzer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.collected_returns = []  # Used to collect the postconditions of return statements as strings

    def complete_triple_cot(self, triple: Triple, depth=0) -> str:
        assert triple.postcondition == State.UNKNOWN

        if isinstance(triple.command,
                      (ast.Assign, ast.AugAssign, ast.Expr, ast.Raise, ast.Pass, ast.Break, ast.Continue)):
            post = complete_triple(triple, self.model)
            return post

        # Handle return statements
        if isinstance(triple.command, ast.Return):
            post = complete_triple(triple, self.model)
            if depth == 1:
                self.collected_returns.append(str(post))
            return post

        if isinstance(triple.command, list):
            pre = triple.precondition
            for subcmd in triple.command:
                completion = self.complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), depth=depth)
                pre = completion
            return pre

        if isinstance(triple.command, ast.If):
            pre = triple.precondition
            then_completion = self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=depth)
            if_post = then_completion

            else_post = None
            if triple.command.orelse:
                else_completion = self.complete_triple_cot(Triple(pre, triple.command.orelse, State.UNKNOWN),
                                                           depth=depth)
                else_post = else_completion

            if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)
            post = complete_if_triple(if_triple, self.model)
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append(str(post))
            return post

        if isinstance(triple.command, ast.Try):
            pre = triple.precondition
            try_command = triple.command.body
            except_command = triple.command.handlers[0].body
            try_completion = self.complete_triple_cot(Triple(pre, try_command, State.UNKNOWN), depth=depth)
            except_completion = self.complete_triple_cot(Triple(State.UNKNOWN, except_command, State.UNKNOWN),
                                                         depth=depth)

            try_triple = TryTriple(pre, triple.command, try_command, try_completion, except_command, except_completion,
                                   State.UNKNOWN)

            post = complete_try_triple(try_triple, self.model)
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append(str(post))
            return post

        if isinstance(triple.command, ast.For):
            t = ForToWhileTransformer()
            while_code = t.visit(triple.command)
            new_triple = Triple(triple.precondition, while_code, State.UNKNOWN)
            return self.complete_triple_cot(new_triple, depth=depth)

        if isinstance(triple.command, ast.While):
            k = self.config["loop-unrolling-count"]
            body_command = triple.command.body
            while_head = get_while_head(triple.command)
            examples = []
            pre = triple.precondition
            for i in range(k):
                post = self.complete_triple_cot(Triple(pre, body_command, State.UNKNOWN), depth=depth)
                examples.append(Triple(pre, body_command, post))
                pre = get_precondition(self.model, post, while_head)

            triple = Triple(triple.precondition, triple.command, State.UNKNOWN)
            post = complete_loop_triple(triple, self.model, examples)
            if depth == 1 and any(isinstance(node, ast.Return) for node in ast.walk(triple.command)):
                self.collected_returns.append(post)

            return post

        if isinstance(triple.command, ast.FunctionDef):
            pre = triple.precondition
            def_str = get_func_def(triple.command)

            body_completion = self.complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), depth=1)

            return_conditions_str = " ; ".join(self.collected_returns)

            func_triple = FuncTriple(triple.precondition, triple.command, def_str, triple.command.body,
                                     return_conditions_str, State.UNKNOWN)
            return complete_func_triple(func_triple, self.model)

        if isinstance(triple.command, (ast.Import, ast.ImportFrom, ast.Assert)):
            return triple.precondition

        raise ValueError(f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}")


def compute_postcondition(model, precondition, program, config):
    analyzer = PostconditionAnalyzer(model, config)
    parsed_code = ast.parse(program).body
    triple = Triple(precondition, parsed_code, State.UNKNOWN)
    postcondition = analyzer.complete_triple_cot(triple)
    return postcondition
