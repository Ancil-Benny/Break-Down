import os
import json
from typing import Dict, Any

class KnowledgeBase:
    def __init__(self, kb_directory: str = "knowledge_base"):
        self.kb_directory = kb_directory
        if not os.path.exists(kb_directory):
            os.makedirs(kb_directory)
            self._initialize_defaults()
        self._load_documents()
    
    def _initialize_defaults(self):
        """Initialize the knowledge base with default components."""
        defaults = {
            "schema": {
                "concept": "Name of the academic concept",
                "simple_definition": "A brief, easy-to-understand definition",
                "detailed_explanation": "A comprehensive explanation in simple terms",
                "key_components": ["List of essential parts or ideas"],
                "analogies": ["Helpful comparisons to familiar concepts"],
                "examples": ["Real-world applications or instances"],
                "common_misconceptions": ["Frequently misunderstood aspects"],
                "related_concepts": ["Other relevant topics worth exploring"],
                "diagrams": [
                    {
                        "title": "Title of the diagram",
                        "description": "What this diagram shows",
                        "type": "flowchart/sequence/etc",
                        "mermaid_code": "The Mermaid code for the diagram"
                    }
                ]
            },
            "system": {
                "prompt": "You are an educational assistant specialized in breaking down complex academic concepts into easily understandable explanations for students."
            },
            "instructions": {
                "instructions": [
                    "Break down concepts into simple language that a high school student can understand",
                    "Use clear analogies that relate to everyday experiences",
                    "Provide concrete examples that illustrate the concept",
                    "Address common misconceptions students might have",
                    "Create visual representations using Mermaid diagrams"
                ]
            },
            "diagrams": {
                "description": "Create clear, educational diagrams that help visualize academic concepts.",
                "guidelines": [
                    "Use flowcharts for processes and sequences",
                    "Use class diagrams for relationships and hierarchies",
                    "Use sequence diagrams for interactions over time",
                    "Keep diagrams simple and focused"
                ],
                "output_format": {
                    "diagrams": [
                        {
                            "title": "Title of the diagram",
                            "description": "What this diagram shows",
                            "mermaid_code": "The complete Mermaid code"
                        }
                    ]
                }
            },
            "examples": {
                "diagrams": [
                    {
                        "title": "Basic Process Flow",
                        "description": "Shows the main steps of a process",
                        "mermaid_code": """flowchart LR
    A[Input] --> B{Process}
    B --> C[Output 1]
    B --> D[Output 2]"""
                    }
                ]
            }
        }
        
        # Save default components
        for doc_id, content in defaults.items():
            self.add_document(doc_id, content)
    
    def _load_documents(self):
        """Load all documents from the knowledge base directory."""
        self.documents = {}
        if not os.path.exists(self.kb_directory):
            return
            
        for filename in os.listdir(self.kb_directory):
            if filename.endswith('.json'):
                file_path = os.path.join(self.kb_directory, filename)
                try:
                    with open(file_path, 'r') as f:
                        doc_id = filename.replace('.json', '')
                        self.documents[doc_id] = json.load(f)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
    
    def add_document(self, doc_id: str, content: Dict[str, Any]) -> bool:
        """Add a new document to the knowledge base."""
        file_path = os.path.join(self.kb_directory, f"{doc_id}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(content, f, indent=2)
            self.documents[doc_id] = content
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False
    
    def build_prompt(self):
        """Build a prompt for concept breakdown focusing on simplicity."""
        # Load required components
        schema = self.documents.get("schema", {})
        system_prompt = self.documents.get("system", {}).get("prompt", "")
        
        # Create a more focused prompt
        prompt = f"""## System Instruction:
{system_prompt}

I need you to break down the following academic concept in a way that's easy for anyone to understand.

## Output Format:
{json.dumps(schema, indent=2)}

## IMPORTANT GUIDELINES:
1. Start with a simple definition anyone can understand
2. Provide a clear, detailed explanation that breaks down complex ideas into simple terms
3. List key components with brief explanations of each
4. Include helpful analogies that relate to everyday experiences
5. Give concrete examples showing how this concept applies in real life
6. Address common misconceptions students might have
7. Include related concepts for further exploration
8. Create mermaid diagrams to visualize the concept (REQUIRED)

For diagrams:
- Use flowcharts for processes
- Use class diagrams for relationships 
- Use sequence diagrams for step-by-step interactions
- Make sure the mermaid code is valid and will render correctly
- Do NOT use markdown code blocks (```) in your response

Make your explanation suitable for someone who has no prior knowledge of this subject.
"""
        
        return prompt
    
    def get_diagram_prompt(self, concept: str) -> str:
        """Build a prompt for getting concept diagrams."""
        diagrams = self.documents.get("diagrams", {})
        examples = self.documents.get("examples", {}).get("diagrams", [])
        
        prompt = f"""Create visual diagrams for: "{concept}"

VERY IMPORTANT: Your Mermaid code must follow these strict requirements:
1. Use ONLY these diagram types:
   - flowchart LR (for left-to-right flow processes)
   - flowchart TD (for top-down processes)
   - classDiagram (for showing relationships)
   - sequenceDiagram (for showing step sequences)
   - pie (for showing proportions)

2. Follow these syntax rules EXACTLY:
   - Start with the diagram type declaration (e.g., "flowchart LR")
   - For flowcharts, use A, B, C, etc. for node IDs
   - Use --> for arrows, not => or ->>
   - Use [] for rectangular nodes, () for round nodes, {{}} for diamond nodes
   - Keep syntax minimal and avoid complex styling
   - NO markdown code blocks (```) in your response

Guidelines:
{chr(10).join(f"- {g}" for g in diagrams.get('guidelines', []))}

For each diagram, provide:
1. A clear title
2. A description explaining what the diagram shows
3. The complete Mermaid code (following the syntax rules above)

Return EXACTLY this JSON structure:
{json.dumps(diagrams.get('output_format', {}), indent=2)}

Example diagram:
{json.dumps(examples[0] if examples else {}, indent=2)}
"""
        return prompt