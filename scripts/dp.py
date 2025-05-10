import os
import time
import csv
from copy import deepcopy

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

# The following function checks if a clause contains both a literal and its negation (tautology)
def is_tautology(clause):
    return any(-literal in clause for literal in clause) 

# The following function applies resolution on 2 clauses over a variable 
def resolve(clause1, clause2, variable):
    resolvent = list(set([literal for literal in clause1 if literal != variable] + [literal for literal in clause2 if literal != -variable]))
    return resolvent if not is_tautology(resolvent) else None # Only return the resolvent if it's not a tautology

# The following function applies the DP (Davis-Putnam) algorithm in order to determine if SAT/UNSAT
def dp(clauses):
    formula = deepcopy(clauses) # Use a copy to not change the original 
    variables = set(abs(literal) for clause in formula for literal in clause) # Store all the variables in the formula (absolute values)
    while variables:
        var = variables.pop() # Picks a variable and removes it
        # Find the clauses that contain var and -var
        pos_clauses = [clause for clause in formula if var in clause]
        neg_clauses = [clause for clause in formula if -var in clause]
        new_clauses = []
        for c1 in pos_clauses:
            for c2 in neg_clauses:
                resolvent = resolve(c1, c2, var) # Resolve the pairs of conflcting clauses
                if resolvent is not None:
                    new_clauses.append(resolvent)
        formula = [clause for clause in formula if var not in clause and -var not in clause]
        formula.extend(new_clauses)
        if [] in formula:
            return False  # If an empty set is found => UNSAT
        
    return True # SAT otherwise

# The following function runs the DP algorithm on all the .cnf files in a folder and outputs the results in a CSV file
def run_dp(folder_path, results_base_path="results/dp", file_limit=10):
    folder_name = os.path.basename(folder_path.rstrip("/"))
    output_csv = os.path.join(results_base_path, f"{folder_name}_results_dp.csv")
    os.makedirs(results_base_path, exist_ok=True)
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename", "Expected", "Solver Result", "Correct?", "Time (s)"])
        for subfolder in ["sat", "unsat"]:
            expected_result = subfolder.upper()
            subfolder_path = os.path.join(folder_path, subfolder)
            if not os.path.exists(subfolder_path):
                continue
            cnf_files = [f for f in os.listdir(subfolder_path) if f.endswith(".cnf")][:file_limit]
            for filename in cnf_files:
                full_path = os.path.join(subfolder_path, filename)
                try:
                    clauses = parse_cnf_file(full_path, as_sets=True)
                    start_time = time.time()
                    is_sat = dp(clauses)
                    time_taken = time.time() - start_time
                    solver_result = "SAT" if is_sat else "UNSAT"
                    is_correct = "Yes" if solver_result == expected_result else "No"
                    writer.writerow([filename, expected_result, solver_result, is_correct, f"{time_taken:.6f}"])
                except Exception as error:
                    writer.writerow([filename, expected_result, "Error", "No", "0.000000"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python scripts/dp.py <path_to_cnf_folder>")
        print("Example: python scripts/dp.py cnfs/small")
    else:
        run_dp(sys.argv[1])