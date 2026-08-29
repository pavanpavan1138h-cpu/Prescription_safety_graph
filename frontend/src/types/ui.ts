export type ActiveTab =
  | 'intelligence'
  | 'findings'
  | 'graph'
  | 'explorer'
  | 'participation'
  | 'convergence'
  | 'narrative'
  | 'structure'
  | 'synthesis'
  | 'contextual'
  | 'comparison'
  | 'explainability'
  | 'trustworthiness'
  | 'longitudinal';

export interface UIState {
  activeTab: ActiveTab;
  loading: boolean;
  errorMsg: string | null;
  sideEffectLimit: number;
}
