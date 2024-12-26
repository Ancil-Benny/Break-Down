import Groq from 'groq-sdk';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pkg from 'outlines';
const { TextGenerator } = pkg;

dotenv.config();

const client = new Groq({
  apiKey: process.env['GROQ_API_KEY'],
});


async function processConcept(input) {
  try {
    // 1.Simplify concept with LLaMA
    const simplifyResponse = await client.chat.completions.create({
      messages: [{
        role: 'user',
        content: `Break down the concept "${input}" into simple and easy-to-understand sections. 
        Include examples where necessary.`
      }],
      model: 'llama-3.3-70b-versatile',
    });

    const simplifiedContent = simplifyResponse.choices[0].message.content;

  
    const contentJson = constructConceptJson(simplifiedContent);

    // 2. Generate Mermaid diagrams
    const gemmaPrompt = `Using the simplified content ${simplifiedContent}, generate valid Mermaid.js diagrams where applicable`;

    const gemmaResponse = await client.chat.completions.create({
      messages: [{ role: 'user', content: gemmaPrompt }],
      model: 'gemma2-9b-it',
    });

    const mermaidContent = gemmaResponse.choices[0].message.content;

  
    const diagramsJson = constructDiagramJson(mermaidContent);

    //3: Write to files
    writeToFile('simplified_concepts.json', contentJson);
    writeToFile('mermaid_diagrams.json', diagramsJson);

    // 4. create the third JSON structure
    const mergedContent = await mergeJsonFiles(contentJson, diagramsJson);

    // output.json
    writeToFile('output.json', mergedContent);

    //  HTML from output.json
    generateHtmlFromJson('output.json', 'output.html');

  } catch (error) {
    console.error('Error:', error.message);
  }
}

function constructConceptJson(content) {
  const lines = content.split('\n');
  const jsonObject = { "CONCEPTS": {} };
  let currentSubheading = '';

  lines.forEach(line => {
    if (line.startsWith('## ')) {
      currentSubheading = line.substring(3);
      jsonObject.CONCEPTS[currentSubheading] = '';
    } else if (currentSubheading) {
      jsonObject.CONCEPTS[currentSubheading] += line + '\n';
    }
  });

  return jsonObject;
}

function constructDiagramJson(content) {
  const lines = content.split('\n');
  const jsonObject = { "CODE": {} };
  let currentDiagramTitle = '';

  lines.forEach(line => {
    if (line.startsWith('```mermaid')) {
      currentDiagramTitle = 'Diagram' + (Object.keys(jsonObject.CODE).length + 1);
      jsonObject.CODE[currentDiagramTitle] = '';
    } else if (line.startsWith('```')) {
      currentDiagramTitle = '';
    } else if (currentDiagramTitle) {
      jsonObject.CODE[currentDiagramTitle] += line + '\n';
    }
  });

  return jsonObject;
}

function writeToFile(fileName, jsonObject) {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const filePath = path.join(__dirname, fileName);

  const fileContent = JSON.stringify(jsonObject, null, 2);

  fs.writeFileSync(filePath, fileContent, 'utf8');
  console.log(`File written: ${filePath}`);
}

async function mergeJsonFiles(conceptsJson, diagramsJson) {
  const mergedContent = {
    "CONTENT": []
  };

  Object.keys(conceptsJson.CONCEPTS).forEach((subheading, index) => {
    mergedContent.CONTENT.push({
      "heading": subheading,
      "concept": conceptsJson.CONCEPTS[subheading],
      "diagram": diagramsJson.CODE['Diagram' + (index + 1)] || ''
    });
  });

  return mergedContent;
}

function generateHtmlFromJson(inputFile, outputFile) {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const inputFilePath = path.join(__dirname, inputFile);
  const outputFilePath = path.join(__dirname, outputFile);

  const jsonData = JSON.parse(fs.readFileSync(inputFilePath, 'utf8'));


  let htmlContent = '<html><body>';
  jsonData.CONTENT.forEach(item => {
    htmlContent += `<h1>${item.heading}</h1>`;
    htmlContent += `<p>${item.concept}</p>`;
    if (item.diagram) {
      htmlContent += `<div class="mermaid">${item.diagram}</div>`;
    }
  });
  htmlContent += `
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@9/dist/mermaid.esm.min.mjs';
      mermaid.initialize({ startOnLoad: true });
    </script>
  </body></html>`;

  fs.writeFileSync(outputFilePath, htmlContent, 'utf8');
  console.log(`HTML file written: ${outputFilePath}`);
}

//usage
processConcept('Explain the importance of low latency in Large Language Models (LLMs).');
