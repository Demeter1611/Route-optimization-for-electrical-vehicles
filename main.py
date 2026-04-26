from evrp_instance import EVRPInstance

DATASET_DIRECTORY = './evrp-benchmark-set'
FILENAME = "E-n22-k4.evrp"

problem_instance = EVRPInstance(f"{DATASET_DIRECTORY}/{FILENAME}");

for info_field in problem_instance.info:
    print(f"{info_field}: {problem_instance.info.get(info_field)}")

for node in problem_instance.nodes:
    print(problem_instance.nodes.get(node))
