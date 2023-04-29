import json
import textwrap

from form_generators import make_fcnf, make_fdnf, make_numeric_fcnf, make_numeric_fdnf, make_index, make_dednf_calc, \
    make_decnf_calc, make_dednf_qmc, make_decnf_qmc, make_karnaugh_map, make_denf_kv
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
        dednf_kv = make_denf_kv(tt, variables, "dnf")
        decnf = make_decnf_calc(tt, variables)
        decnf_qmc = make_decnf_qmc(tt, variables)
        decnf_kv = make_denf_kv(tt, variables, "cnf")

        print(f"f{index} = {nfdnf} = {nfcnf}")
        print(f"FDNF: {fdnf}")
        print(f"FCNF: {fcnf}")
        print(f"Dead-end DNF (Calc): {dednf}")
        print(f"Dead-end DNF (QMC ): {dednf_qmc}")
        print(f"Dead-end DNF ( KV ): {dednf_kv}")
        print(f"Dead-end CNF (Calc): {decnf}")
        print(f"Dead-end CNF (QMC ): {decnf_qmc}")
        print(f"Dead-end CNF ( KV ): {decnf_kv}")
        if len(variables) == 3:
            karnaugh_map = make_karnaugh_map(tt, variables)
            print(f"Karnaugh map:\n{karnaugh_map}")
        print_truth_table(tt, variables)

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

        actions_with_formula()


if __name__ == '__main__':
    normal_mode()
