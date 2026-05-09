from node import Node

class EVRPInstance:
    def __init__(self, file_path):
        self.nodes = {}
        self.info = {}
        self.distance_matrix = []
        self._parse_file(file_path)
        self._calculate_distances()

    def _parse_file(self, file_path):
        current_section = None
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip();
                if not line or line == "EOF": 
                    continue
                
                if ":" in line and current_section is None:
                    key, val = line.split(":", 1)
                    self.info[key.strip().upper()] = val.strip()
                    continue
                
                if "NODE_COORD_SECTION" in line: 
                    current_section = "coords"; 
                    continue
                if "DEMAND_SECTION" in line: 
                    current_section = "demands"; 
                    continue
                if "STATIONS_COORD_SECTION" in line:
                    current_section = "stations";
                    continue
                if "DEPOT_SECTION" in line:
                    current_section = "depot";
                    continue;
                
                parts = line.split()
                node_id = int(parts[0])

                if current_section == "coords":
                    self.nodes[node_id] = Node(node_id, float(parts[1]), float(parts[2]))
                elif node_id in self.nodes:    
                    if current_section == "demands":
                        self.nodes[node_id].demand = float(parts[1])
                    elif current_section == "stations":
                        self.nodes[node_id].type = 'station'
                    elif current_section == "depot":
                        self.nodes[node_id].type = 'depot'
    
    def _calculate_distances(self):
        size = max(self.nodes.keys()) + 1
        self.distance_matrix = [[0.0] * size for _ in range(size)]

        for i in self.nodes:
            for j in self.nodes:
                if i != j:
                    self.distance_matrix[i][j] = self.nodes[i].distance_to(self.nodes[j])
    
    def get_distance(self, i, j):
        return self.distance_matrix[i][j]

    def get_nearest_neighbor_length(self):
        unvisited = [n_id for n_id, node in self.nodes.items() if node.type == 'customer']
        depot_id = next(n_id for n_id, node in self.nodes.items() if node.type == 'depot')

        total_length = 0
        current_node = depot_id

        max_capacity = float(self.info['CAPACITY'])
        current_load = 0

        while unvisited:
            next_node = None
            min_dist = float('inf')

            for candidate in unvisited:
                dist = self.get_distance(current_node, candidate)
                if dist < min_dist and current_load + self.nodes[candidate].demand <= max_capacity:
                    min_dist = dist
                    next_node = candidate
            
            if next_node:
                total_length += min_dist
                current_load += self.nodes[next_node].demand
                unvisited.remove(next_node)
                current_node = next_node
            else:
                total_length += self.get_distance(current_node, depot_id)
                current_node = depot_id
                current_load = 0
            
        total_length += self.get_distance(current_node, depot_id)
        return total_length