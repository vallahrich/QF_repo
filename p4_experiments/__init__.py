"""Phase 4 empirical validation package.

Legacy top-level silo imports are mapped to the professional evidence layout
under :mod:`p4_experiments.experiments.silos`.
"""

from __future__ import annotations

import importlib
import sys

_SILO_COMPAT_ALIASES = {
	"credit_lending": "credit_lending",
	"cryptography_security": "cryptography_security",
	"derivative_pricing": "derivative_pricing",
	"fraud_detection": "fraud_detection",
	"insurance_actuarial": "insurance_actuarial",
	"portfolio_optimization": "portfolio_optimization",
	"quantum_ml_finance": "quantum_ml_finance",
	"risk_management": "risk_management",
	"simulation_monte_carlo": "simulation_monte_carlo",
	"trading_execution": "trading_execution",
	"cross_silo_other": "other",
}

for _legacy_name, _target_name in _SILO_COMPAT_ALIASES.items():
	sys.modules.setdefault(
		f"{__name__}.{_legacy_name}",
		importlib.import_module(f"{__name__}.experiments.silos.{_target_name}"),
	)

del importlib, sys, _legacy_name, _target_name
