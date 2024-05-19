import re
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch  # Add this import statement for torch

class PromptAnalyzer:
    def __init__(self, baseline_tokens=10, baseline_resource_utilization=1.0):
        self.baseline_tokens = baseline_tokens
        self.baseline_resource_utilization = baseline_resource_utilization
        self.token_regex = re.compile(r'\w+')
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Load a pre-trained model for embeddings
        self.expensive_prompts_db = self.load_expensive_prompts_db()

    def load_expensive_prompts_db(self):
        # Placeholder: Load a database or list of known expensive prompts embeddings
        # In practice, this would load from a persistent storage
        expensive_prompts = [
            "complex mathematical reasoning",
            "nested conditional statements",
            "time scheduling for multiple people with constraints",
        ]
        embeddings = self.model.encode(expensive_prompts)
        # Convert embeddings to PyTorch tensor
        embeddings = torch.tensor(embeddings)
        return embeddings

    def tokenize(self, prompt):
        return self.token_regex.findall(prompt)

    def calculate_token_count(self, tokens):
        return len(tokens)

    def calculate_resource_utilization(self, tokens):
        # Basic placeholder function assuming linear relationship between prompt length and resource utilization
        prompt_length = len(''.join(tokens))
        # Adjust this coefficient based on actual resource utilization characteristics
        utilization_coefficient = 0.01
        return utilization_coefficient * prompt_length

    def semantic_complexity_score(self, prompt):
        prompt_embedding = self.model.encode(prompt, convert_to_tensor=True)
        # Move prompt_embedding to the same device as expensive_prompts_db
        prompt_embedding = prompt_embedding.to(self.expensive_prompts_db.device)
        scores = util.pytorch_cos_sim(prompt_embedding, self.expensive_prompts_db)
        max_score, _ = torch.max(scores, dim=1)  # Find the maximum similarity score
        return max_score.item()  # Return the highest similarity score

    def is_expensive_prompt(self, prompt):
        tokens = self.tokenize(prompt)
        token_count = self.calculate_token_count(tokens)
        resource_utilization = self.calculate_resource_utilization(tokens)
        semantic_score = self.semantic_complexity_score(prompt)

        # Check if the token count, resource utilization, or semantic score exceeds the baseline
        if (token_count > self.baseline_tokens or
            resource_utilization > self.baseline_resource_utilization or
            semantic_score > 0.7):  # Adjust threshold as needed
            return True
        return False

    def complexity_metric(self, prompt):
        tokens = self.tokenize(prompt)
        token_count = self.calculate_token_count(tokens)
        resource_utilization = self.calculate_resource_utilization(tokens)
        semantic_score = self.semantic_complexity_score(prompt)

        # A more sophisticated complexity metric combining all factors
        return token_count * resource_utilization * (1 + semantic_score)

# Example usage:
prompt = ("Explain the plot of Cinderella in a sentence where each word has to begin with the next letter in the alphabet from A to Z, without repeating any letters.")
analyzer = PromptAnalyzer()
print("Is prompt expensive?", analyzer.is_expensive_prompt(prompt))
print("Complexity metric:", analyzer.complexity_metric(prompt))