from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv
from mistralai import Mistral
import json

load_dotenv()
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

app = Flask(__name__)

def break_down_concept(concept: str):
    model = "mistral-large-latest"
    prompt = (
        "You are an expert teacher tasked with explaining an academic concept to a student. Your response MUST be a strict JSON object.\n"
        "Follow these steps for the given 'Concept':\n"
        "1.  **Standard Definition**: Provide a concise, standard definition of the concept.\n"
        "2.  **Detailed Explanation**: Explain the concept thoroughly, as if to a student. Use simple language, analogies, and ensure the explanation is easy to grasp beyond just the definition.\n"
        "3.  **Illustrative Examples**: Offer relevant examples that help clarify the concept.\n"
        "4.  **Visual Representation (Mermaid Diagrams)**:\n"
        "    a.  **Evaluate**: First, critically assess if the **current input concept** can be effectively illustrated with one or more diagrams (e.g., flowchart, process diagram, relationship map, component breakdown). Many academic concepts benefit from visual aids.\n"
        "    b.  **Generate (If Applicable)**: If your evaluation in step 4a is YES, you MUST generate the pure, valid Mermaid code for each beneficial diagram. The 'mermaid' field in the JSON output must be a LIST of strings. **Each string in this list MUST be a complete, self-contained, and independently renderable Mermaid diagram, starting with its diagram type (e.g., `graph TD`, `sequenceDiagram`).** Do NOT split a single diagram's code across multiple strings. For example, a list might be `[\"graph TD; A-->B; B-->C;\"]` for one diagram, or `[\"graph TD; A-->B;\", \"sequenceDiagram; X->>Y: Message;\"]` for two.\n"
        "    c.  **Empty List (If Not Applicable)**: If, after careful evaluation in step 4a, you determine that NO diagram can meaningfully represent the **current input concept** (this should be infrequent for complex topics), then the 'mermaid' field must be an empty list `[]`.\n"
        "5.  **Concise Summary**: Provide a brief summary of the key takeaways of the concept.\n\n"
        "**Output Format (Strict JSON only):**\n"
        "Return a single JSON object with the following fields:\n"
        "-   `concept`: The original academic concept provided.\n"
        "-   `definition`: The standard definition (from step 1).\n"
        "-   `explanation`: The detailed explanation (from step 2).\n"
        "-   `examples`: A list of examples (from step 3). Can be an empty list if no examples are suitable.\n"
        "-   `mermaid`: A LIST of strings, where each string is a complete, pure Mermaid diagram (from step 4). This field is REQUIRED. It will be an empty list `[]` ONLY if step 4c applies.\n"
        "-   `summary`: The concise summary (from step 5).\n\n"
        "**Example of JSON Structure (Illustrative - apply the logic above to the actual input concept):**\n"
        "```json\n"
        "{\n"
        "  \"concept\": \"Sample Concept (e.g., Photosynthesis)\",\n"
        "  \"definition\": \"A definition...\",\n"
        "  \"explanation\": \"An explanation...\",\n"
        "  \"examples\": [\"Example 1\", \"Example 2\"],\n"
        "  \"mermaid\": [\"graph TD; Start --> Process1 --> End;\"],\n"
        "  \"summary\": \"A summary...\"\n"
        "```\n"
        f"**Concept to process**: {concept}"
    )
    messages = [
        {"role": "user", "content": prompt}
    ]
    try:
        response = client.chat.complete(
            model=model,
            messages=messages,
            max_tokens=2500, 
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        print("DEBUG: Model response:", result)
        return result
    except Exception as e:
        print(f"Error during API call: {e}") 
        return json.dumps({"error": str(e), "concept": concept, "definition": "", "explanation": "", "examples": [], "mermaid": [], "summary": "Error processing request."})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        concept = request.form.get("concept")
        if (concept):
            result_json_str = break_down_concept(concept)
            data = None 
            try:
                data = json.loads(result_json_str)
               
                if "error" in data and data.get("mermaid", ["not_empty_placeholder_if_list"]) == []: # if error and mermaid is empty list
                   
                    print(f"Error from API processed: {data['error']}")
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e} - Response was: {result_json_str}")
              
                data = {"concept": concept, "definition": "Error decoding response.", "explanation": "", "examples": [], "mermaid": [], "summary": ""}
            except Exception as e:
                print(f"Unexpected error processing result: {e}")
                data = {"concept": concept, "definition": "Unexpected error.", "explanation": "", "examples": [], "mermaid": [], "summary": ""}
            return render_template("index.html", concept=concept, data=data)
    return render_template("index.html", concept=None, data=None)

if __name__ == "__main__":
    app.run(debug=True)
