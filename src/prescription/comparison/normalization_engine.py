class NormalizationEngine:
    @staticmethod
    def safe_divide(numerator: float, denominator: float) -> float:
        if abs(denominator) < 1e-9:
            return 0.0
        return numerator / denominator

    @classmethod
    def get_possible_pairs(cls, total_drugs: int) -> int:
        if total_drugs < 2:
            return 0
        return (total_drugs * (total_drugs - 1)) // 2

    @classmethod
    def evidence_coverage(cls, edges: int, total_drugs: int) -> float:
        possible = cls.get_possible_pairs(total_drugs)
        if possible == 0:
            return 0.0
        return cls.safe_divide(float(edges), float(possible))

    @classmethod
    def convergent_coverage(cls, conv_edges: int, total_drugs: int) -> float:
        possible = cls.get_possible_pairs(total_drugs)
        if possible == 0:
            return 0.0
        return cls.safe_divide(float(conv_edges), float(possible))

    @classmethod
    def theme_coverage(cls, themes_count: int, max_themes: int = 7) -> float:
        return cls.safe_divide(float(themes_count), float(max_themes))

    @classmethod
    def normalized_rank_position(cls, rank: int, total_drugs: int) -> float:
        if total_drugs <= 1:
            return 0.0
        # Position scaled from 0.0 (rank 1, highest centrality) to 1.0 (lowest centrality)
        return cls.safe_divide(float(rank - 1), float(total_drugs - 1))
