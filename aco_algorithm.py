from evrp_instance import EVRPInstance
import random

class Ant:
    def __init__(self, instance, max_battery, max_capacity):
        self.instance = instance
        self.max_battery = max_battery
        self.max_capacity = max_capacity

        self.route = []
        self.current_battery = max_battery
        self.current_load = max_capacity

        self.depot_id = next(n_id for n_id, n in self.instance.nodes.items() if n.type == 'depot')
        self.unvisited_customers = {n_id for n_id, n in self.instance.nodes.items() if n.type == 'customer'}
        self.stations = {n_id for n_id, n in self.instance.nodes.items() if n.type == 'station'}

        self.current_node = self.depot_id
        self.route.append(self.current_node)
        self.total_distance = 0.0
    
    def calculate_eta_urgency(self, i, j):
        eta_base = 1.0 / self.instance.get_distance(i, j)
        if self.instance.nodes[j].type == 'station':
            urgency_factor = 1.0 + ((self.max_battery - self.current_battery) / self.max_battery)
            return eta_base * urgency_factor
        return eta_base
    
    def select_next_node(self, pheromones, alpha, beta):
        candidates = []
        probabilities = []
        sum_prob = 0.0

        consumption_rate = float(self.instance.info.get('ENERGY_CONSUMPTION'))
        possible_nodes = self.unvisited_customers.union(self.stations)
        possible_nodes.add(self.depot_id)

        safe_nodes = self.stations.union({self.depot_id});

        for n_id in possible_nodes:
            if n_id == self.current_node:
                continue

            dist_to_candidate = self.instance.get_distance(self.current_node, n_id)
            energy_needed = dist_to_candidate * consumption_rate
            
            node_type = self.instance.nodes[n_id].type
            
            if energy_needed > self.current_battery:
                continue

            if node_type == 'customer':
                min_dist_to_safe = min(self.instance.get_distance(n_id, safe_node) for safe_node in safe_nodes)
                energy_to_safe_node = min_dist_to_safe * consumption_rate

                if (energy_needed + energy_to_safe_node) > self.current_battery:
                    continue

                demand = self.instance.nodes[n_id].demand
                if self.current_load >= demand:
                    candidates.append(n_id)
            
            elif node_type == 'station':
                if self.instance.nodes[self.current_node].type != 'station':
                    candidates.append(n_id)
            
            elif node_type == 'depot':
                candidates.append(n_id)
            
        if not candidates:
            return None
        
        for candidate in candidates:
            tau = pheromones[self.current_node][candidate] ** alpha
            eta = self.calculate_eta_urgency(self.current_node, candidate) ** beta
            prob = tau * eta
            probabilities.append(prob)
            sum_prob += prob
        
        if sum_prob == 0:
            return random.choice(candidates)
        
        r = random.uniform(0, sum_prob)
        cumulative = 0.0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if cumulative >= r:
                return candidates[i]
        
        return candidates[-1]
    
    def move_to(self, next_node):
        dist = self.instance.get_distance(self.current_node, next_node);
        self.total_distance += dist
        self.current_battery -= dist * float(self.instance.info['ENERGY_CONSUMPTION'])

        node_obj = self.instance.nodes[next_node]

        if node_obj.type == 'customer':
            self.current_load -= node_obj.demand
            self.unvisited_customers.discard(next_node)
        elif node_obj.type == 'station':
            self.current_battery = self.max_battery
        elif node_obj.type == 'depot':
            self.current_battery = self.max_battery
            self.current_load = self.max_capacity
        
        self.current_node = next_node
        self.route.append(next_node)


class ACO:
    def __init__(self, instance, num_ants, alpha=1.0, beta=5.0, rho=0.1, n_iter=200):
        self.instance = instance
        self.m = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.n_iter = n_iter

        l_nn = self.instance.get_nearest_neighbor_length()
        n = len([node for node in self.instance.nodes.values() if node.type == 'customer'])
        self.tau_0 = 1.0 / (n * l_nn)

        size = len(self.instance.distance_matrix)
        self.pheromone_matrix = [[self.tau_0 for _ in range(size)] for _ in range(size)]

        self.eta_matrix = [[0.0 for _ in range(size)] for _ in range(size)]
        for i in range(size):
            for j in range(size):
                dist = self.instance.get_distance(i, j)
                if dist > 0:
                    self.eta_matrix[i][j] = 1.0 / dist
    
    def run(self):
        max_battery = float(self.instance.info['ENERGY_CAPACITY'])
        max_capacity = float(self.instance.info['CAPACITY'])

        global_best_route = None
        global_best_distance = float('inf')

        print(f"Pornire ACO. Parametrii: Baterie={max_battery}, Capacitate={max_capacity}")

        for iteration in range(self.n_iter):
            ants = [Ant(self.instance, max_battery, max_capacity) for _ in range(self.m)]
            valid_ants = []

            for ant in ants:
                failed = False
                while ant.unvisited_customers:
                    next_node = ant.select_next_node(self.pheromone_matrix, self.alpha, self.beta)
                    if next_node is None:
                        failed = True
                        break
                    ant.move_to(next_node)
                    
                if not failed:
                    if ant.current_node != ant.depot_id:
                        ant.move_to(ant.depot_id)
                    valid_ants.append(ant)
                
            if not valid_ants:
                print(f"Iteratia {iteration}: toate furnicile au esuat")
                continue
            
            iteration_best_ant = min(valid_ants, key=lambda a: a.total_distance)

            if iteration_best_ant.total_distance < global_best_distance:
                global_best_distance = iteration_best_ant.total_distance
                global_best_route = iteration_best_ant.route.copy()
            
            size = len(self.pheromone_matrix)
            for i in range(size):
                for j in range(size):
                    self.pheromone_matrix[i][j] *= (1.0 - self.rho)
            
            if iteration_best_ant.total_distance > 0:
                delta_tau = 1.0 / iteration_best_ant.total_distance
                route = iteration_best_ant.route
                for idx in range(len(route) - 1):
                    i = route[idx]
                    j = route[idx + 1]
                    self.pheromone_matrix[i][j] += delta_tau
                    self.pheromone_matrix[j][i] += delta_tau
            
            print(f"Iteratia {iteration:3} | Cea mai buna distanta: {global_best_distance:.2f}")
            
        return global_best_route, global_best_distance
    
