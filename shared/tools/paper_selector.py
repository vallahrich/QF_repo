"""Select papers by tier, group, or topic from classification outputs.

Reads tier_classification.csv and paper_id_bridge.csv to produce
filtered paper lists for use in Steps 2 and 3.

Usage:
    from shared.tools.paper_selector import PaperSelector
    selector = PaperSelector()
    papers = selector.by_tier2_group("portfolio-optimization")
"""

import csv
import os
from pathlib import Path

from .logger import get_logger
from ._paths import find_project_root as _find_project_root

logger = get_logger("paper_selector")


class PaperSelector:
    """Query the classification outputs to select paper subsets."""

    def __init__(
        self,
        tier_csv: str | None = None,
        topic_csv: str | None = None,
        bridge_csv: str | None = None,
    ) -> None:
        root = _find_project_root()

        self._tier_csv = tier_csv or str(
            root / "p2_systematic_review" / "s1_slr" / "06_extraction" / "tier_classification.csv"
        )
        self._topic_csv = topic_csv or str(
            root / "p2_systematic_review" / "s1_slr" / "06_extraction" / "topic_coding.csv"
        )
        self._bridge_csv = bridge_csv or str(
            root / "shared" / "bridge" / "paper_id_bridge.csv"
        )

        self._tier_data: list[dict] | None = None
        self._topic_data: list[dict] | None = None
        self._bridge_data: list[dict] | None = None

    def _load_csv(self, path: str) -> list[dict]:
        """Load a CSV file into a list of dicts."""
        if not os.path.isfile(path):
            logger.warning("CSV file not found: %s", path)
            return []
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    @property
    def tier_data(self) -> list[dict]:
        if self._tier_data is None:
            self._tier_data = self._load_csv(self._tier_csv)
        return self._tier_data

    @property
    def topic_data(self) -> list[dict]:
        if self._topic_data is None:
            self._topic_data = self._load_csv(self._topic_csv)
        return self._topic_data

    @property
    def bridge_data(self) -> list[dict]:
        if self._bridge_data is None:
            self._bridge_data = self._load_csv(self._bridge_csv)
        return self._bridge_data

    def by_tier(self, tier: int) -> list[str]:
        """Return paper_ids classified at the given tier level (1, 2, or 3)."""
        col = f"tier{tier}"
        return [
            row["paper_id"]
            for row in self.tier_data
            if row.get(col, "").strip().lower() not in ("", "no", "false", "0")
        ]

    def by_tier2_group(self, group: str) -> list[str]:
        """Return paper_ids in a specific Tier 2 group."""
        return [
            row["paper_id"]
            for row in self.tier_data
            if row.get("tier2_group", "").strip().lower() == group.lower()
        ]

    def by_topic(self, topic: str) -> list[str]:
        """Return paper_ids tagged with a specific topic."""
        return [
            row["paper_id"]
            for row in self.topic_data
            if topic.lower()
            in [t.strip().lower() for t in row.get("topics", "").split(",")]
        ]

    def by_method(self, method: str) -> list[str]:
        """Return paper_ids tagged with a specific methodology."""
        return [
            row["paper_id"]
            for row in self.topic_data
            if method.lower()
            in [
                m.strip().lower() for m in row.get("methodologies", "").split(",")
            ]
        ]

    def get_doi(self, paper_id: str) -> str | None:
        """Look up DOI for a paper_id via the bridge CSV."""
        for row in self.bridge_data:
            if row.get("paper_id", "").strip() == paper_id.strip():
                doi = row.get("doi", "").strip()
                return doi if doi else None
        return None

    def get_paper_ids_with_dois(self, paper_ids: list[str]) -> dict[str, str]:
        """Return {paper_id: doi} for papers that have DOIs in the bridge."""
        result = {}
        for pid in paper_ids:
            doi = self.get_doi(pid)
            if doi:
                result[pid] = doi
        return result
