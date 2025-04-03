import os
import json
import webbrowser
from datetime import datetime
from dotenv import load_dotenv
from mistralai import Mistral

# Import knowledge base
from knowledge_base import KnowledgeBase

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

kb = KnowledgeBase()

def process_query(query: str):

    model = "mistral-large-latest"
    
    # Build prompt from knowledge base
    base_prompt = kb.build_prompt()
    
    # Add the user query to the prompt
    full_prompt = f"{base_prompt}\n\n## User Query:\n{query}"
    
    # Log the start of the API call
    print(f"Sending query to Mistral API using model: {model}")
    start_time = datetime.now()
    
    # Call Mistral API
    try:
        messages = [
            {"role": "user", "content": full_prompt}
        ]

        response = client.chat.complete(
            model=model,
            messages=messages,
            max_tokens=2000,
            response_format={"type": "json_object"}  
        )
        
        # Calculate response time
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        print(f"Response received in {response_time:.2f} seconds")

        # Extract response content
        content = response.choices[0].message.content
        
        # Parse JSON response
        parsed_json = json.loads(content)
        
        # Save the response to output.txt
        formatted_output = json.dumps(parsed_json, indent=4)
        with open("output.txt", "w") as f:
            f.write(formatted_output)
        
        print(f"Response saved to output.txt")
        print("\nResponse:")
        print(json.dumps(parsed_json, indent=2))
        
    except Exception as e:
        print(f"Error calling Mistral API: {str(e)}")
        raise

def break_down_concept(concept: str):

    model = "mistral-large-latest"
    
  
    base_prompt = kb.build_prompt()
    
    # Add the concept to the prompt with explicit instructions to follow the schema exactly
    full_prompt = f"{base_prompt}\n\n## Academic Concept to Break Down:\n{concept}\n\nPlease provide a comprehensive breakdown of this concept in the EXACT JSON schema format shown above. Make sure to include the following fields exactly as shown in the schema: concept, simple_definition, detailed_explanation, key_components, analogies, examples, common_misconceptions, related_concepts, and diagrams with title, description, type, and mermaid_code. Include Mermaid diagram code for visualizing key aspects. Make it easy to understand for students."
    
    # Log the start of the API call
    print(f"Breaking down concept: '{concept}'")
    print(f"Sending request to Mistral API using model: {model}")
    start_time = datetime.now()
    
    # Call Mistral API
    try:
        messages = [
            {"role": "user", "content": full_prompt}
        ]

        response = client.chat.complete(
            model=model,
            messages=messages,
            max_tokens=4000, 
            response_format={"type": "json_object"} 
            
        )
        
        # Calculate response time
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        print(f"Response received in {response_time:.2f} seconds")

        # Extract response content
        content = response.choices[0].message.content
        
        # Parse JSON response
        parsed_json = json.loads(content)
        
        # Save the response to output.txt
        formatted_output = json.dumps(parsed_json, indent=4)
        with open("output.txt", "w") as f:
            f.write(formatted_output)
        
        print(f"Concept breakdown saved to output.txt")
        print("\nConcept Breakdown:")
        print(json.dumps(parsed_json, indent=2))
        
        # Check if we need to extract from a nested "response" structure
        if "response" in parsed_json and not parsed_json.get("concept"):
            print("Model returned incorrect format. Attempting to extract response...")
            
            # Create a proper concept breakdown from the response
            extracted_data = {
                "concept": concept,
                "simple_definition": parsed_json["response"].get("answer", ""),
                "detailed_explanation": parsed_json["response"].get("additional_info", ""),
                "key_components": [],
                "analogies": [],
                "examples": [],
                "common_misconceptions": [],
                "related_concepts": parsed_json["response"].get("sources", []),
                "diagrams": []
            }
            
            # Extract diagram if present
            if "diagram" in parsed_json["response"]:
                diagram_code = parsed_json["response"]["diagram"]
                # Remove markdown code block markers if present
                diagram_code = diagram_code.replace("```mermaid", "").replace("```", "").strip()
                
                extracted_data["diagrams"].append({
                    "title": "Quantum Superposition Visualization",
                    "description": "Visual representation of quantum superposition concept",
                    "type": "flowchart",
                    "mermaid_code": diagram_code
                })
                
            return extracted_data
        
        return parsed_json
        
    except Exception as e:
        print(f"Error calling Mistral API: {str(e)}")
        raise

def generate_html_page(concept_data):
    """
    Generate an HTML page from the concept breakdown data, including Mermaid diagrams.
    
    Args:
        concept_data: Dictionary containing the concept breakdown
        
    Returns:
        The path to the generated HTML file
    """
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{concept} - Simplified Explanation</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .header {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 2.5em;
        }}
        h2 {{
            color: #3498db;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        h3 {{
            color: #2980b9;
            margin-top: 25px;
        }}
        .simple-def {{
            font-size: 1.3em;
            font-weight: normal;
            background-color: #edf7ff;
            padding: 20px;
            border-radius: 8px;
            margin: 20px auto;
            max-width: 90%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .section {{
            background-color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }}
        .key-component {{
            background-color: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #2c3e50;
            border-radius: 4px;
        }}
        .analogy {{
            background-color: #e8f4fc;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #3498db;
        }}
        .example {{
            background-color: #eafaf1;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border-left: 4px solid #2ecc71;
        }}
        .misconception {{
            background-color: #fff5eb;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #e67e22;
        }}
        .related {{
            display: inline-block;
            background-color: #eaf2f8;
            padding: 8px 15px;
            margin: 8px;
            border-radius: 20px;
            font-size: 0.9em;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}
        .diagram-container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin: 25px 0;
        }}
        .diagram-explanation {{
            padding: 15px;
            background-color: #f5f7fa;
            border-left: 4px solid #3498db;
            margin-top: 15px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{concept}</h1>
        <div class="simple-def">{simple_definition}</div>
    </div>

    <div class="section">
        <h2>Breaking It Down</h2>
        <p>{detailed_explanation}</p>
    </div>

    <div class="section">
        <h2>Key Components</h2>
        {key_components_html}
    </div>

    <div class="section">
        <h2>Visual Explanations</h2>
        {diagrams_html}
    </div>

    <div class="section">
        <h2>Helpful Analogies</h2>
        {analogies_html}
    </div>

    <div class="section">
        <h2>Real-World Examples</h2>
        {examples_html}
    </div>

    <div class="section">
        <h2>Common Misconceptions</h2>
        {misconceptions_html}
    </div>

    <div class="section">
        <h2>Related Concepts</h2>
        <p>Explore these concepts to deepen your understanding:</p>
        <div>
            {related_concepts_html}
        </div>
    </div>

    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            securityLevel: 'loose',
            theme: 'default' 
        }});
        
        // Additional initialization for error handling
        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(function() {{
                const diagrams = document.querySelectorAll('.mermaid');
                diagrams.forEach(function(diagram) {{
                    if (!diagram.querySelector('svg')) {{
                        diagram.innerHTML = '<div style="color: red; padding: 10px; background: #ffeeee; border: 1px solid #ffcccc;">Error rendering diagram</div>' + diagram.innerHTML;
                    }}
                }});
            }}, 1000);
        }});
    </script>
</body>
</html>
"""

    # Process the content for HTML
    key_components_html = ""
    for item in concept_data.get("key_components", []):
        key_components_html += f'<div class="key-component">{item}</div>'
    
    analogies_html = ""
    for item in concept_data.get("analogies", []):
        analogies_html += f'<div class="analogy">{item}</div>'
    
    examples_html = ""
    for item in concept_data.get("examples", []):
        examples_html += f'<div class="example">{item}</div>'
    
    misconceptions_html = ""
    for item in concept_data.get("common_misconceptions", []):
        misconceptions_html += f'<div class="misconception">{item}</div>'
    
    related_concepts_html = ""
    for item in concept_data.get("related_concepts", []):
        related_concepts_html += f'<span class="related">{item}</span>'

    # Create diagrams section
    diagrams_html = ""
    if "diagrams" in concept_data and concept_data["diagrams"]:
        for i, diagram in enumerate(concept_data["diagrams"]):
            diagram_id = f"diagram-{i}"
            title = diagram.get('title', 'Diagram')
            description = diagram.get('description', '')
            mermaid_code = diagram.get('mermaid_code', '')
            
            # Ensure we have cleaned mermaid code
            if mermaid_code:
                mermaid_code = clean_mermaid_code(mermaid_code)
            
            diagrams_html += f"""
            <div class="diagram-container">
                <h3>{title}</h3>
                <div class="mermaid" id="{diagram_id}">
{mermaid_code}
                </div>
                <div class="diagram-explanation">
                    {description}
                </div>
            </div>
            """

    # Fill in the template
    html_content = html_template.format(
        concept=concept_data.get("concept", "Academic Concept"),
        simple_definition=concept_data.get("simple_definition", ""),
        detailed_explanation=concept_data.get("detailed_explanation", ""),
        key_components_html=key_components_html,
        analogies_html=analogies_html,
        examples_html=examples_html,
        misconceptions_html=misconceptions_html,
        related_concepts_html=related_concepts_html,
        diagrams_html=diagrams_html
    )

    # Save to an HTML file
    if not os.path.exists("output"):
        os.makedirs("output")
        
    concept_filename = concept_data.get("concept", "concept").lower().replace(" ", "_")
    html_file = os.path.join("output", f"{concept_filename}.html")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_file

def clean_mermaid_code(mermaid_code):
    """Clean mermaid code to prevent common syntax errors"""
    if not mermaid_code:
        return "flowchart TD\nA[No diagram available]"
    
    # Remove any markdown code block markers
    if "```" in mermaid_code:
        mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
    
    # Fix common syntax issues
    mermaid_code = mermaid_code.replace("=>", "-->")
    mermaid_code = mermaid_code.replace("->>", "-->")
    
    # Remove semicolons which can cause issues
    lines = mermaid_code.strip().split('\n')
    clean_lines = []
    for line in lines:
        if line.strip().endswith(';'):
            line = line[:-1]
        clean_lines.append(line)
    
    return '\n'.join(clean_lines)

def create_diagram_html(diagrams_data, concept):
    """Create a simple HTML page to display the mermaid diagrams."""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{concept} Diagrams</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        h2 {{
            color: #3498db;
            margin-top: 30px;
        }}
        .diagram-container {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin: 30px 0;
        }}
        .description {{
            background-color: #f5f7fa;
            padding: 15px;
            border-left: 3px solid #3498db;
            margin-top: 15px;
        }}
        .error-container {{
            color: #e74c3c;
            background-color: #fadbd8;
            padding: 10px;
            border-left: 3px solid #e74c3c;
            margin-top: 15px;
            display: none;
        }}
        .mermaid-code {{
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            margin-top: 10px;
            white-space: pre-wrap;
            display: none;
        }}
    </style>
</head>
<body>
    <h1>{concept}</h1>
    <p>Visual diagrams explaining {concept}</p>
    {diagrams_html}
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            securityLevel: 'loose',
            theme: 'default'
        }});
        
        // Error handling for diagrams
        window.addEventListener('load', function() {{
            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        }});
    </script>
</body>
</html>"""

    # Create diagrams HTML
    diagrams_html = ""
    
    # Handle different response structures that might come from the model
    diagrams = []
    
    # Case 1: Standard format from our prompt template
    if isinstance(diagrams_data, dict) and "diagrams" in diagrams_data:
        diagrams = diagrams_data["diagrams"]
    
    # Case 2: Direct list of diagrams
    elif isinstance(diagrams_data, list):
        diagrams = diagrams_data
    
    # Case 3: Key-value pairs where keys are titles (like in your diagrams_output.json)
    elif isinstance(diagrams_data, dict):
        for title, data in diagrams_data.items():
            if isinstance(data, dict) and "mermaid_code" in data:
                diagrams.append({
                    "title": title,
                    "description": data.get("description", ""),
                    "mermaid_code": data.get("mermaid_code", "")
                })
    
    for i, diagram in enumerate(diagrams):
        title = diagram.get("title", f"Diagram {i+1}")
        description = diagram.get("description", "")
        mermaid_code = clean_mermaid_code(diagram.get("mermaid_code", ""))
        
        diagrams_html += f"""
        <div class="diagram-container">
            <h2>{title}</h2>
            <div class="mermaid">
{mermaid_code}
            </div>
            <div class="description">{description}</div>
        </div>"""

    # Create output directory if it doesn't exist
    if not os.path.exists("output"):
        os.makedirs("output")
    
    # Generate HTML file
    file_name = concept.lower().replace(" ", "_") + "_diagrams.html"
    html_file = os.path.join("output", file_name)
    
    # Fill template and save file
    html_content = html_template.format(
        concept=concept,
        diagrams_html=diagrams_html
    )
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_file

def main():
    """Main function to break down an academic concept and create visualizations."""
    # Get concept from user input
    concept = input("Enter an academic concept to break down: ")
    if not concept.strip():
        concept = "Quantum Superposition"  # Default concept
    
    print(f"Breaking down concept: '{concept}'")
    
    # Get concept breakdown with diagrams in a single call
    concept_data = break_down_concept(concept)
    
    # Clean up and prepare diagram code
    if "diagrams" in concept_data:
        for diagram in concept_data["diagrams"]:
            if "mermaid_code" in diagram:
                diagram["mermaid_code"] = clean_mermaid_code(diagram["mermaid_code"])
    
    # Generate full concept page with cleaned diagrams
    html_file = generate_html_page(concept_data)
    print(f"Concept breakdown page created: {html_file}")
    
    # Open in browser
    full_path = os.path.abspath(html_file)
    print(f"Opening {full_path} in browser")
    webbrowser.open(f"file:///{full_path}")

if __name__ == "__main__":
    main()