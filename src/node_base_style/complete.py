import ast

from node_base_style.hoare_triple import State, Triple, IfTriple, LoopTriple, FuncTriple, pprint_cmd
from node_base_style.general import complete_triple
from node_base_style.if_statement import complete_if_triple
from node_base_style.loop import complete_loop_triple
from node_base_style.function_definition import complete_func_triple
from node_base_style.loop_condition import get_conditions, combin_condition


def complete_triple_cot(triple: Triple, model, config) -> str:
    # This function selects different processing logic based on various AST nodes and recursively obtains the overall postcondition.
    assert triple.postcondition == State.UNKNOWN
    if isinstance(triple.command,
                  (ast.Assign, ast.AugAssign, ast.Expr, ast.Return, ast.Raise, ast.Pass, ast.Break, ast.Continue)):
        post = complete_triple(triple, model)
        return post
    if isinstance(triple.command, list):
        pre = triple.precondition
        for subcmd in triple.command:
            completion = complete_triple_cot(Triple(pre, subcmd, State.UNKNOWN), model, config)
            pre = completion
        return pre
    if isinstance(triple.command, ast.If):
        pre = triple.precondition
        then_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), model, config)
        if_post = then_completion

        else_post = None
        if triple.command.orelse:
            else_completion = complete_triple_cot(Triple(pre, triple.command.orelse, State.UNKNOWN), model, config)
            else_post = else_completion

        if_triple = IfTriple(pre, triple.command, if_post, else_post, State.UNKNOWN)
        return complete_if_triple(if_triple, model)
    if isinstance(triple.command, ast.Try):
        # this is a very old version.
        pre = triple.precondition
        try_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), model, config)
        except_completion = complete_triple_cot(Triple(State.UNKNOWN, triple.command.body, State.UNKNOWN), model,
                                                config)
        ctx = [Triple(pre, triple.command.body, try_completion),
               Triple(State.UNKNOWN, triple.command.body, except_completion)]
        if triple.command.orelse:
            else_completion = complete_triple_cot(Triple(try_completion, triple.command.orelse, State.UNKNOWN), model,
                                                  config)
            ctx.append(Triple(pre, triple.command.orelse, else_completion))
        if triple.command.finalbody:
            finally_completion = complete_triple_cot(Triple(State.UNKNOWN, triple.command.finalbody, State.UNKNOWN),
                                                     model, config)
            ctx.append(Triple(State.UNKNOWN, triple.command.orelse, finally_completion))
        return complete_triple(triple, model)
    if isinstance(triple.command, ast.For):
        k = config["loop-unrolling-count"]
        body_completion = complete_triple_cot(Triple(State.TOP, triple.command.body, State.UNKNOWN), model, config)
        while_triple = LoopTriple(triple.precondition, triple.command, triple.command.body, body_completion,
                                  State.UNKNOWN, "for")
        examples = []
        conditions = get_conditions(model, while_triple, k)
        pre = triple.precondition
        for i in range(k):
            post = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), model, config)
            examples.append(Triple(pre, triple.command, post))
            pre = combin_condition(model, post, conditions[i])
        return complete_loop_triple(while_triple, model, examples)
    if isinstance(triple.command, ast.While):
        k = config["loop-unrolling-count"]
        body_completion = complete_triple_cot(Triple(State.TOP, triple.command.body, State.UNKNOWN), model, config)
        for_triple = LoopTriple(triple.precondition, triple.command, triple.command.body, body_completion,
                                State.UNKNOWN, "while")
        return complete_loop_triple(for_triple, model, k)
    if isinstance(triple.command, ast.FunctionDef):
        pre = triple.precondition
        body_completion = complete_triple_cot(Triple(pre, triple.command.body, State.UNKNOWN), model, config)
        func_triple = FuncTriple(triple.precondition, triple.command, body_completion, State.UNKNOWN)
        return complete_func_triple(func_triple, model)
    if isinstance(triple.command, (ast.Import, ast.ImportFrom, ast.Assert)):
        return triple.precondition
    raise ValueError(f"unsupported statement type: {triple.command} {pprint_cmd(triple.command)}")


def compute_postcondition(model, precondition, program, config):
    parsed_code = ast.parse(program).body
    triple = Triple(precondition, parsed_code, State.UNKNOWN)
    postcondition = complete_triple_cot(triple, model, config)
    return postcondition
