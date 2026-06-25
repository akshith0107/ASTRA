from typing import List
from app.schemas.analysis import Indicator

class IndicatorService:
    def extract_indicators(self, text: str) -> List[Indicator]:
        """
        Runs heuristic checks to detect specific scam indicators.
        """
        text_lower = text.lower()
        indicators = []

        # 1. OTP detection
        if "otp" in text_lower or "pin" in text_lower or "verification code" in text_lower:
            indicators.append(Indicator(
                type="OTP Request",
                description="The caller/message is asking for a sensitive verification code.",
                confidence=0.9
            ))

        # 2. UPI detection
        if "upi" in text_lower or "gpay" in text_lower or "phonepe" in text_lower:
            indicators.append(Indicator(
                type="UPI Platform",
                description="Mentions of digital payment platforms commonly used for immediate transfers.",
                confidence=0.8
            ))

        # 3. Urgency detection
        urgency_keywords = ["immediate", "urgent", "block", "freeze", "suspend", "today"]
        if any(keyword in text_lower for keyword in urgency_keywords):
            indicators.append(Indicator(
                type="Urgency/Threat",
                description="Language designed to panic the victim into acting quickly.",
                confidence=0.85
            ))

        # 4. Impersonation detection
        impersonation_keywords = ["state bank", "sbi", "hdfc", "icici", "rbi", "police", "customs"]
        if any(keyword in text_lower for keyword in impersonation_keywords):
            indicators.append(Indicator(
                type="Authority Impersonation",
                description="Claiming to be from a bank or government authority.",
                confidence=0.95
            ))

        # 5. Payment request detection
        payment_keywords = ["pay", "transfer", "fee", "processing fee", "deposit"]
        if any(keyword in text_lower for keyword in payment_keywords):
            indicators.append(Indicator(
                type="Financial Request",
                description="Explicit request for money transfer.",
                confidence=0.8
            ))

        return indicators

indicator_service = IndicatorService()
