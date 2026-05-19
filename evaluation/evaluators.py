"""Custom evaluator for HR ticket classification accuracy."""

import json


class ClassificationAccuracyEvaluator:
    """Measures field-level accuracy for ticket classification."""

    def __init__(self):
        self.id = "classification_accuracy"

    def __call__(self, *, response: str, ground_truth: str, **kwargs) -> dict:
        try:
            predicted = json.loads(response)
            expected = json.loads(ground_truth)
        except (json.JSONDecodeError, TypeError):
            return self._zero_scores()

        cat = self._match(predicted, expected, "category")
        subcat = self._match(predicted, expected, "subcategory")
        og = self._match_upper(predicted, expected, "operatorGroup")
        lang = self._match_upper(predicted, expected, "language")
        missing = self._missing_recall(predicted, expected)
        conf = self._confidence_calibration(predicted, expected)

        overall = cat * 0.30 + subcat * 0.25 + og * 0.20 + lang * 0.10 + missing * 0.10 + conf * 0.05
        return {
            "classification_accuracy": overall,
            "category_match": cat,
            "subcategory_match": subcat,
            "operator_group_match": og,
            "language_match": lang,
            "missing_info_recall": missing,
            "confidence_calibration": conf,
        }

    @staticmethod
    def _match(predicted: dict, expected: dict, field: str) -> float:
        return float(predicted.get(field, "").lower() == expected.get(field, "").lower())

    @staticmethod
    def _match_upper(predicted: dict, expected: dict, field: str) -> float:
        return float(predicted.get(field, "").upper() == expected.get(field, "").upper())

    @staticmethod
    def _missing_recall(predicted: dict, expected: dict) -> float:
        expected_set = set(m.lower() for m in expected.get("missingInfo", []))
        predicted_set = set(m.lower() for m in predicted.get("missingInfo", []))
        if not expected_set:
            return 1.0 if not predicted_set else 0.5
        matches = sum(
            1 for exp in expected_set
            if any(exp in pred or pred in exp for pred in predicted_set)
        )
        return matches / len(expected_set)

    @staticmethod
    def _confidence_calibration(predicted: dict, expected: dict) -> float:
        conf = predicted.get("confidence", 0.0)
        min_conf = expected.get("confidence_min", 0.5)
        return 1.0 if conf >= min_conf else conf / min_conf

    @staticmethod
    def _zero_scores() -> dict:
        return {
            "classification_accuracy": 0.0,
            "category_match": 0.0,
            "subcategory_match": 0.0,
            "operator_group_match": 0.0,
            "language_match": 0.0,
            "missing_info_recall": 0.0,
            "confidence_calibration": 0.0,
        }


class DocumentAnalysisEvaluator:
    """Measures accuracy of document analysis: validity detection, type classification, and doctor verification."""

    def __init__(self):
        self.id = "document_analysis_accuracy"

    def __call__(self, *, response: str, ground_truth: str, **kwargs) -> dict:
        try:
            predicted = json.loads(response)
            expected = json.loads(ground_truth)
        except (json.JSONDecodeError, TypeError):
            return self._zero_scores()

        validity = self._bool_match(predicted, expected, "documentValid")
        doc_type = self._str_match(predicted, expected, "documentType")
        recommendation = self._str_match(predicted, expected, "recommendation")
        doctor_verification = self._doctor_verification_match(predicted, expected)

        overall = validity * 0.30 + doc_type * 0.20 + recommendation * 0.25 + doctor_verification * 0.25

        return {
            "document_analysis_accuracy": overall,
            "validity_match": validity,
            "document_type_match": doc_type,
            "recommendation_match": recommendation,
            "doctor_verification_accuracy": doctor_verification,
        }

    @staticmethod
    def _bool_match(predicted: dict, expected: dict, field: str) -> float:
        return float(predicted.get(field) == expected.get(field))

    @staticmethod
    def _str_match(predicted: dict, expected: dict, field: str) -> float:
        p = str(predicted.get(field, "")).lower().strip()
        e = str(expected.get(field, "")).lower().strip()
        return float(p == e)

    @staticmethod
    def _doctor_verification_match(predicted: dict, expected: dict) -> float:
        expected_val = expected.get("doctor_verified_expected")
        if expected_val is None:
            # No verification expected (e.g., not a medical certificate)
            return 1.0
        predicted_val = predicted.get("doctorVerified", "").lower().strip()
        expected_val = expected_val.lower().strip()
        if predicted_val == expected_val:
            return 1.0
        # Partial credit: inconclusive when expected not_found or vice versa
        if {predicted_val, expected_val} == {"inconclusive", "not_found"}:
            return 0.5
        return 0.0

    @staticmethod
    def _zero_scores() -> dict:
        return {
            "document_analysis_accuracy": 0.0,
            "validity_match": 0.0,
            "document_type_match": 0.0,
            "recommendation_match": 0.0,
            "doctor_verification_accuracy": 0.0,
        }
