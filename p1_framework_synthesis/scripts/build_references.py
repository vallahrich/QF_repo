"""
Phase 1 — Step 10: Populate references.bib from extraction metadata + foundational refs.

Reads review_data_done.json and generates BibTeX entries for all included papers
plus essential foundational and methodological references.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATA = ROOT / "s2_coding" / "review_data_done.json"
BIB_FILE = ROOT.parent / "manuscript" / "07_Bibliography" / "references.bib"


def author_key(authors: list[str], year: str) -> str:
    """Generate a cite key from authors and year."""
    if not authors:
        return f"Unknown{year}"
    # Take first author's last name
    first = authors[0]
    # Handle "Last, First" and "First Last" formats
    if "," in first:
        last = first.split(",")[0].strip()
    else:
        parts = first.strip().split()
        last = parts[-1] if parts else "Unknown"
    # Clean non-ascii
    last = re.sub(r'[^a-zA-Z]', '', last)
    return f"{last}{year}"


def format_authors_bibtex(authors: list[str]) -> str:
    """Format author list for BibTeX (Last, First and Last, First)."""
    formatted = []
    for a in authors:
        a = a.strip()
        if "," in a:
            formatted.append(a)
        else:
            parts = a.split()
            if len(parts) >= 2:
                formatted.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
            else:
                formatted.append(a)
    return " and ".join(formatted)


def escape_bibtex(s: str) -> str:
    """Escape special BibTeX characters."""
    if not s:
        return ""
    s = s.replace("&", r"\&")
    s = s.replace("%", r"\%")
    s = s.replace("#", r"\#")
    s = s.replace("_", r"\_")
    return s


def generate_entries(data: dict) -> list[str]:
    """Generate BibTeX entries from review_data_done.json papers."""
    entries = []
    used_keys = set()

    for paper in data["papers"]:
        review = paper.get("_review", {})
        if review.get("status") == "exclude":
            continue  # Skip excluded papers

        meta = paper.get("metadata", {})
        title = meta.get("title", "Unknown Title")
        authors = meta.get("authors", [])
        year = meta.get("year", "2025")
        venue = meta.get("venue", "")
        doc_type = meta.get("document_type", "academic-paper")

        key = author_key(authors, year)
        # Deduplicate keys
        if key in used_keys:
            suffix = "b"
            while f"{key}{suffix}" in used_keys:
                suffix = chr(ord(suffix) + 1)
            key = f"{key}{suffix}"
        used_keys.add(key)

        authors_bib = format_authors_bibtex(authors)
        title_bib = escape_bibtex(title)

        # Determine entry type
        if venue and "arxiv" in venue.lower():
            entry_type = "misc"
            venue_field = f"  note          = {{arXiv preprint: {escape_bibtex(venue)}}},"
        elif venue and ("book" in doc_type.lower() or "book" in (venue or "").lower()):
            entry_type = "incollection"
            venue_field = f"  booktitle     = {{{escape_bibtex(venue)}}},"
        elif venue and ("conference" in (venue or "").lower() or
                        "proceedings" in (venue or "").lower() or
                        "summit" in (venue or "").lower()):
            entry_type = "inproceedings"
            venue_field = f"  booktitle     = {{{escape_bibtex(venue)}}},"
        elif venue:
            entry_type = "article"
            venue_field = f"  journal       = {{{escape_bibtex(venue)}}},"
        else:
            entry_type = "misc"
            venue_field = f"  note          = {{Unpublished}},"

        entry = f"""@{entry_type}{{{key},
  author        = {{{authors_bib}}},
  title         = {{{{{title_bib}}}}},
  year          = {{{year}}},
{venue_field}
}}"""
        entries.append(entry)

    return entries


# ── Foundational references ────────────────────────────────────────────
FOUNDATIONAL_REFS = r"""
% ======================================================================
% FOUNDATIONAL REFERENCES — Quantum Computing
% ======================================================================

@book{NielsenChuang2010,
  author        = {Nielsen, Michael A. and Chuang, Isaac L.},
  title         = {{Quantum Computation and Quantum Information}},
  year          = {2010},
  edition       = {10th Anniversary},
  publisher     = {Cambridge University Press},
  address       = {Cambridge},
}

@article{Preskill2018,
  author        = {Preskill, John},
  title         = {{Quantum Computing in the NISQ Era and Beyond}},
  journal       = {Quantum},
  year          = {2018},
  volume        = {2},
  pages         = {79},
  doi           = {10.22331/q-2018-08-06-79},
}

@article{Shor1997,
  author        = {Shor, Peter W.},
  title         = {{Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer}},
  journal       = {SIAM Journal on Computing},
  year          = {1997},
  volume        = {26},
  number        = {5},
  pages         = {1484--1509},
  doi           = {10.1137/S0097539795293172},
}

@inproceedings{Grover1996,
  author        = {Grover, Lov K.},
  title         = {{A Fast Quantum Mechanical Algorithm for Database Search}},
  booktitle     = {Proceedings of the 28th Annual ACM Symposium on Theory of Computing (STOC)},
  year          = {1996},
  pages         = {212--219},
  doi           = {10.1145/237814.237866},
}

@article{Arute2019,
  author        = {Arute, Frank and Arya, Kunal and Babbush, Ryan and others},
  title         = {{Quantum Supremacy Using a Programmable Superconducting Processor}},
  journal       = {Nature},
  year          = {2019},
  volume        = {574},
  pages         = {505--510},
  doi           = {10.1038/s41586-019-1666-5},
}

@article{Hoefler2023,
  author        = {Hoefler, Torsten and H{\"a}ner, Thomas and Troyer, Matthias},
  title         = {{Disentangling Hype from Practicality: On Realistically Achieving Quantum Advantage}},
  journal       = {Communications of the ACM},
  year          = {2023},
  volume        = {66},
  number        = {5},
  pages         = {82--87},
  doi           = {10.1145/3571725},
}

@article{Farhi2014,
  author        = {Farhi, Edward and Goldstone, Jeffrey and Gutmann, Sam},
  title         = {{A Quantum Approximate Optimization Algorithm}},
  journal       = {arXiv preprint arXiv:1411.4028},
  year          = {2014},
}

@article{Peruzzo2014,
  author        = {Peruzzo, Alberto and McClean, Jarrod and Shadbolt, Peter and Yung, Man-Hong and Zhou, Xiao-Qi and Love, Peter J. and Aspuru-Guzik, Al{\'a}n and O'Brien, Jeremy L.},
  title         = {{A Variational Eigenvalue Solver on a Photonic Quantum Processor}},
  journal       = {Nature Communications},
  year          = {2014},
  volume        = {5},
  pages         = {4213},
  doi           = {10.1038/ncomms5213},
}

@article{HarrowHassidimLloyd2009,
  author        = {Harrow, Aram W. and Hassidim, Avinatan and Lloyd, Seth},
  title         = {{Quantum Algorithm for Linear Systems of Equations}},
  journal       = {Physical Review Letters},
  year          = {2009},
  volume        = {103},
  number        = {15},
  pages         = {150502},
  doi           = {10.1103/PhysRevLett.103.150502},
}

@article{Brassard2002,
  author        = {Brassard, Gilles and H{\o}yer, Peter and Mosca, Michele and Tapp, Alain},
  title         = {{Quantum Amplitude Amplification and Estimation}},
  journal       = {Contemporary Mathematics},
  year          = {2002},
  volume        = {305},
  pages         = {53--74},
}

% Quantum finance seminal works
@article{Rebentrost2018,
  author        = {Rebentrost, Patrick and Gupt, Brajesh and Bromley, Thomas R.},
  title         = {{Quantum Computational Finance: Monte Carlo Pricing of Financial Derivatives}},
  journal       = {Physical Review A},
  year          = {2018},
  volume        = {98},
  number        = {2},
  pages         = {022321},
  doi           = {10.1103/PhysRevA.98.022321},
}

@article{Stamatopoulos2020,
  author        = {Stamatopoulos, Nikitas and Egger, Daniel J. and Sun, Yue and Zoufal, Christa and Iten, Raban and Sber, Ning and Wo{\'e}rner, Stefan},
  title         = {{Option Pricing Using Quantum Computers}},
  journal       = {Quantum},
  year          = {2020},
  volume        = {4},
  pages         = {291},
  doi           = {10.22331/q-2020-07-06-291},
}

@article{Chakrabarti2021,
  author        = {Chakrabarti, Shouvanik and Krishnakumar, Rajiv and Mazzola, Guglielmo and Stamatopoulos, Nikitas and Wo{\"e}rner, Stefan and Zeng, William J.},
  title         = {{A Threshold for Quantum Advantage in Derivative Pricing}},
  journal       = {Quantum},
  year          = {2021},
  volume        = {5},
  pages         = {463},
  doi           = {10.22331/q-2021-06-01-463},
}

@article{Markowitz1952,
  author        = {Markowitz, Harry},
  title         = {{Portfolio Selection}},
  journal       = {The Journal of Finance},
  year          = {1952},
  volume        = {7},
  number        = {1},
  pages         = {77--91},
}

@article{Woerner2019,
  author        = {Wo{\"e}rner, Stefan and Egger, Daniel J.},
  title         = {{Quantum Risk Analysis}},
  journal       = {npj Quantum Information},
  year          = {2019},
  volume        = {5},
  pages         = {15},
  doi           = {10.1038/s41534-019-0130-6},
}

% ======================================================================
% METHODOLOGY REFERENCES
% ======================================================================

@incollection{Kitchenham2007,
  author        = {Kitchenham, Barbara and Charters, Stuart},
  title         = {{Guidelines for Performing Systematic Literature Reviews in Software Engineering}},
  booktitle     = {EBSE Technical Report},
  year          = {2007},
  publisher     = {Keele University and Durham University},
  number        = {EBSE-2007-01},
}

@article{EloKyngas2008,
  author        = {Elo, Satu and Kyng{\"a}s, Helvi},
  title         = {{The Qualitative Content Analysis Process}},
  journal       = {Journal of Advanced Nursing},
  year          = {2008},
  volume        = {62},
  number        = {1},
  pages         = {107--115},
  doi           = {10.1111/j.1365-2648.2007.04569.x},
}

@article{HsiehShannon2005,
  author        = {Hsieh, Hsiu-Fang and Shannon, Sarah E.},
  title         = {{Three Approaches to Qualitative Content Analysis}},
  journal       = {Qualitative Health Research},
  year          = {2005},
  volume        = {15},
  number        = {9},
  pages         = {1277--1288},
  doi           = {10.1177/1049732305276687},
}

@article{ArkseyOMalley2005,
  author        = {Arksey, Hilary and O'Malley, Lisa},
  title         = {{Scoping Studies: Towards a Methodological Framework}},
  journal       = {International Journal of Social Research Methodology},
  year          = {2005},
  volume        = {8},
  number        = {1},
  pages         = {19--32},
  doi           = {10.1080/1364557032000119616},
}

@article{BraunClarke2006,
  author        = {Braun, Virginia and Clarke, Victoria},
  title         = {{Using Thematic Analysis in Psychology}},
  journal       = {Qualitative Research in Psychology},
  year          = {2006},
  volume        = {3},
  number        = {2},
  pages         = {77--101},
  doi           = {10.1191/1478088706qp063oa},
}

@article{ThomasHarden2008,
  author        = {Thomas, James and Harden, Angela},
  title         = {{Methods for the Thematic Synthesis of Qualitative Research in Systematic Reviews}},
  journal       = {BMC Medical Research Methodology},
  year          = {2008},
  volume        = {8},
  pages         = {45},
  doi           = {10.1186/1471-2288-8-45},
}

@article{Page2021,
  author        = {Page, Matthew J. and McKenzie, Joanna E. and Bossuyt, Patrick M. and others},
  title         = {{The PRISMA 2020 Statement: An Updated Guideline for Reporting Systematic Reviews}},
  journal       = {BMJ},
  year          = {2021},
  volume        = {372},
  pages         = {n71},
  doi           = {10.1136/bmj.n71},
}

@book{Creswell2018,
  author        = {Creswell, John W. and Creswell, J. David},
  title         = {{Research Design: Qualitative, Quantitative, and Mixed Methods Approaches}},
  year          = {2018},
  edition       = {5th},
  publisher     = {SAGE Publications},
}

@book{Saunders2019,
  author        = {Saunders, Mark N. K. and Lewis, Philip and Thornhill, Adrian},
  title         = {{Research Methods for Business Students}},
  year          = {2019},
  edition       = {8th},
  publisher     = {Pearson Education},
}

@article{Wohlin2014,
  author        = {Wohlin, Claes},
  title         = {{Guidelines for Snowballing in Systematic Literature Studies and a Replication in Software Engineering}},
  journal       = {Proceedings of the 18th International Conference on Evaluation and Assessment in Software Engineering},
  year          = {2014},
  pages         = {1--10},
  doi           = {10.1145/2601248.2601268},
}

@article{Pare2015,
  author        = {Par{\'e}, Guy and Trudel, Marie-Claude and Jaana, Mirou and Kitsiou, Spyros},
  title         = {{Synthesizing Information Systems Knowledge: A Typology of Literature Reviews}},
  journal       = {Information \& Management},
  year          = {2015},
  volume        = {52},
  number        = {2},
  pages         = {183--199},
  doi           = {10.1016/j.im.2014.08.008},
}

@article{CruzesDyba2011,
  author        = {Cruzes, Daniela S. and Dyb{\aa}, Tore},
  title         = {{Recommended Steps for Thematic Synthesis in Software Engineering}},
  journal       = {International Symposium on Empirical Software Engineering and Measurement},
  year          = {2011},
  pages         = {275--284},
  doi           = {10.1109/ESEM.2011.36},
}

@article{FeredayMuirCochrane2006,
  author        = {Fereday, Jennifer and Muir-Cochrane, Eimear},
  title         = {{Demonstrating Rigor Using Thematic Analysis: A Hybrid Approach of Inductive and Deductive Coding and Theme Development}},
  journal       = {International Journal of Qualitative Methods},
  year          = {2006},
  volume        = {5},
  number        = {1},
  pages         = {80--92},
  doi           = {10.1177/160940690600500107},
}
"""


def main():
    # Load review data
    with open(REVIEW_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate entries from papers
    entries = generate_entries(data)
    print(f"Generated {len(entries)} BibTeX entries from review data")

    # Combine
    bib_content = "% ==========================================================================\n"
    bib_content += "% Master bibliography for thesis\n"
    bib_content += "% Quantum Computing in Financial Services — MSc Thesis, CBS\n"
    bib_content += "% Auto-generated from Phase 1 extraction metadata + foundational references\n"
    bib_content += "% Date: 2026-04-11\n"
    bib_content += "% ==========================================================================\n\n"

    bib_content += "% ======================================================================\n"
    bib_content += "% PHASE 1 CORPUS — Papers from exploratory framework synthesis\n"
    bib_content += "% ======================================================================\n\n"

    for entry in entries:
        bib_content += entry + "\n\n"

    bib_content += FOUNDATIONAL_REFS

    # Write
    BIB_FILE.write_text(bib_content, encoding="utf-8")
    print(f"Written: {BIB_FILE}")
    print(f"Total bibliography entries: {len(entries)} corpus + foundational refs")


if __name__ == "__main__":
    main()
