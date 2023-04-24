# !((!a\/!b)/\(c\/b)/\!(!a/\c))

import json
import textwrap

from form_generators import make_fcnf, make_fdnf, make_numeric_fcnf, make_numeric_fdnf, make_index, make_dednf_calc, \
    make_decnf_calc, make_dednf_qmc, make_decnf_qmc, make_dednf_kv
from lexer import to_tokens
from reverse_polish_notation import to_rpn
from truth_table import make_truth_table

EDUCATION_FILE = "education.json"

HELP_TEXT = ("What do you want to do?\n"
             "\t/q\t\t\tquit\n"
             "\t/fdnf\t\tget full disjunctive normal form\n"
             "\t/dednf\t\tget dead-end disjunctive normal form\n"
             "\t/fcnf\t\tget full conjunctive normal form\n"
             "\t/forms\t\tget numeric and index forms\n"
             "\t/tt\t\t\tget truth table\n"
             "> ")
MODE_CHOICE_TEXT = ("Choose mode:\n"
                    "\t1) Normal\n"
                    "\t2) Education\n"
                    "Your choice: ")
ENTER_FORMULA_TEXT = "Enter your formula: "
FAILED_TO_PARSE_TEXT = "Failed to parse formula: "


def print_truth_table(table, variables):
    print(", ".join(variables), ", f(...)")
    for values, result in table:
        print(", ".join("1" if value else "0" for value in values), ", f(...)=", "1" if result else "0")


def normal_mode():
    def actions_with_formula():
        tt = make_truth_table(rpn, variables)
        index = make_index(tt)
        nfdnf = make_numeric_fdnf(tt)
        nfcnf = make_numeric_fcnf(tt)
        fdnf = make_fdnf(tt, variables)
        fcnf = make_fcnf(tt, variables)
        dednf = make_dednf_calc(tt, variables)
        dednf_qmc = make_dednf_qmc(tt, variables)
        dednf_kv = make_dednf_kv(tt, variables)
        decnf = make_decnf_calc(tt, variables)
        decnf_qmc = make_decnf_qmc(tt, variables)

        print(f"f{index} = {nfdnf} = {nfcnf}")
        print(f"FDNF: {fdnf}")
        print(f"FCNF: {fcnf}")
        print(f"Dead-end DNF (Calc): {dednf}")
        print(f"Dead-end DNF (QMC ): {dednf_qmc}")
        print(f"Dead-end DNF ( KV ): {dednf_kv}")
        print(f"Dead-end CNF (Calc): {decnf}")
        print(f"Dead-end CNF (QMC ): {decnf_qmc}")
        print_truth_table(tt, variables)

        return False

    while True:
        try:
            print(ENTER_FORMULA_TEXT, end="")
            raw_input = input()

            if raw_input == "/q":
                break

            tokens, variables = to_tokens(raw_input)
            variables = list(sorted(variables))
            rpn = to_rpn(tokens)
        except RuntimeError as e:
            print(f"{FAILED_TO_PARSE_TEXT}{e}")
            continue

        while actions_with_formula():
            pass


def education_mode():
    with open(EDUCATION_FILE) as file:
        qa = json.loads(file.read())

    questions = list(map(lambda x: x['q'], qa))
    for i, question in enumerate(questions):
        print(f"{i + 1}. {question}")

    while True:
        qid = input()
        if qid == "/q":
            break
        try:
            qid = int(qid)
        except ValueError as e:
            print(e)
            continue

        try:
            print('\n'.join(textwrap.wrap(qa[qid - 1]['a'], width=150)))
        except IndexError as e:
            print(e)
            continue


def main():
    print(MODE_CHOICE_TEXT, end="")

    match input():
        case "1":
            normal_mode()
        case "2":
            education_mode()


if __name__ == '__main__':
    main()
