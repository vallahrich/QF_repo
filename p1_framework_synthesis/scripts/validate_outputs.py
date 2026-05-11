"""Quick validation of review_data_done.json"""
import json

with open("p1_framework_synthesis/s2_coding/review_data_done.json", "r", encoding="utf-8") as f:
    data = json.load(f)

papers = data["papers"]
print(f"Total papers: {len(papers)}")

stats = data.get("_assessment_metadata", {}).get("statistics", {})
print(f"Verified: {stats.get('verified', 0)}, Excluded: {stats.get('excluded', 0)}, "
      f"Recheck: {stats.get('needs_recheck', 0)}")
print(f"Total entries: {stats.get('total_entries', 0)}, "
      f"Accepted: {stats.get('accepted_entries', 0)}, "
      f"Rejected: {stats.get('rejected_entries', 0)}")

# Verify no null decisions
null_count = 0
for p in papers:
    for section in ["problem_domains", "solution_approaches", "problem_solution_mappings",
                     "key_claims", "maturity_indicators", "open_questions"]:
        for e in p.get(section, []):
            if e.get("review", {}).get("decision") is None:
                null_count += 1
print(f"Entries with null decision: {null_count}")

# Verify all accepted entries have codes
no_codes = 0
for p in papers:
    for section in ["problem_domains", "solution_approaches", "problem_solution_mappings",
                     "key_claims", "maturity_indicators", "open_questions"]:
        for e in p.get(section, []):
            if e.get("review", {}).get("decision") == "accept" and not e.get("codes"):
                no_codes += 1
print(f"Accepted entries without codes: {no_codes}")

# Check taxonomy files exist
from pathlib import Path
for f in [
    "p1_framework_synthesis/s3_taxonomy/problem-space.md",
    "p1_framework_synthesis/s3_taxonomy/solution-space.md",
    "p1_framework_synthesis/s4_outputs/codebook.md",
    "p1_framework_synthesis/s4_outputs/conceptual-framework.md",
    "p1_framework_synthesis/audit-trail.md",
    "manuscript/07_Bibliography/references.bib",
    "manuscript/03_Chapters/02_Background.tex",
]:
    p = Path(f)
    size = p.stat().st_size if p.exists() else 0
    status = f"{size:,} bytes" if p.exists() else "MISSING"
    print(f"  {f}: {status}")

print("\nValidation complete.")
