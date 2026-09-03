RISK_LOW_MAX = 26      # score < 26        -> low
RISK_MEDIUM_MAX = 39   # 26 <= score < 39  -> medium
                        # score >= 39       -> high

RISK_LOW, RISK_MEDIUM, RISK_HIGH = "low", "medium", "high"


def score_to_risk_level(score: float) -> str:
    if score < RISK_LOW_MAX:
        return RISK_LOW
    if score < RISK_MEDIUM_MAX:
        return RISK_MEDIUM
    return RISK_HIGH