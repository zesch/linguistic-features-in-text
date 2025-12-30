import logging
from cassis import Cas
from py_lift.dkpro import T_FEATURE
from py_lift.util import load_lift_typesystem
from typing import Callable, Any, Optional, Union, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class FEL_BaseExtractor(ABC):
    """Marker base class for all extractors."""

    def __init__(self, strict: bool = False):
        self.strict = strict

    @abstractmethod
    def extract(self, cas: Cas) -> bool:
        pass

    def _feature_type(self, cas: Cas):
        # Hole Feature-Typ immer aus dem CAS-TypeSystem
        return cas.typesystem.get_type(T_FEATURE)

    def _add_feature(self, cas: Cas, name: str, value: Union[int, float, str]):
        F = self._feature_type(cas)
        cas.add(F(name=name, value=value, begin=0, end=0))

class FEL_BaseCounter(ABC):
    """Marker base class for all counters."""
    
    @abstractmethod
    def count(self, cas: Cas) -> int:
        pass

    @abstractmethod
    def feature_name(self) -> str:
        pass

class FEL_AnnotationCounter(FEL_BaseExtractor, FEL_BaseCounter):
    """Counts annotations of a specific type.
    For unique counts, a custom function can be provided to convert
    an annotation to a string representation.
    By default, the covered text is used."""

    def __init__(
        self,
        _type: str,
        unique: bool = False,
        custom_to_string: Optional[Callable[[Any], str]] = None,
        strict: bool = False
    ):
        super().__init__(strict=strict)
        self.type = _type
        self.unique = unique
        self.to_string = custom_to_string or self._default_to_string

    def _default_to_string(self, x: Any) -> str:
        try:
            return x.get_covered_text()
        except Exception:
            return str(x) if x is not None else ''

    def feature_name(self) -> str:
        return f"{self.type}_COUNT" + ("_UNIQUE" if self.unique else "")

    def count(self, cas: Cas) -> int:
        try:
            if not self.unique:
                return sum(1 for _ in cas.select(self.type))
            seen = set()
            for anno in cas.select(self.type):
                try:
                    s = self.to_string(anno)
                except Exception as e:
                    if self.strict:
                        raise
                    logger.debug("to_string failed: %s", e)
                    continue
                seen.add(s)
            return len(seen)
        except KeyError as e:
            # type not found in type system
            if self.strict:
                raise
            logger.warning("Type '%s' not found in CAS type system: %s", self.type, e)
            return 0

    def extract(self, cas: Cas) -> bool:
        count = self.count(cas)
        self._add_feature(cas, self.feature_name(), count)
        return True

def _sanitize(values: List[str]) -> List[str]:
    return [v.strip().lower() for v in values]

class FEL_FeatureValueCounter(FEL_BaseExtractor, FEL_BaseCounter):
    allowed_feature_values: List[str]

    def __init__(
        self,
        _type: str,
        feature_path: str,
        feature_values: Optional[Union[str, List[str]]] = None,
        count_only_if_feature_present: bool = False,
        strict: bool = False
    ):
        super().__init__(strict=strict)
        self.type = _type
        self.feature_path = feature_path
        self.count_only_if_feature_present = count_only_if_feature_present

        if feature_values is None:
            self.allowed_feature_values = []
        elif isinstance(feature_values, str):
            self.allowed_feature_values = _sanitize([feature_values])
        else:
            self.allowed_feature_values = _sanitize(list(feature_values))

    def feature_name(self) -> str:
        name = f"{self.type}"
        if self.allowed_feature_values:
            name += "_" + "_".join(self.allowed_feature_values)
        name += "_FEATURECOUNT"
        return name

    def _get_feature_value(self, anno) -> Optional[str]:
        try:
            v = anno.get(self.feature_path)
        except Exception:
            if self.strict:
                raise
            v = None
        if v is None:
            return None
        return str(v).strip().lower()

    def count(self, cas: Cas) -> int:
        cnt = 0
        for anno in cas.select(self.type):
            fv = self._get_feature_value(anno)
            if self.allowed_feature_values:
                if fv in self.allowed_feature_values:
                    cnt += 1
            else:
                # if no allowed feature values specified, count all
                if self.count_only_if_feature_present:
                    if fv is not None:
                        cnt += 1
                else:
                    cnt += 1
        return cnt

    def extract(self, cas: Cas) -> bool:
        self._add_feature(cas, self.feature_name(), self.count(cas))
        return True

class FEL_AnnotationRatio(FEL_BaseExtractor):
    def __init__(
        self,
        counter_dividend: FEL_BaseCounter,
        counter_divisor: FEL_BaseCounter,
        strict: bool = False,
        zero_division_policy: str = "zero"  # "zero", "nan", "skip", "raise"
    ):
        super().__init__(strict=strict)
        self.counter_dividend = counter_dividend
        self.counter_divisor = counter_divisor
        self.zero_division_policy = zero_division_policy

    def feature_name(self) -> str:
        return f"{self.counter_dividend.feature_name()}_PER_{self.counter_divisor.feature_name()}"

    def extract(self, cas: Cas) -> bool:
        a = self.counter_dividend.count(cas)
        b = self.counter_divisor.count(cas)

        if b == 0:
            if self.zero_division_policy == "raise" or self.strict:
                raise ZeroDivisionError(f"Division by zero for {self.feature_name()}")
            elif self.zero_division_policy == "nan":
                value = float('nan')
            elif self.zero_division_policy == "skip":
                logger.info("Skipping ratio %s due to zero divisor", self.feature_name())
                return False
            else:
                value = 0.0
        else:
            value = a / b

        self._add_feature(cas, self.feature_name(), value)
        return True

class FEL_Length(FEL_BaseExtractor):
    def __init__(self, annotation_type: str, strict: bool = False):
        super().__init__(strict=strict)
        self.annotation_type = annotation_type

    def extract(self, cas: Cas) -> bool:
        lengths = []
        for anno in cas.select(self.annotation_type):
            try:
                l = int(anno.end) - int(anno.begin)
                if l >= 0:
                    lengths.append(l)
            except Exception as e:
                if self.strict:
                    raise
                logger.debug("Invalid begin/end for %s: %s", self.annotation_type, e)

        if not lengths:
            logger.info("No values found for annotation: %s", self.annotation_type)
            # Optional: bei leerer Menge keine Features hinzufügen oder definierte Defaults
            return False

        min_val = min(lengths)
        max_val = max(lengths)
        mean = sum(lengths) / len(lengths)

        self._add_feature(cas, f"{self.annotation_type}_length_mean", mean)
        self._add_feature(cas, f"{self.annotation_type}_length_min", min_val)
        self._add_feature(cas, f"{self.annotation_type}_length_max", max_val)
        return True

class FEL_Min_Max_Mean(FEL_BaseExtractor):
    def __init__(self, annotation_type: str, feature_path: str, strict: bool = False):
        super().__init__(strict=strict)
        self.annotation_type = annotation_type
        self.feature_path = feature_path

    def _get_feature_value(self, anno) -> Optional[float]:
        try:
            v = anno.get(self.feature_path)
            if v is None or v == '':
                return None
            return float(v)
        except Exception as e:
            if self.strict:
                raise
            logger.debug("Non-numeric feature at %s.%s: %s", self.annotation_type, self.feature_path, e)
            return None

    def collect_values(self, cas: Cas) -> List[float]:
        vals = []
        for anno in cas.select(self.annotation_type):
            fv = self._get_feature_value(anno)
            if fv is not None:
                vals.append(fv)
        return vals

    def extract(self, cas: Cas) -> bool:
        vals = self.collect_values(cas)
        if not vals:
            logger.info("No numeric values found for %s.%s", self.annotation_type, self.feature_path)
            return False

        min_val = min(vals)
        max_val = max(vals)
        mean = sum(vals) / len(vals)

        self._add_feature(cas, f"{self.annotation_type}_mean", mean)
        self._add_feature(cas, f"{self.annotation_type}_min", min_val)
        self._add_feature(cas, f"{self.annotation_type}_max", max_val)
        return True
    
class FE_NumberOfSpellingAnomalies(FEL_AnnotationCounter):
    def __init__(self, strict: bool = False):
        super().__init__('SpellingAnomaly', strict=strict)

class FE_NounPhrasesPerSentence(FEL_AnnotationRatio):
    def __init__(self, strict: bool = False):
        super().__init__(
            FEL_AnnotationCounter('NC', strict=strict),
            FEL_AnnotationCounter('Sentence', strict=strict),
            strict=strict
        )

class FE_TokensPerSentence(FEL_AnnotationRatio):
    def __init__(self, strict: bool = False):
        super().__init__(
            FEL_AnnotationCounter('Token', strict=strict),
            FEL_AnnotationCounter('Sentence', strict=strict),
            strict=strict
        )

class FE_EasyWordRatio(FEL_AnnotationRatio):
    def __init__(self, strict: bool = False):
        super().__init__(
            FEL_AnnotationCounter('EasyWord', strict=strict),
            FEL_AnnotationCounter('Token', strict=strict),
            strict=strict
        )

class FE_AbstractnessStats(FEL_Min_Max_Mean):
    def __init__(self, strict: bool = False):
        super().__init__('org.lift.type.AbstractnessConcreteness', 'value', strict=strict)