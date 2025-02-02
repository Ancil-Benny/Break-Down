import express from 'express';
import Groq from 'groq-sdk';
import dotenv from 'dotenv';

dotenv.config();

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'],
});

/**
 * @param {string} input - The concept for which to generate diagrams.
 * @returns {Promise<Object>} - The JSON object with generated diagrams.
 */
async function processConcept(input) {
  const simplifyResponse = await client.chat.completions.create({
    messages: [
      {
        role: 'system',
        content: `You are an expert at converting complex concepts into multiple Mermaid diagrams.
Respond ONLY with a valid JSON object in the exact following format:
{
  "diagrams": [
    {
      "title": "<TITLE_FOR_DIAGRAM_1>",
      "code": "<MERMAID_CODE_FOR_DIAGRAM_1>"
    },
    {
      "title": "<TITLE_FOR_DIAGRAM_2>",
      "code": "<MERMAID_CODE_FOR_DIAGRAM_2>"
    }
    // You may include more diagrams if necessary.
  ]
}

Here is a sample example:
{
  "diagrams": [
    {
      "title": "Photosynthesis Overview",
      "code": "graph TD; Light-->Chlorophyll; Chlorophyll-->Photosynthesis;"
    },
    {
      "title": "Chloroplast Structure",
      "code": "graph LR; Stroma-->Grana; Grana-->Thylakoid_Membranes;"
    }
  ]
}

Do not include any additional text, markdown formatting, or explanations.`
      },
      {
        role: 'user',
        content: `Generate Mermaid diagrams for the concept: "${input}".`
      }
    ],
    model: 'llama-3.3-70b-versatile',
    response_format: { 
      type: "json_object" 
    },
    max_tokens: 4096
  });


  let simplifiedJson;
  try {
    simplifiedJson = JSON.parse(simplifyResponse.choices[0].message.content);
  } catch (error) {
    console.error("Failed to parse JSON response:", error);
    throw error;
  }
  return simplifiedJson;
}

const app = express();
const PORT = process.env.PORT || 3000;


app.use(express.urlencoded({ extended: true }));


app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Mermaid Diagram Generator</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        form { margin-bottom: 20px; }
        input[type="text"] { padding: 8px; width: 300px; }
        button { padding: 8px 12px; }
      </style>
    </head>
    <body>
      <h1>Mermaid Diagram Generator</h1>
      <form action="/generate" method="POST">
        <label for="concept">Enter a concept:</label>
        <input type="text" id="concept" name="concept" required>
        <button type="submit">Generate</button>
      </form>
    </body>
    </html>
  `);
});


app.post('/generate', async (req, res) => {
  const { concept } = req.body;
  try {
    const result = await processConcept(concept);
    let diagramsHtml = '';
    result.diagrams.forEach((diagram, index) => {
      diagramsHtml += `<h2>Diagram ${index + 1} - ${diagram.title}</h2>
      <div class="mermaid">
        ${diagram.code}
      </div>`;
    });

    res.send(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Generated Mermaid Diagrams</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          h2 { margin-top: 40px; }
          .mermaid { background: #f4f4f4; padding: 10px; border: 1px solid #ccc; }
          a { text-decoration: none; color: blue; }
        </style>
        <!-- Load Mermaid from CDN -->
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
          // Initialize Mermaid after the page loads
          document.addEventListener('DOMContentLoaded', function() {
            mermaid.initialize({ startOnLoad: true });
          });
        </script>
      </head>
      <body>
        <h1>Mermaid Diagrams for Concept: ${concept}</h1>
        ${diagramsHtml}
        <br/>
        <a href="/">&#8592; Go back</a>
      </body>
      </html>
    `);
  } catch (error) {
    console.error("Error processing concept:", error);
    res.status(500).send("Internal Server Error. Please try again later.");
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});