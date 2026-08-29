import React, { useState } from 'react';
import { Plus, Play, RefreshCw, X } from 'lucide-react';

interface MedicationInputProps {
  medications: string[];
  onAddMedication: (med: string) => void;
  onRemoveMedication: (index: number) => void;
  onAnalyze: () => void;
  onReset: () => void;
  loading: boolean;
}

export const MedicationInput: React.FC<MedicationInputProps> = ({
  medications,
  onAddMedication,
  onRemoveMedication,
  onAnalyze,
  onReset,
  loading
}) => {
  const [inputVal, setInputVal] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim()) {
      onAddMedication(inputVal.trim());
      setInputVal('');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>
          Medication Intake List
        </h2>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
          Input brand names, generics, RXCUIs, or DrugBank IDs to build the prescription.
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="e.g. fluconazole, cyclosporine..."
          disabled={loading}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            color: '#fff',
            fontSize: '0.9rem',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '0.75rem 1.25rem',
            borderRadius: '6px',
            backgroundColor: '#1e293b',
            border: '1px solid var(--border-color)',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          <Plus size={16} />
          <span>Add</span>
        </button>
      </form>

      {/* Medication Chips */}
      <div style={{ minHeight: '80px', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignContent: 'flex-start' }}>
        {medications.length === 0 ? (
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '0.5rem 0' }}>
            No medications added yet.
          </div>
        ) : (
          medications.map((med, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.4rem 0.8rem',
                borderRadius: '9999px',
                backgroundColor: '#1e293b',
                border: '1px solid var(--border-color)',
                fontSize: '0.85rem',
                color: '#fff'
              }}
            >
              <span>{med}</span>
              <button
                type="button"
                onClick={() => onRemoveMedication(index)}
                disabled={loading}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <X size={14} className="hover:text-red-400" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={loading || medications.length === 0}
          style={{
            flex: 1,
            padding: '0.75rem 1.5rem',
            borderRadius: '6px',
            backgroundColor: '#8b5cf6',
            color: '#fff',
            fontWeight: 600,
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            cursor: medications.length === 0 ? 'not-allowed' : 'pointer',
            opacity: medications.length === 0 ? 0.6 : 1
          }}
        >
          {loading ? (
            <>
              <RefreshCw size={16} className="animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Play size={16} />
              <span>Analyze Prescription</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onReset}
          disabled={loading || medications.length === 0}
          style={{
            padding: '0.75rem 1.25rem',
            borderRadius: '6px',
            backgroundColor: '#0f1222',
            border: '1px solid var(--border-color)',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          Reset
        </button>
      </div>
    </div>
  );
};
