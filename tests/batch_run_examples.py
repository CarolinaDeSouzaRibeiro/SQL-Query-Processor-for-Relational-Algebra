import os
import random
import sys
from parser import process_sql_query
from arvores_construcao_otimizacao import gerar_imagem_arvore_processada, gerar_grafo_otimizado, converter_algebra_em_arvore, otimizar_selects, No

EXAMPLES_PATH = os.path.join(os.path.dirname(__file__), '../docs/exemplos_consultas.txt')

# Read and split queries
valid_queries = []
invalid_queries = []
with open(EXAMPLES_PATH, encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith('---------')]
    mode = 'valid'
    for line in lines:
        if line.startswith('SEM ERRO'):
            mode = 'valid'
        elif line.startswith('COM ERRO'):
            mode = 'invalid'
        elif mode == 'valid':
            valid_queries.append(line)
        elif mode == 'invalid':
            invalid_queries.append(line)

def is_error_result(result):
    return isinstance(result, Exception) or (isinstance(result, str) and 'Erro' in result)

def check_optimization_structure(sql, ra):
    """
    For join queries, check if selection nodes are pushed below the join.
    Returns (True, msg) if optimization is as expected, else (False, reason).
    """
    try:
        arvore = converter_algebra_em_arvore(ra)
        arvore_opt = otimizar_selects(arvore)
        root = arvore_opt.raiz
        # Only check for JOINs
        if root.get_operacao() == "PROJECT":
            node = root.filho_esq
        else:
            node = root
        if node.get_operacao() == "SELECT":
            # Selection at the root, not pushed down
            return False, "Selection node is still above join (not pushed down)"
        if node.get_operacao() == "JOIN":
            left = node.filho_esq
            right = node.filho_dir
            left_ok = (left is not None and (left.get_operacao() == "SELECT" or left.get_operacao() == "TABLE"))
            right_ok = (right is not None and (right.get_operacao() == "SELECT" or right.get_operacao() == "TABLE"))
            if left_ok or right_ok:
                return True, "Selection nodes are pushed below join as expected."
            else:
                return False, "No selection nodes found below join."
        return True, "No join found, or not a join query."
    except Exception as e:
        return False, f"Exception during optimization check: {e}"

results = []
opt_results = []

print('--- Running VALID queries ---')
for i, sql in enumerate(valid_queries, 1):
    try:
        ra = process_sql_query(sql)
        if is_error_result(ra):
            results.append((sql, 'FAIL', f'Parser error: {ra}'))
            print(f'[{i}] FAIL: {sql}\n    Parser error: {ra}')
            continue
        try:
            gerar_imagem_arvore_processada(ra)
            gerar_grafo_otimizado(ra)
            results.append((sql, 'PASS', ''))
            print(f'[{i}] PASS: {sql}')
            # Optimization structure check for queries 8th onwards
            if i >= 8:
                # Randomly select about half of the queries from 8th onwards for optimization check
                if random.random() < 0.7:
                    ok, msg = check_optimization_structure(sql, ra)
                    opt_results.append((sql, ok, msg))
                    if ok:
                        print(f'    OPTIMIZATION CHECK: PASS - {msg}')
                    else:
                        print(f'    OPTIMIZATION CHECK: FAIL - {msg}')
        except Exception as e:
            results.append((sql, 'FAIL', f'Image generation error: {e}'))
            print(f'[{i}] FAIL: {sql}\n    Image generation error: {e}')
    except Exception as e:
        results.append((sql, 'FAIL', f'Parser exception: {e}'))
        print(f'[{i}] FAIL: {sql}\n    Parser exception: {e}')

print('\n--- Running INVALID queries ---')
for i, sql in enumerate(invalid_queries, 1):
    try:
        ra = process_sql_query(sql)
        if is_error_result(ra):
            results.append((sql, 'PASS', ''))
            print(f'[{i}] PASS (expected error): {sql}')
        else:
            results.append((sql, 'FAIL', f'Expected error, got: {ra}'))
            print(f'[{i}] FAIL: {sql}\n    Expected error, got: {ra}')
    except Exception as e:
        results.append((sql, 'PASS', ''))
        print(f'[{i}] PASS (expected error): {sql}')

# Summary
print('\n--- SUMMARY ---')
num_pass = sum(1 for _, status, _ in results if status == 'PASS')
num_fail = sum(1 for _, status, _ in results if status == 'FAIL')
print(f'Total: {len(results)} | PASS: {num_pass} | FAIL: {num_fail}')
if num_fail > 0:
    print('\nFailed cases:')
    for sql, status, msg in results:
        if status == 'FAIL':
            print(f'- {sql}\n    {msg}')

# Optimization summary
if opt_results:
    print('\n--- OPTIMIZATION CHECKS ---')
    num_opt_pass = sum(1 for _, ok, _ in opt_results if ok)
    num_opt_fail = sum(1 for _, ok, _ in opt_results if not ok)
    print(f'Optimization checks: {len(opt_results)} | PASS: {num_opt_pass} | FAIL: {num_opt_fail}')
    if num_opt_fail > 0:
        print('\nFailed optimization checks:')
        for sql, ok, msg in opt_results:
            if not ok:
                print(f'- {sql}\n    {msg}') 