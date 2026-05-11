# Canonical Audit Namespace

This directory is the target namespace for canonical audit scripts.

The current files delegate to the compatibility-stable audit modules in [../](../). Audit JSON reports still live at their existing paths until a later report-layer migration moves them under `canonical/reports/audit/` together with the code that reads them.