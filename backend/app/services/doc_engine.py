import json
from pathlib import Path
from app.models import Category, DocumentRequirements

RULES_PATH = Path(__file__).parent.parent / "data" / "country_rules.json"


class DocumentEngine:
    def __init__(self, path: Path = RULES_PATH):
        self.rules = json.loads(path.read_text(encoding="utf-8"))

    def requirements_for(self, origin: str, destination: str, category: Category) -> DocumentRequirements:
        corridor = "CN-EU" if origin == "CN" else f"{origin}-{destination}"
        rule = self.rules[corridor]
        docs = list(rule["required_docs"])
        docs.extend(rule.get("conditional", {}).get(category.value, []))
        meta = self.rules["metadata"]
        return DocumentRequirements(corridor=corridor, required_docs=docs, rule_version=meta["rule_version"], effective_date=meta["effective_date"], last_reviewed_at=meta["last_reviewed_at"], source_urls=meta["source_urls"])

    def supported_corridors(self) -> list[str]:
        return sorted(key for key in self.rules if key != "metadata")
