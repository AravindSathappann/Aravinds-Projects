import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.risk_model import train_risk_classifier


if __name__ == "__main__":
    train_risk_classifier()
