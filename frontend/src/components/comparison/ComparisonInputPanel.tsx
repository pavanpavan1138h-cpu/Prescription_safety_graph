import React, { useState } from 'react';
import { Card } from '../common/Card';
import { ArrowRightLeft } from 'lucide-react';

interface ComparisonInputPanelProps {
  availableAnalyses: Array<{ id: string; medications: string[] }>;
  onCompare: (idA: string, idB: string) => void;
  loading: boolean;
}

export const ComparisonInputPanel: React.FC<ComparisonInputPanelProps> = ({
  availableAnalyses,
  onCompare,
  loading
}) => {
  const [selectedA, setSelectedA] = useState('');
  const [selectedB, setSelectedB] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedA && selectedB) {
      onCompare(selectedA, selectedB);
    }
  };

  return (
    <Card title="Prescription State Selection" subtitle="Choose two completed analyses to compare their evidence networks and structural parameters">
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          alignItems: 'center',
          gap: '1rem',
          flexWrap: 'wrap'
        }}>
          {/* Analysis A Dropdown */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>Analysis Snapshot A</label>
            <select
              value={selectedA}
              onChange={(e) => setSelectedA(e.target.value)}
              required
              style={{
                padding: '0.6rem',
                borderRadius: '6px',
                backgroundColor: '#0c1020',
                border: '1px solid var(--border-color)',
                color: '#fff',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              <option value="" disabled>-- Select Snapshot A --</option>
              {availableAnalyses.map((item) => (
                <option key={`a-${item.id}`} value={item.id}>
                  {item.id} ({item.medications.join(', ')})
                </option>
              ))}
            </select>
          </div>

          {/* Versus Icon */}
          <ArrowRightLeft size={18} style={{ color: 'var(--text-muted)', marginTop: '1.2rem' }} />

          {/* Analysis B Dropdown */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>Analysis Snapshot B</label>
            <select
              value={selectedB}
              onChange={(e) => setSelectedB(e.target.value)}
              required
              style={{
                padding: '0.6rem',
                borderRadius: '6px',
                backgroundColor: '#0c1020',
                border: '1px solid var(--border-color)',
                color: '#fff',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              <option value="" disabled>-- Select Snapshot B --</option>
              {availableAnalyses.map((item) => (
                <option key={`b-${item.id}`} value={item.id}>
                  {item.id} ({item.medications.join(', ')})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !selectedA || !selectedB || selectedA === selectedB}
          style={{
            alignSelf: 'flex-start',
            padding: '0.6rem 1.5rem',
            borderRadius: '6px',
            backgroundColor: (loading || !selectedA || !selectedB || selectedA === selectedB) ? '#1e293b' : '#3b82f6',
            color: '#fff',
            fontSize: '0.85rem',
            fontWeight: 600,
            border: 'none',
            cursor: (loading || !selectedA || !selectedB || selectedA === selectedB) ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s'
          }}
        >
          {loading ? 'Executing Delta Analytics...' : 'Compare Snapshot States'}
        </button>
      </form>
    </Card>
  );
};
