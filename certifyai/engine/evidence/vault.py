"""Evidence vault — stores and verifies attack evidence with integrity checks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from certifyai.engine.evidence.hasher import hash_chain_link, hash_evidence, verify_chain
from certifyai.engine.models import AttackResult, EvidenceBlob

logger = logging.getLogger(__name__)


class EvidenceVault:
    """Append-only evidence store with SHA-256 hash chain integrity.

    Evidence is stored as JSON files in a directory tree, with an
    append-only hash chain linking all records for tamper detection.
    """

    def __init__(self, vault_path: Path) -> None:
        self.vault_path = vault_path.resolve()
        self.vault_path.mkdir(parents=True, exist_ok=True)

    def store(self, result: AttackResult) -> Path:
        """Store a single attack result as evidence in the vault.

        Args:
            result: The attack result to store.

        Returns:
            Path to the stored evidence file.
        """
        run_dir = self.vault_path / f"run_{result.run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        evidence = EvidenceBlob(
            run_id=result.run_id,
            result_id=result.id,
            prompt=result.prompt,
            response=result.response,
            evaluation=result.evaluation,
        )

        evidence_dict = evidence.model_dump(mode="json")
        evidence_hash = hash_evidence(evidence_dict)

        # Store evidence file
        evidence_path = run_dir / f"{result.scenario_id}_{result.id[:8]}.json"
        evidence_path.write_text(json.dumps(evidence_dict, indent=2, default=str), encoding="utf-8")

        # Store hash file
        hash_path = run_dir / f"{result.scenario_id}_{result.id[:8]}.hash"
        hash_path.write_text(evidence_hash, encoding="utf-8")

        # Update chain
        self._append_to_chain(result.run_id, evidence_hash)

        return evidence_path

    def store_batch(self, results: list[AttackResult]) -> list[Path]:
        """Store multiple attack results.

        Args:
            results: List of attack results.

        Returns:
            List of paths to stored evidence files.
        """
        return [self.store(r) for r in results]

    def verify_run(self, run_id: str) -> dict[str, Any]:
        """Verify the integrity of all evidence for a given run.

        Recomputes hashes and checks the chain integrity.

        Args:
            run_id: The run ID to verify.

        Returns:
            Dict with verification status, total files, and any issues found.
        """
        run_dir = self.vault_path / f"run_{run_id}"
        if not run_dir.exists():
            return {"verified": False, "error": f"Run {run_id} not found in vault"}

        result: dict[str, Any] = {
            "verified": True,
            "total_files": 0,
            "mismatches": [],
            "chain_valid": False,
        }

        hashes: list[str] = []
        for f in sorted(run_dir.glob("*.json")):
            result["total_files"] += 1
            data = json.loads(f.read_text(encoding="utf-8"))
            computed = hash_evidence(data)

            hash_file = f.with_suffix(".hash")
            if hash_file.exists():
                stored = hash_file.read_text(encoding="utf-8").strip()
                if computed != stored:
                    result["verified"] = False
                    result["mismatches"].append(
                        f"{f.name}: hash mismatch (computed={computed[:16]}..., stored={stored[:16]}...)"
                    )
                hashes.append(stored)

        result["chain_valid"] = verify_chain(hashes)
        if not result["chain_valid"]:
            result["verified"] = False

        return result

    def verify_all(self) -> dict[str, Any]:
        """Verify integrity of the entire vault.

        Returns:
            Dict with overall verification status and per-run results.
        """
        runs = sorted(set(d.name for d in self.vault_path.iterdir() if d.is_dir()))
        results: dict[str, Any] = {"verified": True, "runs": {}}

        for run_name in runs:
            run_id = run_name.replace("run_", "", 1)
            run_result = self.verify_run(run_id)
            results["runs"][run_id] = run_result
            if not run_result.get("verified", False):
                results["verified"] = False

        return results

    def _append_to_chain(self, run_id: str, evidence_hash: str) -> None:
        """Append a hash entry to the chain file for a run.

        The chain is an append-only file where each entry links to
        the previous entry via a chain hash.
        """
        chain_path = self.vault_path / f"run_{run_id}" / "chain.log"
        prev_hash = "0" * 64

        if chain_path.exists():
            lines = chain_path.read_text(encoding="utf-8").strip().split("\n")
            if lines and lines[-1].strip():
                parts = lines[-1].strip().split(" ")
                if len(parts) >= 2:
                    prev_hash = parts[-1]

        chain_link = hash_chain_link(prev_hash, evidence_hash)

        with chain_path.open("a", encoding="utf-8") as f:
            f.write(f"{evidence_hash} {chain_link}\n")
