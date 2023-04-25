from form_generators import make_fdnf, make_fcnf, make_dednf_qmc, make_decnf_qmc
from lexer import to_tokens
from main import print_truth_table
from reverse_polish_notation import to_rpn
from tree import get_tree_string, to_tree


def print_info(title, tt, variables):
    print(title)
    print("-" * 100)
    print_truth_table(tt, variables)
    print("FDNF: ", make_fdnf(tt, variables))
    print("FCNF: ", make_fcnf(tt, variables))
    dednf = make_dednf_qmc(tt, variables)
    print("Dead-end DNF: ", dednf)
    print("Dead-end CNF: ", make_decnf_qmc(tt, variables))


def ods3_pdnf():
    res_tt = [
        ((False, False, False), False,),
        ((False, False, True ), True, ),
        ((False, True,  False), True, ),
        ((False, True,  True ), False,),
        ((True,  False, False), True, ),
        ((True,  False, True ), False,),
        ((True,  True,  False), False,),
        ((True,  True,  True ), True, )
    ]

    tran_tt = [
        ((False, False, False), False,),
        ((False, False, True),  False,),
        ((False, True, False),  False,),
        ((False, True, True),   True, ),
        ((True, False, False),  False,),
        ((True, False, True),   True, ),
        ((True, True, False),   True, ),
        ((True, True, True),    True, )
    ]

    variables = ["A", "B", "P"]

    print_info("ОДС-3 - Результат", res_tt,  variables)
    print_info("ОДС-3 - Перенос",   tran_tt, variables)


if __name__ == '__main__':
    ods3_pdnf()
