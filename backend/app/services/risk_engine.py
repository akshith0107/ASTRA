class RiskEngine:
    @staticmethod
    def calculate_risk(base_confidence: float, indicators: list, similar_scam_score: float = 0.0) -> tuple[float, str]:
        """
        Calculates the final risk score (0-1.0) and risk level.
        Combines BERT base confidence, indicator heuristics, and RAG similarity.
        """
        # Base weight from ML model
        score = base_confidence * 0.4
        
        # Indicator weights
        indicator_weight = 0.0
        for ind in indicators:
            if ind.type == "Urgency/Threat":
                indicator_weight += 0.2
            elif ind.type == "Financial Request":
                indicator_weight += 0.25
            elif ind.type == "Authority Impersonation":
                indicator_weight += 0.3
            elif ind.type == "Suspicious URL":
                indicator_weight += 0.2
            else:
                indicator_weight += 0.1
                
        # Cap indicator influence
        indicator_weight = min(indicator_weight, 0.4)
        score += indicator_weight
        
        # RAG Historical match weight
        if similar_scam_score > 0.0:
            rag_weight = min(similar_scam_score * 0.2, 0.2)
            score += rag_weight
            
        # Normalize score
        score = min(max(score, 0.0), 1.0)
        
        # Determine Level
        if score < 0.3:
            level = "SAFE"
        elif score < 0.6:
            level = "SUSPICIOUS"
        elif score < 0.85:
            level = "HIGH_RISK"
        else:
            level = "CRITICAL"
            
        return score, level

risk_engine = RiskEngine()
