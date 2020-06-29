#!/usr/bin/env python
from os import name as osname, path, sep
# from pyomo.opt import SolverStatus, TerminationCondition
# pyomo.util.timing.report_timing() to timeit the pyomo objects.
"""
Caution: Always use the intrinsic functions that are part of the Pyomo package.
from pyomo.environ import * # imports, e.g., pyomo versions of exp, log, etc.)
from math import * # overrides the pyomo versions with math versions
expr = acos(model.x)
"""
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
scippath = path.join(SOLVERS_PATH, 'scipampl601')
winscippath = path.join(SOLVERS_PATH, 'scipampl700.exe')


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


def run_solver(model, stype='scip'):
    if osname == 'nt':
        if stype =='scip':
            solver = pe.SolverFactory('scip6', executable=winscippath, solver_io='nl')
        else:
            solver = pe.SolverFactory("gurobi", solver_io="python", executable=r'C:\gurobi902\win64\bin\gurobi_cl.exe')
    else:
        if stype =='scip':
            solver = pe.SolverFactory('scip6', executable=scippath, solver_io='nl')
        else:
            print('gurobi not installed for linux. exiting')
            raise ValueError

    logging.info('starting solver...')
    results = solver.solve(model, keepfiles=True, tee=True, report_timing=False, load_solutions=False)
    print('solver message:%s' % results.solver.message)
    print('term_cond: %s' % results.solver.termination_condition.__str__())
    print('solver_status: %s' % results.solver.status.__str__())
    log_fpath = solver._log_file
    logging.info('finished running solver...')
    solver_status = results.solver.status.__str__()
    solver_term_cond = results.solver.termination_condition.__str__()
    print('solver_status:', solver_status)
    print('solver_term_cond:', solver_term_cond)

    if solver_term_cond == 'optimal':
        if len(results.solution) > 0:
            model.solutions.load_from(results)
        print('objective value: %d' % model.objective())
        # print(80 * '&')
        # m.display()
        # print(80 * '&')
        # print(80 * '*')
        # print(results)
        # print(80 * '*')
        return results, log_fpath

    else:
        # read the log file created by solver and look for text '<_scon[' to find the failed constr.
        # this logic is specific to scip solver's log.
        print('optimization failed.')
        f = open(log_fpath, 'r')
        lines = f.read()
        pos1 = lines.find('<_scon[')
        pos2 = lines.find(']', pos1)
        try:
            print('failed_constr_num', int(lines[pos1 + 7: pos2]))
            print('SOLVER LOG:\n', '<>'*10, lines, '\n', '<>'*10 )
        except ValueError as e:
            logging.warning('parser failed to find questionable constraint in logfile: %s' % log_fpath)
            pass
        return None, None
    # result_dict['term_cond'] = results.solver.termination_condition.__str__()
    # result_dict['solver_status'] = results.solver.status.__str__()
    # logging.info('solvername #: %s termination_condition: %s; status: %s' %
    #              (slvid, result_dict['term_cond'], result_dict['solver_status']))
    # if result_dict['solver_status'] == 'ok':
    #     print('SUCCESS WITH SOLVER: %s' % slvid)
    #     if len(results.solution) > 0:
    #         pebidobj.model.solutions.load_from(results)
    #     result_dict['succ_solverid'] = slvid


def output_to_display(m, list_varnames):
    from pprint import pprint
    output_dict = {}
    for vname in list_varnames:
        varval = getattr(m, vname)
        output_tuples = []
        for key in varval:
            # output_tuples.append((key + (varval[key].value,)))
            output_tuples.append(([key] + [varval[key].value, ]))
        output_dict[vname] = output_tuples
    pprint(output_dict)
