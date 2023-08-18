import networkx as nx
from nerfs import NERFExtractor # NERF library
from cfg_generator import CFGGenerator # CFG generator class 

class KnowledgeGraphGenerator:

    def __init__(self):
        self.nerf = NERFExtractor() 
        self.relations = ["calls", "assigns", "declares", "contains", "subgraph_of"]

    def extract_entities_relations(self, cfg):
        # Run NERF on CFG nodes to extract entities
        sentences = [node.label for node in cfg.nodes()] 
        entities = self.nerf.extract_entities(sentences)
        
        # Extract relations from edges
        relations = []
        for u, v in cfg.edges():
            if "calls" in u.label:
                relations.append((u.name, "calls", v.name))  
            elif "assigns" in v.label:
                relations.append((u.name, "assigns", v.name))
            #... extract other relations
        
        return entities, relations

    def connect_entities(self, entities, relations):
        # Create knowledge graph
        G = nx.Graph()
        G.add_nodes_from(entities)
        G.add_edges_from(relations)
        return G

    def build_graph(self, cfgs):
        # Build unified graph from list of CFGs
        full_graph = nx.Graph()
        
        for cfg in cfgs:
            entities, relations = self.extract_entities_relations(cfg)
            kg = self.connect_entities(entities, relations) 
            
            # Merge this KG into unified graph
            full_graph = nx.compose(full_graph, kg)  
            
        return full_graph

if __name__ == "__main__":
    generator = CFGGenerator()
    cfgs = [generator.generate("source1.java"), generator.generate("source2.java")]
    
    kg_generator = KnowledgeGraphGenerator()
    knowledge_graph = kg_generator.build_graph(cfgs)