# Phase 7.E — Interactive UI & Dashboard Architecture Specification

## 1. Executive Summary & Core UI Philosophy
Phase 7.E establishes the complete user interface, component hierarchy, user journey, and visual explainability workflow for the **Prescription Safety Application Platform**.

### The Core UI Philosophy:
> **Input $\rightarrow$ Resolve $\rightarrow$ Analyze $\rightarrow$ Understand $\rightarrow$ Investigate $\rightarrow$ Trace Evidence**
> The interface is designed around structured evidence exploration and transparent knowledge graph reasoning. It never presents uncalibrated red warnings or unsubstantiated "unsafe" claims.

```text
┌────────────────────────────────────────────────────────────────────────────────┐
│                         PRESCRIPTION INPUT SCREEN                              │
│                                                                                │
│   - Multi-medication input list (Names, RxCUIs, DB IDs, CIDs, Internal IDs)    │
│   - Dynamic resolution preview (Status: RESOLVED, AMBIGUOUS, UNRESOLVED)       │
│   - Transparent duplicate collapsing representation                            │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                      PIPELINE EXECUTION & LOADING STATE                        │
│                                                                                │
│   - Live progress checklist (Resolution -> Pairs -> Inference -> Report)      │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                      PRESCRIPTION SAFETY REPORT DASHBOARD                      │
│                                                                                │
│   [Summary Metrics]       Unique Drugs, Evaluated Pairs, Overall Status        │
│   [Prioritized Findings]  Ranked Cards (CRITICAL -> HIGH -> MODERATE)          │
│   [Drug Participation]    Bar distribution of evidence involvement             │
│   [All Pairs Explorer]    Filterable/sortable table of all N*(N-1)/2 pairs     │
│   [Ethical Guardrails]    Server-rendered scientific limitation notices        │
└──────────────────────────────────────┬─────────────────────────────────────────┘
                                       │ (Drill-Down on any Pair)
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│                   PAIR DETAIL, EVIDENCE & PROVENANCE INSPECTOR                 │
│                                                                                │
│   [Channel 1: DrugBank]   Directed assertion text & Edge IDs                   │
│   [Channel 2: TWOSIDES]   Searchable adverse event list (e.g. 202 events)      │
│   [Channel 3: RxNorm]     Clinical concepts and match method                   │
│   [Multi-Hop Provenance]  Finding -> Rule -> Graph Edges -> Source Records     │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Screen & Component Hierarchy

### Screen 1: Landing & Prescription Input
- **Header**: System identity & one-sentence mission (*"Analyze prescription combinations through structured interaction and adverse-event evidence"*).
- **Medication Input List**: Dynamic multi-row input with add/remove actions.
- **Resolution Preview Panel**: Real-time feedback displaying what the system understood before analysis:
  - `✓ fluconazole` $\rightarrow$ `Fluconazole (DRUG_000048)`
  - `✓ CID000003365` $\rightarrow$ `Fluconazole (DRUG_000048) [DUPLICATE COLLAPSED]`
  - `⚠ UnknownNovelDrugXYZ` $\rightarrow$ `Unresolved (Excluded from graph analysis)`

### Screen 2: Analysis Loading State
- Real-time step tracker making backend operations explicit:
  1. *Resolving medication identities...*
  2. *Collapsing duplicate entities...*
  3. *Generating unique $N(N-1)/2$ combinations...*
  4. *Retrieving direct interaction and combination adverse events...*
  5. *Synthesizing clinical safety report...*

### Screen 3: Main Safety Report Dashboard
- **Top Summary Cards**:
  - `Unique Canonical Drugs` (e.g. 3)
  - `Total Pairs Evaluated` (e.g. 3)
  - `Pairs with Graph Evidence` (e.g. 2)
  - `Overall Prescription Status` (`MULTI_SIGNAL_EVIDENCE`)
  - `Highest Evidence Priority` (`CRITICAL_EVIDENCE_PRIORITY`)
- **Prioritized Findings Cards**:
  - Highlights top evidence-supported pairs (e.g. `Cyclosporine + Fluconazole` $\rightarrow$ `CRITICAL_EVIDENCE_PRIORITY`).
  - Lists evidence channels present (DrugBank DDI assertions, TWOSIDES combination events).
  - Includes a direct *[Inspect Evidence]* button.
- **Drug Participation Analysis**:
  - Visual breakdown indicating which medications participate in multiple findings across the prescription.
- **All Pairs Explorer Table**:
  - Comprehensive table of all evaluated pairs with sorting by Priority, Confidence, and Drug Name, and filtering by Evidence Type (`All`, `Convergent`, `DDI Only`, `Combination Events Only`, `No Direct Evidence`).
- **Standardized Guardrail Banner**:
  - Prominently displays server-side scientific disclaimers.

### Screen 4: Granular Pair Detail & Provenance Inspector (Modal / Dedicated Route)
- **Channel 1 (DrugBank DDI Evidence)**: Directed path, assertion text, and source IDs.
- **Channel 2 (TWOSIDES Combination Evidence)**: Total observed event count with interactive search/filtering over adverse event names.
- **Channel 3 (Clinical Concept Context)**: Standardized RxNorm identifiers (`RXCUI_xxxx`).
- **Reasoning Trace & Multi-Hop Provenance**: Complete path traversal from Finding $\rightarrow$ Fired Rule $\rightarrow$ Graph Edge IDs $\rightarrow$ Source Records $\rightarrow$ Dataset Provenance.

---

## 3. UI Technology & Component Structure (`frontend/`)

```text
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
│
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   │
│   ├── api/
│   │   ├── client.ts
│   │   └── prescriptionApi.ts
│   │
│   ├── types/
│   │   └── api.ts
│   │
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── MedicationInput.tsx
│   │   ├── ResolutionPreview.tsx
│   │   ├── LoadingTracker.tsx
│   │   ├── SummaryCards.tsx
│   │   ├── FindingCard.tsx
│   │   ├── DrugParticipationChart.tsx
│   │   ├── PairExplorerTable.tsx
│   │   ├── PairDetailModal.tsx
│   │   ├── ProvenanceTracePanel.tsx
│   │   └── GuardrailBanner.tsx
│   │
│   └── views/
│       ├── HomeView.tsx
│       └── ReportView.tsx
```

---

## 4. UI Safety States & Edge Cases

| Scenario | UI Presentation Rule |
| :--- | :--- |
| **Empty Input** | Prompts user to enter at least one medication before submitting. |
| **Single Drug Input** | Displays single drug identity card; gracefully informs that pairwise combination analysis requires $\ge 2$ unique drugs. |
| **Duplicate Identifiers** | Displays all entered strings while visually grouping them under their single canonical drug card. |
| **Unresolved Medications** | Displays an alert listing unmapped inputs and informs that analysis proceeded on the remaining valid drugs. |
| **No Direct Graph Evidence** | Displays clear notice: *"No direct interaction or combination evidence found in the current graph. This does NOT establish clinical safety."* |
| **Server Error** | Displays user-friendly error envelope with traceable `request_id`. |
