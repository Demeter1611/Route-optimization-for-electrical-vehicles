from evrp_instance import EVRPInstance
from aco_algorithm import ACO

DATASET_DIRECTORY = './evrp-benchmark-set'
FILENAME = "E-n22-k4.evrp"

problem_instance = EVRPInstance(f"{DATASET_DIRECTORY}/{FILENAME}");

aco_solver = ACO(problem_instance, num_ants=30, n_iter=100)
best_route, best_dist = aco_solver.run()

print(f"Distanta minima: {best_dist:.2f}\nRuta: {best_route}")
