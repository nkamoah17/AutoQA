import openai
import networkx as nx
import logging
import validators
from functools import lru_cache

logging.basicConfig(level=logging.INFO)

class PromptEngine:

    def __init__(self, openai_key):
        self.openai_key = openai_key

    def generate_prompt(self, template, inputs):
        return template.format(**inputs)

    def call_api(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            temperature=0.5
        )
        return response.choices[0].text.strip()

class CFGEngine:

    def __init__(self, prompt_engine):
        self.prompt_engine = prompt_engine

    def extract_structure(self, code):
        if not validators.java_code(code):
            raise ValueError("Invalid Java code")
        
        template = self.get_structure_template()
        prompt = self.prompt_engine.generate_prompt(template, {"code": code})

        logging.info("Extracting structure")
        output = self.prompt_engine.call_api(prompt)
        return output

    @lru_cache(maxsize=128)
    def get_structure_template(self):
        return """
        Analyze and format the following Java code snippet to identify the nested code blocks and indent them to reflect the block structure:

        Input code:
        {code}

        Output structure:
        {structure}
        """

    def extract_blocks(self, code, structure):
        if not structure:
            raise ValueError("Structure required")
        
        template = self.get_blocks_template()    
        prompt = self.prompt_engine.generate_prompt(template, {"code": code, "structure": structure})
        
        logging.info("Extracting blocks")
        output = self.prompt_engine.call_api(prompt)
        return output

    @lru_cache(maxsize=128)  
    def get_blocks_template(self):
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
        if not block:
            raise ValueError("Code block required")
        
        template = self.get_cfg_template()
        prompt = self.prompt_engine.generate_prompt(template, {"code": block})
        
        logging.info("Generating CFG")
        output = self.prompt_engine.call_api(prompt)
        return output

    @lru_cache(maxsize=128)
    def get_cfg_template(self):
        return """
        Convert the following code block to a control flow graph (CFG):

        Input code:
        {code}

        Output CFG:
        {cfg}
        """

    def fuse_graphs(self, cfgs):
        if not cfgs:
            raise ValueError("CFGs required")
        
        cfg_text = "\n".join(cfgs)
        template = self.get_fuse_template()
        prompt = self.prompt_engine.generate_prompt(template, {"input_cfgs": cfg_text})
        
        logging.info("Fusing CFGs")
        output = self.prompt_engine.call_api(prompt)
        return output

    @lru_cache(maxsize=128)
    def get_fuse_template(self):
        return """
        Merge the following CFGs into a complete control flow graph:

        Input CFGs:
        {input_cfgs}

        Output merged CFG:
        {output_cfg}
        """
    
    def evaluate_cfg(self, generated, expected):
        if not generated:
            raise ValueError("Generated CFG required")
        if not expected:
            raise ValueError("Expected CFG required")

        g1 = nx.drawing.nx_pydot.from_pydot(generated)
        g2 = nx.drawing.nx_pydot.from_pydot(expected)

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