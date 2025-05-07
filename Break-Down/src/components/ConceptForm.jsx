
import React, { useState } from 'react';

function ConceptForm({ onSubmit, isLoading }) {
  const [concept, setConcept] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!concept.trim()) return; 
    onSubmit(concept);
    setConcept(''); 
  };

  return (
    <form onSubmit={handleSubmit} className="concept-form">
      <textarea
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="Enter an academic concept..."
        rows="3"
        disabled={isLoading}
      />
      <button type="submit" className="primary" disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Explain'}
      </button>
    </form>
  );
}

export default ConceptForm;