import time
import os
import csv

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

# The following function attempts to apply resolution on 2 clauses and returns the resolvent if possible
def resolve_clauses(clause1, clause2):
    for literal in clause1:
        if -literal in clause2:
            resolvent = (clause1 | clause2) - {literal, -literal} 
            if any(-lit in resolvent for lit in resolvent):
                return None # Does not return tautologies 
            return resolvent
    return None  # Resolution isn't possible

# The following function applies the resolution algorithm in order to determine if SAT/UNSAT
def resolution(clauses_set):
    known_clauses = set(frozenset(clause) for clause in clauses_set) # Converts clauses to frozenset to avoid duplicates and improve lookup speed
    while True:
        new_resolvents = set()
        clause_list = list(known_clauses) # Converts the set to a list for accessing elements using indexing
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)): 
                resolvent = resolve_clauses(clause_list[i], clause_list[j]) # Resolve every pair of clauses
                if resolvent is not None:
                    if not resolvent:  # If it reaches an empty clause (contradiction) => UNSAT
                        return False
                    new_resolvents.add(frozenset(resolvent)) # Once again, using frozenset to avoid duplicates
        if new_resolvents.issubset(known_clauses) or not new_resolvents: # If no new clauses were generated
            return True  # No empty clauses(contradictions) => SAT
        known_clauses.update(new_resolvents) # Update known clauses for resolution

# The following function runs the resolution algorithm on all the .cnf files in a folder and outputs the results in a CSV file
def run_resolution(folder_path, results_base_path, solver_name):
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
                        result = resolution(clauses)
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
        print("Usage: python scripts/resolution.py <path_to_cnf_folder>")
        print("Example: python scripts/resolution.py cnfs/small")
    else:
        run_resolution(sys.argv[1], "results/resolution", "resolution")