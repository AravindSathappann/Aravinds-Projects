import re
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin


FRAUD_KEYWORDS = [
    "fraud",
    "stolen",
    "unauthorized",
    "did not authorize",
    "do not recognize",
    "suspicious",
    "strange charge",
    "strange activity",
    "dispute",
    "never made this purchase",
    "card was stolen"
]

COMPLIANCE_KEYWORDS = [
    "interest rate",
    "loan terms",
    "apr",
    "fee",
    "disclosed",
    "agreement",
    "documents",
    "repayment",
    "representative explained",
    "promised"
]

ESCALATION_KEYWORDS = [
    "manager",
    "supervisor",
    "called three times",
    "nobody helped",
    "no one has helped",
    "transferred",
    "frustrated",
    "resolved today",
    "keeps happening",
    "waiting for days",
    "escalated"
]

SUPPORT_KEYWORDS = [
    "update",
    "reset",
    "password",
    "account balance",
    "replacement card",
    "phone number",
    "mailing address",
    "help me"
]

NEGATIVE_WORDS = [
    "angry",
    "frustrated",
    "upset",
    "worried",
    "concerned",
    "problem",
    "issue",
    "wrong",
    "stolen",
    "suspicious",
    "unauthorized"
]

URGENCY_WORDS = [
    "today",
    "immediately",
    "right now",
    "as soon as possible",
    "urgent",
    "emergency",
    "quickly"
]

POSITIVE_WORDS = [
    "thank",
    "thanks",
    "helpful",
    "resolved",
    "appreciate",
    "great"
]


FEATURE_NAMES = [
    "word_count",
    "sentence_count",
    "dollar_amount_count",
    "max_dollar_amount",
    "total_dollar_amount",
    "fraud_keyword_count",
    "compliance_keyword_count",
    "escalation_keyword_count",
    "support_keyword_count",
    "negative_word_count",
    "urgency_word_count",
    "positive_word_count",
    "speaker_turn_count",
    "question_count",
    "exclamation_count",
    "risk_keyword_total"
]


def clean_text(text):
    if not isinstance(text, str):
        return ""

    return text.lower()


def count_keyword_hits(text, keywords):
    text_lower = clean_text(text)
    count = 0

    for keyword in keywords:
        count += text_lower.count(keyword)

    return count


def extract_dollar_amounts(text):
    text_lower = clean_text(text)

    dollar_patterns = [
        r"\$\s?(\d+(?:,\d{3})*(?:\.\d{1,2})?)",
        r"\b(\d+(?:,\d{3})*(?:\.\d{1,2})?)\s?(?:dollars|dollar|bucks|usd)\b"
    ]

    amounts = []

    for pattern in dollar_patterns:
        matches = re.findall(pattern, text_lower)

        for match in matches:
            clean_amount = match.replace(",", "")

            try:
                amounts.append(float(clean_amount))
            except ValueError:
                continue

    return amounts


def count_sentences(text):
    sentences = re.split(r"[.!?]+", text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return len(sentences)


def count_words(text):
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def count_speaker_turns(text):
    speaker_patterns = [
        r"\bcustomer:",
        r"\bagent:",
        r"\brepresentative:",
        r"\bcaller:"
    ]

    text_lower = clean_text(text)
    count = 0

    for pattern in speaker_patterns:
        count += len(re.findall(pattern, text_lower))

    return count


def extract_manual_features(text):
    text = "" if not isinstance(text, str) else text

    dollar_amounts = extract_dollar_amounts(text)

    fraud_count = count_keyword_hits(text, FRAUD_KEYWORDS)
    compliance_count = count_keyword_hits(text, COMPLIANCE_KEYWORDS)
    escalation_count = count_keyword_hits(text, ESCALATION_KEYWORDS)
    support_count = count_keyword_hits(text, SUPPORT_KEYWORDS)

    negative_count = count_keyword_hits(text, NEGATIVE_WORDS)
    urgency_count = count_keyword_hits(text, URGENCY_WORDS)
    positive_count = count_keyword_hits(text, POSITIVE_WORDS)

    features = {
        "word_count": count_words(text),
        "sentence_count": count_sentences(text),
        "dollar_amount_count": len(dollar_amounts),
        "max_dollar_amount": max(dollar_amounts) if dollar_amounts else 0,
        "total_dollar_amount": sum(dollar_amounts) if dollar_amounts else 0,
        "fraud_keyword_count": fraud_count,
        "compliance_keyword_count": compliance_count,
        "escalation_keyword_count": escalation_count,
        "support_keyword_count": support_count,
        "negative_word_count": negative_count,
        "urgency_word_count": urgency_count,
        "positive_word_count": positive_count,
        "speaker_turn_count": count_speaker_turns(text),
        "question_count": text.count("?"),
        "exclamation_count": text.count("!"),
        "risk_keyword_total": fraud_count + compliance_count + escalation_count
    }

    return features


class ManualFeatureExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        feature_matrix = []

        for text in X:
            features = extract_manual_features(text)
            row = [features[name] for name in FEATURE_NAMES]
            feature_matrix.append(row)

        return np.array(feature_matrix, dtype=float)
