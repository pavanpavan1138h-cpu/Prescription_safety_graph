from typing import Dict, List, Set, Tuple
from src.prescription.intelligence.intelligence_schema import EvidenceTheme, EvidenceThemeType

THEME_DESCRIPTIONS = {
    EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value: "Arrhythmias, abnormal ECG readings, QT prolongation, or conduction delays.",
    EvidenceThemeType.HEMODYNAMIC_SIGNAL.value: "Blood pressure fluctuations (hypertension, hypotension) or shock states.",
    EvidenceThemeType.NEUROLOGICAL_SIGNAL.value: "Headaches, somnolence, confusion, tremors, convulsions, or other central nervous system effects.",
    EvidenceThemeType.RESPIRATORY_SIGNAL.value: "Dyspnea, coughs, bronchospasms, pneumonia, or respiratory distress markers.",
    EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value: "Nausea, vomiting, diarrhea, dyspepsia, or general abdominal pain symptoms.",
    EvidenceThemeType.RENAL_SIGNAL.value: "Acute kidney injury, serum creatinine elevations, or filtration efficiency drops.",
    EvidenceThemeType.HEPATIC_SIGNAL.value: "Elevated liver enzymes (ALT/AST), jaundice, hepatomegaly, or direct liver tissue stress.",
    EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value: "Leukopenia, thrombocytopenia, anemia, or systemic bleeding events.",
    EvidenceThemeType.METABOLIC_SIGNAL.value: "Electrolyte imbalances (potassium/sodium swings) or glucose metabolism shifts.",
    EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value: "Allergic hyper-reactivity (rash, anaphylaxis), fevers, or systemic infections.",
    EvidenceThemeType.DERMATOLOGICAL_SIGNAL.value: "Direct skin tissue markers, alopecia, dry skin, or non-immunological dermatitis.",
    EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value: "Joint and muscle pain, spasms, or density-related skeletal issues.",
    EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value: "General fatigue, asthenia, edema, chest pains, or unexplained weight shifts.",
    EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME.value: "Grounded side effects not belonging to a primary controlled vocabulary class."
}

THEME_MAP = {
    # CARDIAC_ELECTROPHYSIOLOGY_SIGNAL
    "abnormal ecg": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "electrocardiogram abnormal": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "arrhythmia": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "tachycardia": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "bradycardia": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "palpitations": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "palpitation": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "qt interval prolonged": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "electrocardiogram qt interval prolonged": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "cardiac arrest": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "ventricular fibrillation": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "ventricular tachycardia": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,
    "atrial fibrillation": EvidenceThemeType.CARDIAC_ELECTROPHYSIOLOGY_SIGNAL.value,

    # HEMODYNAMIC_SIGNAL
    "hypotension": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "hypertension": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "orthostatic hypotension": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "blood pressure increased": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "blood pressure decreased": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "shock": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,
    "cardiogenic shock": EvidenceThemeType.HEMODYNAMIC_SIGNAL.value,

    # NEUROLOGICAL_SIGNAL
    "headache": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "dizziness": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "somnolence": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "seizure": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "convulsion": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "tremor": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "paresthesia": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "ataxia": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "insomnia": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "confusion": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,
    "confusional state": EvidenceThemeType.NEUROLOGICAL_SIGNAL.value,

    # RESPIRATORY_SIGNAL
    "dyspnea": EvidenceThemeType.RESPIRATORY_SIGNAL.value,
    "cough": EvidenceThemeType.RESPIRATORY_SIGNAL.value,
    "respiratory failure": EvidenceThemeType.RESPIRATORY_SIGNAL.value,
    "asthma": EvidenceThemeType.RESPIRATORY_SIGNAL.value,
    "pneumonia": EvidenceThemeType.RESPIRATORY_SIGNAL.value,
    "bronchospasm": EvidenceThemeType.RESPIRATORY_SIGNAL.value,

    # GASTROINTESTINAL_SIGNAL
    "nausea": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,
    "vomiting": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,
    "diarrhea": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,
    "constipation": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,
    "abdominal pain": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,
    "dyspepsia": EvidenceThemeType.GASTROINTESTINAL_SIGNAL.value,

    # RENAL_SIGNAL
    "renal failure": EvidenceThemeType.RENAL_SIGNAL.value,
    "renal failure acute": EvidenceThemeType.RENAL_SIGNAL.value,
    "blood urea nitrogen increased": EvidenceThemeType.RENAL_SIGNAL.value,
    "serum creatinine increased": EvidenceThemeType.RENAL_SIGNAL.value,
    "creatinine renal increased": EvidenceThemeType.RENAL_SIGNAL.value,
    "acute kidney injury": EvidenceThemeType.RENAL_SIGNAL.value,
    "dysuria": EvidenceThemeType.RENAL_SIGNAL.value,

    # HEPATIC_SIGNAL
    "aspartate aminotransferase increased": EvidenceThemeType.HEPATIC_SIGNAL.value,
    "alanine aminotransferase increased": EvidenceThemeType.HEPATIC_SIGNAL.value,
    "jaundice": EvidenceThemeType.HEPATIC_SIGNAL.value,
    "hepatic failure": EvidenceThemeType.HEPATIC_SIGNAL.value,
    "hepatomegaly": EvidenceThemeType.HEPATIC_SIGNAL.value,
    "hepatotoxicity": EvidenceThemeType.HEPATIC_SIGNAL.value,

    # HEMATOLOGICAL_SIGNAL
    "anemia": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,
    "thrombocytopenia": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,
    "leukopenia": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,
    "neutropenia": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,
    "hemorrhage": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,
    "epistaxis": EvidenceThemeType.HEMATOLOGICAL_SIGNAL.value,

    # METABOLIC_SIGNAL
    "hyperglycemia": EvidenceThemeType.METABOLIC_SIGNAL.value,
    "hypoglycemia": EvidenceThemeType.METABOLIC_SIGNAL.value,
    "hyperkalemia": EvidenceThemeType.METABOLIC_SIGNAL.value,
    "hypokalemia": EvidenceThemeType.METABOLIC_SIGNAL.value,
    "hyponatremia": EvidenceThemeType.METABOLIC_SIGNAL.value,
    "hyperuricemia": EvidenceThemeType.METABOLIC_SIGNAL.value,

    # IMMUNOLOGICAL_SIGNAL
    "fever": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "pyrexia": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "rash": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "urticaria": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "pruritus": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "anaphylactic shock": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "anaphylaxis": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,
    "infection": EvidenceThemeType.IMMUNOLOGICAL_SIGNAL.value,

    # DERMATOLOGICAL_SIGNAL
    "alopecia": EvidenceThemeType.DERMATOLOGICAL_SIGNAL.value,
    "dry skin": EvidenceThemeType.DERMATOLOGICAL_SIGNAL.value,
    "dermatitis": EvidenceThemeType.DERMATOLOGICAL_SIGNAL.value,
    "skin rash": EvidenceThemeType.DERMATOLOGICAL_SIGNAL.value,

    # MUSCULOSKELETAL_SIGNAL
    "myalgia": EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value,
    "arthralgia": EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value,
    "muscle spasm": EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value,
    "muscle spasms": EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value,
    "osteoporosis": EvidenceThemeType.MUSCULOSKELETAL_SIGNAL.value,

    # GENERAL_SYSTEMIC_SIGNAL
    "fatigue": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "asthenia": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "edema": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "peripheral edema": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "pain": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "chest pain": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "weight increased": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value,
    "weight decreased": EvidenceThemeType.GENERAL_SYSTEMIC_SIGNAL.value
}

class EvidenceThemeMapper:
    @staticmethod
    def normalize_term(term: str) -> str:
        if not term:
            return ""
        return term.strip().lower()

    @classmethod
    def map_event_to_theme(cls, event_name: str) -> EvidenceThemeType:
        norm = cls.normalize_term(event_name)
        theme_str = THEME_MAP.get(norm)
        if theme_str:
            return EvidenceThemeType(theme_str)
        return EvidenceThemeType.UNKNOWN_OR_UNMAPPED_THEME

    @classmethod
    def get_description_for_theme(cls, theme: EvidenceThemeType) -> str:
        return THEME_DESCRIPTIONS.get(theme.value, "No description available.")
