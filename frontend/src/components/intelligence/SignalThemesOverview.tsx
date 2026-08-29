import React from 'react';
import { Card } from '../common/Card';
import { EvidenceTheme } from '../../types/api';
import { formatEvidenceStatus } from '../../utils/formatters';

interface SignalThemesOverviewProps {
  themes: EvidenceTheme[];
}

export const SignalThemesOverview: React.FC<SignalThemesOverviewProps> = ({ themes }) => {
  const activeThemes = themes.filter((t) => t.theme_name !== "UNKNOWN_OR_UNMAPPED_THEME");
  const unmappedTheme = themes.find((t) => t.theme_name === "UNKNOWN_OR_UNMAPPED_THEME");

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <Card title="Clinical Safety Signal Themes" subtitle="Deterministic classification of combination side effects into standardized physiological mapping classes">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {activeThemes.length === 0 ? (
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '1rem 0' }}>
              No primary safety signal themes identified.
            </div>
          ) : (
            activeThemes.map((theme) => (
              <div
                key={theme.theme_id}
                style={{
                  padding: '1.25rem',
                  borderRadius: '6px',
                  backgroundColor: '#0f1222',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.75rem'
                }}
              >
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff' }}>
                    {formatEvidenceStatus(theme.theme_name)}
                  </span>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Grounded occurrences: <b style={{ color: '#fff' }}>{theme.supporting_evidence_count}</b>
                  </div>
                </div>

                {/* Description */}
                <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  {theme.description}
                </p>

                {/* Medications involved */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginRight: '0.25rem' }}>Involved Drugs:</span>
                  {theme.participating_drugs.map((d) => (
                    <span
                      key={d}
                      style={{
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        backgroundColor: '#1e293b',
                        border: '1px solid var(--border-color)',
                        color: '#fff',
                        fontSize: '0.75rem'
                      }}
                    >
                      {d}
                    </span>
                  ))}
                </div>

                {/* Side effect sub-chips */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', borderTop: '1px solid #1e293b', paddingTop: '0.5rem' }}>
                  {theme.mapped_events.slice(0, 8).map((evt, i) => (
                    <span
                      key={i}
                      style={{
                        padding: '0.15rem 0.4rem',
                        borderRadius: '3px',
                        backgroundColor: '#ef44440d',
                        border: '1px solid #ef444422',
                        color: '#fca5a5',
                        fontSize: '0.7rem'
                      }}
                    >
                      {evt}
                    </span>
                  ))}
                  {theme.mapped_events.length > 8 && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', alignSelf: 'center', marginLeft: '0.25rem' }}>
                      + {theme.mapped_events.length - 8} more...
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Unmapped side effects drawer card */}
      {unmappedTheme && unmappedTheme.mapped_events.length > 0 && (
        <Card title="Supplementary Unmapped Side Effects" subtitle="Observed combinations side effects that did not match primary registry vocabulary classes">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
            {unmappedTheme.mapped_events.slice(0, 30).map((evt, i) => (
              <span
                key={i}
                style={{
                  padding: '0.2rem 0.5rem',
                  borderRadius: '4px',
                  backgroundColor: '#1e293b',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-muted)',
                  fontSize: '0.75rem'
                }}
              >
                {evt}
              </span>
            ))}
            {unmappedTheme.mapped_events.length > 30 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center', marginLeft: '0.25rem' }}>
                + {unmappedTheme.mapped_events.length - 30} more unmapped events...
              </span>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};
