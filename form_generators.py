from copy import copy
from copy import copy
from functools import reduce
from itertools import product

from lexer import to_tokens, TokenType
from reverse_polish_notation import to_rpn
from truth_table import make_truth_table

CONJUNCTION = "/\\"
DISJUNCTION = "\\/"


def make_fcnf(table, variables):
    table = list(filter(lambda x: not x[1], table))
    constituents = []
    for values, _ in table:
        used_variables = []
        for variable, value in zip(variables, values):
            if value:
                used_variables.append(f"!{variable}")
            else:
                used_variables.append(f"{variable}")
        constituents.append("(" + DISJUNCTION.join(used_variables) + ")")
    return CONJUNCTION.join(constituents)


def make_numeric_fcnf(table):
    def tuple_to_int(bool_tuple):
        binary_str = ''.join('1' if b else '0' for b in bool_tuple)
        return int(binary_str, 2)

    table = filter(lambda x: not x[1], table)
    table = map(lambda x: x[0], table)
    table = map(lambda x: tuple_to_int(x), table)
    return f"/\\{tuple(table)}"


def make_index(table):
    def bool_tuple_to_int(bool_tuple):
        binary_str = ''.join('1' if not b else '0' for b in bool_tuple)
        return int(binary_str, 2)

    index = 0
    for values, result in table:
        weight = pow(2, bool_tuple_to_int(values))
        if result:
            index += weight
    return index


def make_fdnf(table, variables):
    table = list(filter(lambda x: x[1], table))
    constituents = []
    for values, _ in table:
        vars2 = []
        for variable, value in zip(variables, values):
            if not value:
                vars2.append(f"!{variable}")
            else:
                vars2.append(f"{variable}")
        constituents.append("(" + CONJUNCTION.join(vars2) + ")")
    return DISJUNCTION.join(constituents)


def get_connectives(connective_tokens):
    connectives = set()
    it = iter(connective_tokens)
    connective = None
    try:
        while True:
            token = next(it)
            if token.type == TokenType.OP_BRACE:
                connective = set()
            elif token.type == TokenType.NEG:
                connective.add(f"!{next(it).value}")
            elif token.type == TokenType.VAR:
                connective.add(token.value)
            elif token.type == TokenType.CL_BRACE:
                connectives.add(tuple(connective))
                connective = None
    except StopIteration:
        pass
    return connectives


def to_name(atom):
    if atom[0] == "!":
        return atom[1:]
    else:
        return atom


def glue_connectives(connectives):
    to_glue = copy(connectives)
    glued = set()

    seen = []
    for connective1 in to_glue:
        connective1 = set(connective1)
        for connective2 in to_glue:
            connective2 = set(connective2)
            if connective1 == connective2 or len(connective1) != len(connective2):
                continue
            if len(connective1.intersection(connective2)) == len(connective1) - 1 and \
               reduce(lambda x, y: x == y, (to_name(atom) for atom in connective1.symmetric_difference(connective2))):
                seen.append(connective1)
                seen.append(connective2)
                glued.add(tuple(connective1.intersection(connective2)))

    for connective in to_glue:
        connective = set(connective)
        if connective not in seen:
            glued.add(tuple(connective))

    if connectives == glued:
        return glued
    else:
        return glue_connectives(glued)


def remove_extra(connectives, table, formulator):

    for connective in connectives:
        filtered_connectives = copy(connectives)
        filtered_connectives.discard(connective)

        if len(filtered_connectives) == 0:
            continue

        formula = formulator(filtered_connectives)

        tokens, variables = to_tokens(formula)
        variables = list(sorted(variables))
        rpn = to_rpn(tokens)
        tt = make_truth_table(rpn, variables)

        if tt == table:
            return remove_extra(filtered_connectives, table, formulator)

    return connectives


def to_dnf(filtered_connectives):
    return "(" + ")\\/(".join(("/\\".join(atom for atom in conn) for conn in filtered_connectives)) + ")"


def to_cnf(filtered_connectives):
    return "(" + ")/\\(".join(("\\/".join(atom for atom in conn) for conn in filtered_connectives)) + ")"


def make_dednf_calc(table, variables):
    fdnf = make_fdnf(table, variables)
    tokens, variables = to_tokens(fdnf)

    connectives = get_connectives(tokens)
    connectives = glue_connectives(connectives)
    connectives = remove_extra(connectives, table, to_dnf)

    return to_dnf(connectives)


def remove_extra_qmc(connectives, glued_connectives):
    table = {glued_connective: set() for glued_connective in glued_connectives}
    for glued_connective in glued_connectives:
        for connective in connectives:
            if all(conn in connective for conn in glued_connective):
                table[glued_connective].add(connective)

    for glued_connective, covered_connectives in table.items():
        table_copy = copy(table)
        table_copy.pop(glued_connective)
        if len(table_copy) != 0:
            all_covered_connectives = reduce(lambda x, y: x.union(y), table_copy.values())
        else:
            all_covered_connectives = []
        if len(all_covered_connectives) == len(connectives):
            return remove_extra_qmc(connectives, {key for key in table_copy.keys()})

    return glued_connectives


def make_dednf_qmc(table, variables):
    fdnf = make_fdnf(table, variables)
    tokens, variables = to_tokens(fdnf)

    connectives = get_connectives(tokens)
    glued_connectives = glue_connectives(connectives)
    glued_connectives = remove_extra_qmc(connectives, glued_connectives)

    return to_dnf(glued_connectives)


# (!x1/\!x2/\x3)\/(!x1/\x2/\!x3)\/(!x1/\x2/\x3)\/(x1/\x2/\!x3)
# (!x1*!x2*x3)+(!x1*x2*!x3)+(!x1*x2*x3)+(x1*x2*!x3)
def make_karnaugh_map(table, variables):
    table = {item[0]: item[1] for item in table}

    def get(x1, x2, x3):
        return int(table[(bool(x1), bool(x2), bool(x3))])

    result = f"     x2   x2  !x2  !x2\n" \
             f"     !x3  x3  x3   !x3\n" \
             f"x1   {get(1, 1, 0)}    {get(1, 1, 1)}   {get(1, 0, 1)}    {get(1, 0, 0)}\n" \
             f"!x1  {get(0, 1, 0)}    {get(0, 1, 1)}   {get(0, 0, 1)}    {get(0, 0, 0)}"

    return result


def make_denf_kv(table, variables, mode):
    if mode == "cnf":
        return _make_denf_kv(table, variables, to_cnf, lambda x: not x)
    elif mode == "dnf":
        return _make_denf_kv(table, variables, to_dnf, lambda x: x)
    else:
        raise RuntimeError("Unknown normal form: " + mode)


def _make_denf_kv(table, variables, formulator, map_checker):
    table_dict = {item[0]: item[1] for item in table}

    def matches(target, variant):
        for i, _ in enumerate(variant):
            if variant[i] is not None and variant[i] != target[i]:
                return False
        return True

    variants = product([None, True, False], repeat=len(variables))
    selected_variants = []
    for variant in variants:
        if all(map_checker(item[1]) for item in table_dict.items() if matches(item[0], variant)) and \
                not any(matches(variant, selected_variant) for selected_variant in selected_variants):
            selected_variants.append(variant)

    connectives = []
    for variant in selected_variants:
        connective = []
        for i, value in enumerate(variant):
            if value is None:
                continue
            connective.append(("" if map_checker(value) else "!") + variables[i])
        connectives.append(connective)

    connectives = set(tuple(connective) for connective in connectives)
    connectives = remove_extra(connectives, table, formulator)
    return formulator(connectives)


def make_decnf_calc(table, variables):
    fcnf = make_fcnf(table, variables)
    tokens, variables = to_tokens(fcnf)

    connectives = get_connectives(tokens)
    connectives = glue_connectives(connectives)
    connectives = remove_extra(connectives, table, to_cnf)

    return to_cnf(connectives)


def make_decnf_qmc(table, variables):
    fcnf = make_fcnf(table, variables)
    tokens, variables = to_tokens(fcnf)

    connectives = get_connectives(tokens)
    glued_connectives = glue_connectives(connectives)
    glued_connectives = remove_extra_qmc(connectives, glued_connectives)

    return to_cnf(glued_connectives)


def make_numeric_fdnf(table):
    def tuple_to_int(bool_tuple):
        binary_str = ''.join('1' if b else '0' for b in bool_tuple)
        return int(binary_str, 2)

    table = filter(lambda x: x[1], table)
    table = map(lambda x: x[0], table)
    table = map(lambda x: tuple_to_int(x), table)
    return f"\\/{tuple(table)}"