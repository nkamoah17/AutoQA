import openai 
import networkx as nx

class CFGGenerator:

    def __init__(self, openai_key):
        openai.api_key = openai_key

    def extract_structure(self, code):
        prompt = self.get_structure_prompt(code)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024
        )
        return response.choices[0].text.strip()

    def get_structure_prompt(self, code):
        return """
        Analyze and format the following Java code snippet to identify the nested code blocks and indent them to reflect the block structure:

        Input code:
        {code}

        Output structure:
        {structure}
        """
    
    def extract_blocks(self, code, structure):
        prompt = self.get_blocks_prompt(code, structure)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024
        )
        return response.choices[0].text.strip()

    def get_blocks_prompt(self, code, structure):
        return """
        Extract the nested code blocks according to the code structure.
        Input code:
        {code}

        Input structure: 
        {structure}

        Output blocks:
        {blocks}
        """

    def generate_cfg(self, block):
        prompt = self.get_cfg_prompt(block)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024  
        )
        return response.choices[0].text.strip()

    def get_cfg_prompt(self, block):
        return """
        Convert the following code block to a control flow graph (CFG):

        Input code:
        {code}
        
        Output CFG:
        {cfg}
        """

    def fuse_graphs(self, cfgs):
        prompt = self.get_fuse_prompt(cfgs)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt, 
            max_tokens=2048
        )
        return response.choices[0].text.strip()

    def get_fuse_prompt(self, cfgs):
        cfg_text = "\n".join(cfgs)
        return """
        Merge the following CFGs into a complete control flow graph:

        Input CFGs:
        {input_cfgs}

        Output merged CFG: 
        {output_cfg}
        """
    
    def evaluate_cfg(self, generated_cfg, expected_cfg):
        g1 = nx.drawing.nx_pydot.from_pydot(generated_cfg)
        g2 = nx.drawing.nx_pydot.from_pydot(expected_cfg)

        node_correct = len(set(g1.nodes()) & set(g2.nodes())) / len(g2.nodes())
        edge_correct = len(set(g1.edges()) & set(g2.edges())) / len(g2.edges())

        return {
            "node_coverage": node_correct,
            "edge_coverage": edge_correct  
        }

    def generate(self, code, expected_cfg):
        structure = self.extract_structure(code)
        blocks = self.extract_blocks(code, structure)
        cfgs = [self.generate_cfg(b) for b in blocks]
        generated_cfg = self.fuse_graphs(cfgs)
        return self.evaluate_cfg(generated_cfg, expected_cfg)