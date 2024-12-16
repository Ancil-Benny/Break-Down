import Groq from 'groq-sdk';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'],
});

// Process user input
async function processConcept(input) {
  try {
    // Step 1: Simplify concept with LLaMA
    const simplifyResponse = await client.chat.completions.create({
      messages: [{ role: 'user', content: `Break down the concept "${input}"
         into easy-to-understand sections with sub-headings, include examples if necessary. Provide the output 
         as json objects where each sub-heading is a key and each concept as values, the enitre sub-section is enclosed 
         on a parent called object called CONCEPTS, dont include anything else. ` }],
      model: 'llama-3.3-70b-versatile',
    });
    
    const simplifiedContent = simplifyResponse.choices[0].message.content;

    // Step 2: Generate Mermaid diagrams with Gemma
    const gemmaPrompt = `Using the simplified content ${simplifiedContent}, generate only Mermaid.js diagrams where applicable. 
    Output each diagram as a JSON object, with the diagram heading as the key and its corresponding Mermaid.js code as the value. 
    Enclose all diagrams within a single parent key "CODE". Provide *only* the JSON structure and nothing else — no additional text, explanations, labels, or formatting like backticks or "json".`;
    
    const gemmaResponse = await client.chat.completions.create({
      messages: [{ role: 'user', content: gemmaPrompt }],
      model: 'gemma2-9b-it',
    });

    const mermaidContent = gemmaResponse.choices[0].message.content;

    // Step 3: Write to text file
    writeToFile(simplifiedContent, mermaidContent);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

function writeToFile(content, diagrams) {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const textFilePath = path.join(__dirname, 'test.txt');

  // Sanitize the diagrams content
  const sanitizedDiagrams = diagrams.replace(/```json|```/g, '').trim();

  // Parse the content and diagrams as JSON
  const contentJson = JSON.parse(content);
  const diagramsJson = JSON.parse(sanitizedDiagrams);

  // Combine the content and diagrams into a single JSON object
  const combinedJson = {
    ...contentJson,
    ...diagramsJson
  };

  // Convert the combined JSON object to a string
  const textContent = JSON.stringify(combinedJson, null, 2);

  fs.writeFileSync(textFilePath, textContent, 'utf8');
}

// Example usage
processConcept('Explain the importance of low latency in Large Language Models (LLMs).');