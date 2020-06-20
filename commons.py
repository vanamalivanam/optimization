#!/usr/bin/env python
from os import name as osname, path, sep

import logging
import sys
from inspect import stack
from pyomo import environ as pe
from pyomo.version.info import version_info as pyomoversion

modpath = path.abspath(__file__)
dir_path = path.dirname(modpath)
sys.path.append(dir_path)
initpathlist = path.realpath(__file__).split(sep)

PROJ_PATH = sep.join(initpathlist[:-1])
EXP = initpathlist[-2]

SOLVERS_PATH = sep.join(initpathlist[:-1] + ['solvers'])
print(SOLVERS_PATH)
exepath = path.join(SOLVERS_PATH, 'scipampl601')
winexepath = path.join(SOLVERS_PATH, 'scipampl700.exe')
print(exepath)

"""
dir(pe.Var)
a = [
    '_ComponentDataClass',
    '_DEFAULT_INDEX_CHECKING_ENABLED',
    '__class__',
    '__contains__',
    '__deepcopy__',
    '__delattr__',
    '__delitem__',
    '__dict__',
    '__dir__',
    '__doc__',
    '__eq__',
    '__format__',
    '__ge__',
    '__getattribute__',
    '__getitem__',
    '__getstate__',
    '__gt__',
    '__hash__',
    '__init__',
    '__init_subclass__',
    '__iter__',
    '__le__',
    '__len__',
    '__lt__',
    '__module__',
    '__ne__',
    '__new__',
    '__reduce__',
    '__reduce_ex__',
    '__repr__',
    '__setattr__',
    '__setitem__',
    '__setstate__',
    '__sizeof__',
    '__slots__',
    '__str__',
    '__subclasshook__',
    '__weakref__',
    '_bounds_init_rule',
    '_bounds_init_value',
    '_constructed',
    '_data',
    '_dense',
    '_domain_init_rule',
    '_domain_init_value',
    '_getitem_when_not_present',
    '_implicit_subsets',
    '_index',
    '_initialize_members',
    '_name',
    '_not_constructed_error',
    '_parent',
    '_pprint',
    '_processUnhashableIndex',
    '_setitem_impl',
    '_setitem_when_not_present',
    '_type',
    '_validate_index',
    '_value_init_rule',
    '_value_init_value',
    'active',
    'add',
    'clear',
    'clear_suffix_value',
    'cname',
    'construct',
    'dim',
    'display',
    'doc',
    'domain',
    'extract_values',
    'fix',
    'flag_as_stale',
    'free',
    'get_suffix_value',
    'get_values',
    'getname',
    'id_index_map',
    'index_set',
    'is_component_type',
    'is_constructed',
    'is_expression_type',
    'is_indexed',
    'items',
    'iteritems',
    'iterkeys',
    'itervalues',
    'keys',
    'local_name',
    'model',
    'name',
    'parent_block',
    'parent_component',
    'pprint',
    'reconstruct',
    'root_block',
    'set_suffix_value',
    'set_value',
    'set_values',
    'to_dense_data',
    'to_string',
    'type',
    'unfix',
    'valid_model_component',
    'values']
"""


def check_expr(exprarg):
    # supports Pyomo 5.6.5
    # pyomo >= 5.6: is_expression_type(); pyomo <=5.5: is_expression()
    if pyomoversion[1] >= 6:
        if exprarg.is_expression_type():
            return True
    elif pyomoversion[1] == 5:
        if exprarg.is_expression():
            return True
    logging.warning('No expression returned by expr_method: %s called by the parent %s' %
                    (stack()[0][3], stack()[1][3]))
    return False


def print_vars_debug(m, vartype=pe.Constraint, c1='$', c2='%'):
    # Displays constraints upper bound lower bound and expression.
    # m.display()
    # debugging: constraints defined in the model.
    # logging.debug(peobj.model.display())
    s1 = c1 * 80
    s2 = c2 * 80
    for con in m.component_map(vartype).itervalues():
        # for con in m.component_map(vartype).itervalues():
        print(s1)
        con.pprint()
        print(s2)


def print_constr_debug(m, constr_name, c1='$', c2='%'):
    # Displays constraints upper bound lower bound and expression.
    # m.display()
    # debugging: constraints defined in the model.
    # logging.debug(peobj.model.display())
    s1 = c1 * 80
    s2 = c2 * 80
    con = getattr(m, constr_name)
    print(s1)
    con.pprint()
    print(s2)


def print_bad_constr(model, log_fpath):
    print_vars_debug(model, pe.Constraint, '^', '#')
    print_vars_debug(model, pe.Var, '&', '+')

    # read the log file created by solver and look for text '<_scon[' to find the failed constr.
    # this logic is specific to scip solver's log.
    f = open(log_fpath, 'r')
    lines = f.read()
    pos1 = lines.find('<_scon[')
    pos2 = lines.find(']', pos1)
    try:
        # result_dict['failed_constr_num'] = int(lines[pos1 + 7: pos2])
        print('@' * 20)
        print(lines)
        print('@' * 30)
    except ValueError as e:
        logging.warning('parser failed to find questionable constraint in logfile: %s' % log_fpath)
        pass


def run_solver(model):
    if osname == 'nt':
        exepath = winexepath
    solver = pe.SolverFactory('scip6', executable=exepath, solver_io='nl')
    if not path.isfile(exepath):
        logging.error('Error in path to solver file.')
    # if osname == 'nt':
    #     logging.error('cannot run solver in windows.')
    #     pass
    logging.info('starting solver...')
    results = solver.solve(model, keepfiles=True, tee=True,
                           report_timing=False, load_solutions=False)
    print('solver message:%s' % results.solver.message)
    print('term_cond: %s' % results.solver.termination_condition.__str__())
    print('solver_status: %s' % results.solver.status.__str__())
    if len(results.solution) > 0:
        model.solutions.load_from(results)
    print('objective value: %d' % model.objective())
    log_fpath = solver._log_file
    # print(80 * '&')
    # m.display()
    # print(80 * '&')
    # print(80 * '*')
    # print(results)
    # print(80 * '*')
    return results, log_fpath


def output_to_display(m, list_varnames):
    from pprint import pprint
    output_dict = {}
    for vname in list_varnames:
        varval = getattr(m, vname)
        output_tuples = []
        for key in varval:
            # output_tuples.append((key + (varval[key].value,)))
            output_tuples.append(([key] + [varval[key].value,]))
        output_dict[vname] = output_tuples
    pprint(output_dict)
