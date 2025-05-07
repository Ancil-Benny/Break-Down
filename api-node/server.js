
import express from 'express';
import { Mistral } from '@mistralai/mistralai';
import dotenv from 'dotenv';
import cors from 'cors';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001; 

const apiKey = process.env.MISTRAL_API_KEY;
if (!apiKey) {
    console.error("API_KEY is not set.");
    process.exit(1);
}

const client = new Mistral({apiKey: apiKey});

// Middleware
app.use(cors()); // Enable CORS 
app.use(express.json()); 

// --- Your Mistral API Call Logic ---
async function breakDownConceptWithMistral(concept) {
    const model = "mistral-large-latest";
    const promptContent = `You are an expert teacher tasked with explaining an academic concept to a student. Your response MUST be a strict JSON object.
Follow these steps for the given 'Concept':
1.  **Standard Definition**: Provide a concise, standard definition of the concept.
2.  **Detailed Explanation**: Explain the concept thoroughly, as if to a student. Use simple language, analogies, and ensure the explanation is easy to grasp beyond just the definition.
3.  **Illustrative Examples**: Offer relevant examples that help clarify the concept.
4.  **Visual Representation (Mermaid Diagrams)**:
    a.  **Evaluate**: First, critically assess if the **current input concept** can be effectively illustrated with one or more diagrams (e.g., flowchart, process diagram, relationship map, component breakdown). Many academic concepts benefit from visual aids.
    b.  **Generate (If Applicable)**: If your evaluation in step 4a is YES, you MUST generate the pure, valid Mermaid code for each beneficial diagram. The 'mermaid' field in the JSON output must be a LIST of strings. **Each string in this list MUST be a complete, self-contained, and independently renderable Mermaid diagram, starting with its diagram type (e.g., \`graph TD\`, \`sequenceDiagram\`).** Do NOT split a single diagram's code across multiple strings. For example, a list might be [\`graph TD; A-->B; B-->C;\`] for one diagram, or [\`graph TD; A-->B;\`, \`sequenceDiagram; X->>Y: Message;\`] for two.
    c.  **Empty List (If Not Applicable)**: If, after careful evaluation in step 4a, you determine that NO diagram can meaningfully represent the **current input concept** (this should be infrequent for complex topics), then the 'mermaid' field must be an empty list \`[]\`.
5.  **Concise Summary**: Provide a brief summary of the key takeaways of the concept.

**Output Format (Strict JSON only):**
Return a single JSON object with the following fields:
-   \`concept\`: The original academic concept provided.
-   \`definition\`: The standard definition (from step 1).
-   \`explanation\`: The detailed explanation (from step 2).
-   \`examples\`: A list of examples (from step 3). Can be an empty list if no examples are suitable.
-   \`mermaid\`: A LIST of strings, where each string is a complete, pure Mermaid diagram (from step 4). This field is REQUIRED. It will be an empty list \`[]\` ONLY if step 4c applies.
-   \`summary\`: The concise summary (from step 5).

**Example of JSON Structure (Illustrative - apply the logic above to the actual input concept):**
\`\`\`json
{
  "concept": "Sample Concept (e.g., Photosynthesis)",
  "definition": "A definition...",
  "explanation": "An explanation...",
  "examples": ["Example 1", "Example 2"],
  "mermaid": ["graph TD; Start --> Process1 --> End;"],
  "summary": "A summary..."
}
\`\`\`
**Concept to process**: ${concept}`;

    try {
     
        const chatResponse = await client.chat.complete({
            model: model,
            messages: [{ role: 'user', content: promptContent }],
            responseFormat: { type: 'json_object' },
        });

        const resultString = chatResponse.choices[0].message.content;
        console.log("DEBUG: Raw model response string before parsing:\n---\n", resultString, "\n---");
        
        const parsedResult = JSON.parse(resultString);
        return parsedResult;

    } catch (error) {
        console.error("ERROR: Error during Mistral API call or JSON parsing.");
        console.error("Error Name:", error.name);
        console.error("Error Message:", error.message);
        if (error.stack) {
            console.error("Error Stack:", error.stack);
        }
        if (error instanceof SyntaxError) {
            console.error("This was likely a JSON parsing error. The string received from the API was not valid JSON.");
        }
        return {
            errorSource: "breakDownConceptWithMistral",
            errorMessage: error.message || "Error processing request with Mistral.",
            originalConcept: concept,
            definition: "",
            explanation: "",
            examples: [],
            mermaid: [],
            summary: "Error processing request.",
        };
    }
}

// --- API Endpoint ---
app.post('/api/breakdown', async (req, res) => {
    const { concept } = req.body;

    if (!concept) {
        console.log("API_VALIDATION_ERROR: Missing 'concept' in request body");
        return res.status(400).json({ error: "Missing 'concept' in request body" });
    }
    console.log(`API_INFO: Received request for concept: "${concept}"`);

    try {
        const resultData = await breakDownConceptWithMistral(concept);
        
        if (resultData.errorSource === "breakDownConceptWithMistral") {
            console.error(`API_ERROR: Error from breakDownConceptWithMistral for concept "${concept}": ${resultData.errorMessage}`);
            return res.status(500).json(resultData);
        }
        // console.log(`API_SUCCESS: Successfully processed concept: "${concept}"`);
        res.json(resultData);
    } catch (error) {
     
        console.error(`API_FATAL_ERROR: Unhandled server error in /api/breakdown for concept "${concept}":`, error);
        res.status(500).json({ error: "Internal server error", details: error.message });
    }
});

app.listen(port, () => {
    console.log(`Node.js backend server running on http://localhost:${port}`);
});