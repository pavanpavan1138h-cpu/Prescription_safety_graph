import React from 'react';
import { Card } from '../common/Card';
import { PrescriptionSnapshotReference } from '../../types/api';
import { Calendar, ArrowDown, Info } from 'lucide-react';

interface SnapshotTimelineProps {
  timeline: PrescriptionSnapshotReference[];
}

export const SnapshotTimeline: React.FC<SnapshotTimelineProps> = ({ timeline }) => {
  return (
    <Card title="Analysis Snapshot Sequence" subtitle="Chronological trace of evaluated prescription states">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'center' }}>
        
        {timeline.map((ref, idx) => (
          <React.Fragment key={ref.analysis_id}>
            {/* Timeline node */}
            <div style={{
              width: '100%',
              padding: '1rem 1.25rem',
              borderRadius: '6px',
              backgroundColor: '#0c1020',
              border: '1px solid #1e293b',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Calendar size={18} style={{ color: '#3b82f6' }} />
                <div>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>
                    Snapshot #{ref.sequence_index + 1}: {ref.analysis_id}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.15rem' }}>
                    Meds resolved: {ref.medications.join(', ')}
                  </span>
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  padding: '0.15rem 0.4rem',
                  borderRadius: '3px',
                  backgroundColor: '#1e293b',
                  color: '#94a3b8'
                }}>
                  {ref.position_type}
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: 'block', marginTop: '0.25rem' }}>
                  {ref.snapshot_timestamp ? new Date(ref.snapshot_timestamp).toLocaleString() : 'No timestamp'}
                </span>
              </div>

            </div>

            {/* Down arrow link if not last */}
            {idx < timeline.length - 1 && (
              <ArrowDown size={18} style={{ color: '#1e293b', margin: '0.2rem 0' }} />
            )}
          </React.Fragment>
        ))}

      </div>
    </Card>
  );
};
