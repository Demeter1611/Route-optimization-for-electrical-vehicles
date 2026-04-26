from node import Node

class EVRPInstance:
    def __init__(self, file_path):
        self.nodes = {}
        self.info = {}
        self._parse_file(file_path)

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
    
