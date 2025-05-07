import React, { useState } from 'react';
import ConceptForm from './components/ConceptForm';
import ConceptDisplay from './components/ConceptDisplay';
import './App.css';

function App() {
  const [conceptData, setConceptData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]); 

  const fetchConceptBreakdown = async (concept) => {
    setIsLoading(true);
    setError(null);
    setConceptData(null); 

    try {
      const response = await fetch('http://localhost:3001/api/breakdown', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ concept }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data.error) {
        setError(data.error || data.errorMessage || 'An error occurred while fetching data.');
        setConceptData(null);
      } else {
        setConceptData(data);
        setHistory((prev) => [...prev, { concept, data }]); 
      }
    } catch (e) {
      console.error("Fetch error:", e);
      setError(e.message || 'Failed to fetch concept breakdown.');
      setConceptData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Concept Explainer</h1>
      <ConceptForm onSubmit={fetchConceptBreakdown} isLoading={isLoading} />
      {isLoading && <p className="loading-message">Loading...</p>}
      {error && <p className="error-message">{error}</p>}
      {conceptData && !error && <ConceptDisplay data={conceptData} />}
      {history.length > 0 && (
        <div className="section">
          <h3>Query History</h3>
          <div className="history-buttons">
            {history.map((item, index) => (
              <button
                key={index}
                onClick={() => setConceptData(item.data)}
              >
                {item.concept}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;