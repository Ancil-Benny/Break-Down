
import React, { useEffect, useRef, useState } from 'react';


const MermaidDiagram = ({ chart, chartId }) => {
    const containerRef = useRef(null);
    const [errorMessage, setErrorMessage] = useState('');
    const renderCycleRef = useRef(0); 

    useEffect(() => {
        setErrorMessage(''); 
        const currentContainer = containerRef.current;
        const currentRenderCycle = renderCycleRef.current + 1;
        renderCycleRef.current = currentRenderCycle;

        if (!chart || !chart.trim() || !currentContainer) {
            if (currentContainer) currentContainer.innerHTML = ''; 
            return;
        }

        // Function to attempt rendering
        const attemptRender = (isRetry = false) => {
            if (window.mermaid && window.mermaid.initialized) {
                console.log(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Mermaid is ready. Preparing to render. Chart: ${chart.substring(0,70)}...`);
                
         
                currentContainer.innerHTML = ''; 
         

      
                currentContainer.textContent = chart; 
                currentContainer.classList.add('mermaid');

                try {
                   
                    const timeoutId = setTimeout(() => {
                   
                        if (containerRef.current && renderCycleRef.current === currentRenderCycle) { 
                           window.mermaid.run({
                                nodes: [currentContainer] 
                            });
                            console.log(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Called window.mermaid.run()`);
                     
                            if (errorMessage.startsWith("Mermaid library loading")) {
                                setErrorMessage('');
                            }
                        } else {
                            console.log(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Stale render attempt, component unmounted or new chart data arrived. Aborting mermaid.run.`);
                        }
                    }, 0);

                 
                    return () => clearTimeout(timeoutId);

                } catch (e) {
                    console.error(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Error calling window.mermaid.run():`, e);
                    setErrorMessage(`Mermaid run error: ${e.message}`);
                    currentContainer.innerHTML = `<p style="color:red;">Error: ${e.message}</p>`;
                }
            } else {
                if (!isRetry) { 
                    console.warn(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Mermaid not ready or not initialized. Will retry.`);
                    setErrorMessage('Mermaid library loading or not initialized. Waiting...');
                }
                return false; 
            }
            return true; 
        };

        let pollerCleanup = () => {};

        if (!attemptRender()) {
            let attempts = 0;
            const intervalId = setInterval(() => {
                attempts++;
        
                if (!containerRef.current || renderCycleRef.current !== currentRenderCycle) {
                    clearInterval(intervalId);
                    return;
                }
                console.log(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Retry attempt ${attempts} for mermaid readiness.`);
                if (attemptRender(true)) { 
                    clearInterval(intervalId);
                } else if (attempts >= 15) {
                    clearInterval(intervalId);
                    if (!(window.mermaid && window.mermaid.initialized)) {
                        console.error(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): Mermaid library failed to load after multiple retries.`);
                        setErrorMessage('Mermaid library failed to load. Please check the CDN script and network.');
                         if (currentContainer) currentContainer.innerHTML = `<p style="color:red;">Mermaid library failed to load.</p>`;
                    }
                }
            }, 200);
            pollerCleanup = () => clearInterval(intervalId);
        }
        
    
        return () => {
            pollerCleanup(); 
            console.log(`MermaidDiagram [${chartId}] (Cycle ${currentRenderCycle}): useEffect cleanup.`);
        };

    }, [chart, chartId]); 

    if (!chart || !chart.trim()) return null;

    return (
        <div className="mermaid-diagram-container">
            {}
            {errorMessage && !errorMessage.startsWith("Mermaid library loading") && 
                <p style={{ color: 'red', border: '1px dashed red', padding: '10px' }}>{errorMessage}</p>
            }
            <div ref={containerRef} id={`mermaid-actor-${chartId}`}>
                {}
                {(errorMessage || !(window.mermaid && window.mermaid.initialized)) && (
                    <pre>{chart}</pre>
                )}
            </div>
        </div>
    );
};

function ConceptDisplay({ data }) {
  if (!data) return null;

  const {
    concept = "N/A",
    definition = "No definition provided.",
    explanation = "No explanation provided.",
    examples = [],
    mermaid: mermaidCodes = [],
    summary = "No summary provided."
  } = data;

  return (
    <div className="concept-display">
      <div className="section">
        <h2>Concept: {concept}</h2>
      </div>

      <div className="section">
        <h3>Definition</h3>
        <p>{definition}</p>
      </div>

      <div className="section">
        <h3>Detailed Explanation</h3>
        <p>{explanation}</p>
      </div>

      {examples && examples.length > 0 && (
        <div className="section">
          <h3>Illustrative Examples</h3>
          <ul>
            {examples.map((example, index) => (
              <li key={index}>{example}</li>
            ))}
          </ul>
        </div>
      )}

      {mermaidCodes && mermaidCodes.length > 0 && (
        <div className="section">
          <h3>Visual Representation(s)</h3>
          {mermaidCodes.map((code, index) => {
            if (code && code.trim()) {
              const diagramId = `mermaid-cdn-final-${data.concept ? data.concept.replace(/\s+/g, '-').toLowerCase() : 'item'}-${index}`;
              return <MermaidDiagram key={diagramId} chart={code} chartId={diagramId} />;
            }
            return null;
          })}
        </div>
      )}

      <div className="section">
        <h3>Concise Summary</h3>
        <p>{summary}</p>
      </div>
    </div>
  );
}

export default ConceptDisplay;