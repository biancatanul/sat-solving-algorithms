import os
import csv
import time

# The following function parses the DIMACS CNF file into a list of clauses
def parse_cnf_file(file_path, as_sets=False):
    clauses_set = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith(('c', 'p', '%')):
                continue  # Skip comments, problem line, empty lines, or '%'
            try:
                literals = list(map(int, line.split()))
                if literals and literals[-1] == 0:
                    literals = literals[:-1]  # Remove trailing 0
                if literals:
                    clauses_set.append(set(literals) if as_sets else literals)
            except ValueError:
                continue  # Skip invalid lines
    return clauses_set

# The following function simplifies the formula based on the current variable assignment
def simplify(clauses, current_assignment):
    new_clauses = []
    for clause in clauses:
        if any(literal in current_assignment for literal in clause):
            continue  # Clause is satisfied
        new_clause = [literal for literal in clause if -literal not in current_assignment]
        if not new_clause:
            return None  # Empty clause => conflict
        new_clauses.append(new_clause)
    return new_clauses

# The following function returns unit clauses (if such exist)
def find_unit_clause(clauses):
    for clause in clauses:
        if len(clause) == 1:
            return clause[0]
    return None

# The following function returns a list of literals that appear in only positive or negative form (pure literals)
def find_pure_literals(clauses):
    counter = {}
    for clause in clauses:
        for literal in clause:
            counter[literal] = counter.get(literal, 0) + 1
    pure_literals = []
    for lit in counter:
        if -lit not in counter:
            pure_literals.append(lit)
    return pure_literals

# The following function uses a naive strategy to select a literal to assign next
def choose_literal(clauses):
    for clause in clauses:
        for lit in clause:
            return abs(lit)
    return None

# The following function applies the DPLL (Davis-Putnam_Logemann-Loveland) algorithm in order to determine if SAT/UNSAT
def dpll(clauses, current_assignment):
    clauses = simplify(clauses, current_assignment)
    if clauses is None:
        return False, None # Conflict found => UNSAT
    if not clauses:
        return True, current_assignment # No more clauses left => SAT

    # Apply the one literal rule (unit propagation)
    unit_literal = find_unit_clause(clauses)
    while unit_literal is not None:
        current_assignment.append(unit_literal)
        clauses = simplify(clauses, [unit_literal])
        if clauses is None:
            return False, None
        unit_literal = find_unit_clause(clauses)

    # Apply the pure literal rule
    pure_literals = find_pure_literals(clauses)
    for literal in pure_literals:
        current_assignment.append(literal)
    clauses = simplify(clauses, pure_literals)
    if clauses is None:
        return False, None

    # Choose a variable to split on
    variable = choose_literal(clauses)
    if variable is None:
        return True, current_assignment

    # Assign true or false to the chosen variable
    for value in [variable, -variable]:
        sat, result = dpll([clause[:] for clause in clauses], current_assignment + [value])
        if sat:
            return True, result
        
    return False, None # Go back if no assignment results in SAT

# The following function runs the DPLL algorithm on all the .cnf files in a folder and outputs the results in a CSV file
def run_dpll(folder_path, results_base_path, solver_name):
    folder_name = os.path.basename(folder_path.rstrip("/"))
    output_csv = os.path.join(results_base_path, f"{folder_name}_results_{solver_name}.csv")
    os.makedirs(results_base_path, exist_ok=True)
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Expected", "Solver Result", "Correct?", "Time (s)"])
        for subfolder in ["sat", "unsat"]:
            expected_result = subfolder.upper()
            subfolder_path = os.path.join(folder_path, subfolder)
            if not os.path.exists(subfolder_path):
                continue
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".cnf"):
                    full_path = os.path.join(subfolder_path, filename)
                    try:
                        clauses = parse_cnf_file(full_path, as_sets=(solver_name == "resolution"))
                        start_time = time.time()
                        result = dpll(clauses, [])
                        time_taken = time.time() - start_time
                        is_sat = result if isinstance(result, bool) else result[0]
                        solver_result = "SAT" if is_sat else "UNSAT"
                        is_correct = "Yes" if solver_result == expected_result else "No"
                        writer.writerow([filename, expected_result, solver_result, is_correct, f"{time_taken:.6f}"])
                    except Exception as error:
                        writer.writerow([filename, expected_result, "Error", "No", "0.000000"])
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python scripts/dpll.py <path_to_cnf_folder>")
        print("Example: python scripts/dpll.py cnfs/small")
    else:
        run_dpll(sys.argv[1], "results/dpll", "dpll")