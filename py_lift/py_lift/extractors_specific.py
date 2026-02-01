from cassis import Cas
from collections import Counter, defaultdict
from py_lift.extractors import FEL_BaseExtractor
from typing import Callable, Any, Optional, List, Dict, Union, Tuple

class FE_FreqBandRatios(FEL_BaseExtractor):
    """Extractor that computes the ratio of frequency bands per token. 
    Assumes that 'org.lift.type.Frequency' structure annotations are present in the CAS."""
    
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
    
    def extract(self, cas: Cas) -> bool:
        F = self.ts.get_type("FeatureAnnotationNumeric")
        
        # Count frequency bands
        band_counts = Counter(
            freq.frequencyBand 
            for freq in cas.select('org.lift.type.Frequency')
        )
        
        # Handle empty case
        total = sum(band_counts.values())
        if total == 0:
            return True  # or False, depending on your requirements
        
        # Define feature mappings
        feature_mappings = {
            'f1': 'Freq_Ratio_F1_PER_Token',
            'f2': 'Freq_Ratio_F2_PER_Token',
            'f3': 'Freq_Ratio_F3_PER_Token',
            'f4': 'Freq_Ratio_F4_PER_Token',
            'f5': 'Freq_Ratio_F5_PER_Token',
            'f6': 'Freq_Ratio_F6_PER_Token',
            'f7': 'Freq_Ratio_F7_PER_Token',
            'oov': 'Freq_Ratio_OOV_PER_Token'
        }
        
        # Create and add features
        for band, feature_name in feature_mappings.items():
            ratio = band_counts.get(band, 0) / total
            feature = F(name=feature_name, value=ratio, begin=0, end=0)
            cas.add(feature)

        if (self.verbose):
            self._print_distribution(band_counts, total)
        
        return True

    def _print_distribution(self, band_counts: dict, total: int):
        """Print frequency band distribution as stacked bar chart."""
        bands = list(sorted(band_counts.keys()))
        
        # Calculate ratios
        ratios = {band: band_counts.get(band, 0) / total for band in bands}
        total_ratio = sum(ratios.values())
        
        print(f"\n{'='*70}")
        print(f"Frequency Band Distribution (total: {total}, sum: {total_ratio:.4f})")
        print('='*70)
        
        # Individual bars
        for band in bands:
            ratio = ratios[band]
            percentage = ratio * 100
            bar_length = int(ratio * 50)
            bar = '█' * bar_length
            count = band_counts.get(band, 0)
            print(f"{band:>4}: {bar:<50} {percentage:5.1f}% ({count:>4})")
        
        print('='*70)

### syntax

class FE_DependencyAndTreeStats(FEL_BaseExtractor):
    """
    Extraktor für Abhängigkeitslängen- und Baumtiefen-Statistiken.
    Erwartet im CAS:
      - de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency
        (Governor, Dependent, DependencyType)
      - de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token (order)
      - org.lift.type.TreeStructure (maxDepth)
    """

    def __init__(
        self,
        dep_type: str = "de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency",
        token_type: str = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
        tree_type: str = "org.lift.type.TreeStructure",
        strict: bool = False
    ):
        super().__init__(strict=strict)
        self.dep_type = dep_type
        self.token_type = token_type
        self.tree_type = tree_type

    def _get_token_order(self, token):
        try:
            return int(token.get("begin"))
        except Exception:
            return None

    def _get_token_by_xmi_id(self, cas, xmi_id):
        for token in cas.select(self.token_type):
            if getattr(token, "xmi_id", None) == xmi_id:
                return token
        return None

    def _get_dependency_length_counter(self, cas, excluded_rels=["root", "punct"]) -> Dict[str, Counter]:
        counter_per_rel = {}
        for dep in cas.select(self.dep_type):
            try:
                rel = dep.get("DependencyType")
                if rel is None or rel.lower() in excluded_rels:
                    continue
                gov = dep.get("Governor")
                depn = dep.get("Dependent")
                # Falls gov/depn keine Annotation, sondern nur Referenz/ID:
                gov_token = gov
                depn_token = depn
                # Falls es keine Annotation ist, sondern ein Referenzobjekt oder nur die ID:
                if not hasattr(gov, "get"):
                    gov_token = self._get_token_by_xmi_id(cas, gov.xmi_id if hasattr(gov, "xmi_id") else gov)
                if not hasattr(depn, "get"):
                    depn_token = self._get_token_by_xmi_id(cas, depn.xmi_id if hasattr(depn, "xmi_id") else depn)
                gov_ord = self._get_token_order(gov_token)
                depn_ord = self._get_token_order(depn_token)
                if gov_ord is None or depn_ord is None:
                    continue
                diff = depn_ord - gov_ord
                if rel not in counter_per_rel:
                    counter_per_rel[rel] = Counter()
                counter_per_rel[rel][diff] += 1
            except Exception as e:
                print("Exception:", e)
                continue
        return counter_per_rel



    def _get_average_from_counter(self, mycounter):
        insts = 0
        totlen = 0
        for lng in mycounter:
            totlen += mycounter[lng] * abs(lng)
            insts += mycounter[lng]
        try:
            avg_dep_len = round(float(totlen / insts), 2)
        except Exception:
            avg_dep_len = 0
        return avg_dep_len

    def _get_dependency_lengths_across_all_rels_in_doc(
        self, counts_per_rel: Dict
    ) -> Tuple:
        leftward = Counter()
        rightward = Counter()
        for rel in counts_per_rel.keys():
            ctr = counts_per_rel[rel]
            for kee in ctr.keys():
                if kee < 0:
                    if not abs(kee) in leftward:
                        leftward[abs(kee)] = 0
                    leftward[abs(kee)] += ctr[kee]
                elif kee > 0:
                    if not kee in rightward:
                        rightward[kee] = 0
                    rightward[kee] += ctr[kee]
                else:
                    continue
        anydir = leftward + rightward
        avg_left = self._get_average_from_counter(leftward)
        avg_right = self._get_average_from_counter(rightward)
        avg_all = self._get_average_from_counter(anydir)
        return (avg_left, avg_right, avg_all)

    def _get_max_dep_lengths_per_sentence(self, cas, excluded_rels=["root", "punct"]) -> list:
        # Gruppiere Dependencies nach Satz (Governor/Dependent sollten im selben Satz liegen)
        # Wir nutzen die begin/end-Offsets als Satz-Identifikator
        # Annahme: Token haben begin/end, Dependency zeigt auf Token
        sentence_map = defaultdict(list)
        for dep in cas.select(self.dep_type):
            try:
                rel = dep.get("DependencyType")
                if rel is None or rel.lower() in excluded_rels:
                    continue
                gov = dep.get("Governor")
                depn = dep.get("Dependent")
                gov_ord = self._get_token_order(gov)
                depn_ord = self._get_token_order(depn)
                if gov_ord is None or depn_ord is None:
                    continue
                # Satz-ID: begin-offset des Governors (alternativ: begin-offset des Satzes, falls vorhanden)
                sent_id = getattr(gov, "begin", None)
                sentence_map[sent_id].append(abs(depn_ord - gov_ord))
            except Exception:
                continue
        max_lengths = []
        for sent_id, lens in sentence_map.items():
            if lens:
                max_lengths.append(max(lens))
        return max_lengths

    def _get_avg_max_dep_length(self, cas) -> float:
        max_lengths = self._get_max_dep_lengths_per_sentence(cas)
        if max_lengths:
            return round(sum(max_lengths) / len(max_lengths), 2)
        else:
            return 0.0

    def _get_avg_tree_depth(self, cas) -> float:
        depths = []
        for anno in cas.select(self.tree_type):
            try:
                d = float(anno.get("maxDepth"))
                depths.append(d)
            except Exception:
                continue
        if depths:
            return round(sum(depths) / len(depths), 2)
        else:
            return 0.0

    def extract(self, cas) -> bool:
        # Dependency lengths direkt aus Dependency-Annotation berechnen
        counts_per_rel = self._get_dependency_length_counter(cas)
        avg_left_dep_len, avg_right_dep_len, avg_all_dep_len = self._get_dependency_lengths_across_all_rels_in_doc(counts_per_rel)
        self._add_feature(cas, "Average_Dependency_Length_Left", avg_left_dep_len)
        self._add_feature(cas, "Average_Dependency_Length_Right", avg_right_dep_len)
        self._add_feature(cas, "Average_Dependency_Length_All", avg_all_dep_len)

        # Average maximal dependency length (berechnet pro Satz, dann gemittelt)
        avg_max_dep_len = self._get_avg_max_dep_length(cas)
        self._add_feature(cas, "Average_Maximal_Dependency_Length", avg_max_dep_len)

        # Average tree depth
        avg_tree_depth = self._get_avg_tree_depth(cas)
        self._add_feature(cas, "Average_Tree_Depth", avg_tree_depth)

        return True

class FE_Per1kTokenStats(FEL_BaseExtractor):
    """
    Extraktor für X_per_1k_tokens für verschiedene Annotationstypen.
    Erwartet im CAS:
      - TokenCount (value)
      - ConjunctionCount (value)
      - SubordinatorCount (value)
      - AdpositionCount (value)
      - PrepositionCount (value)
      - PostpositionCount (value)
      - RelativePronounCount (value)
      - PersonalPronounCount (value)
    """

    def __init__(
        self,
        token_type: str = "TokenCount",
        conj_type: str = "ConjunctionCount",
        subord_type: str = "SubordinatorCount",
        adp_type: str = "AdpositionCount",
        prep_type: str = "PrepositionCount",
        postp_type: str = "PostpositionCount",
        relpron_type: str = "RelativePronounCount",
        perspron_type: str = "PersonalPronounCount",
        strict: bool = False
    ):
        super().__init__(strict=strict)
        self.token_type = token_type
        self.conj_type = conj_type
        self.subord_type = subord_type
        self.adp_type = adp_type
        self.prep_type = prep_type
        self.postp_type = postp_type
        self.relpron_type = relpron_type
        self.perspron_type = perspron_type

    def _collect_values(self, cas, annotation_type):
        vals = []
        for anno in cas.select(annotation_type):
            try:
                v = float(anno.get("value"))
                vals.append(v)
            except Exception:
                continue
        return vals

    def extract(self, cas) -> bool:
        token_vals = self._collect_values(cas, self.token_type)
        conj_vals = self._collect_values(cas, self.conj_type)
        subord_vals = self._collect_values(cas, self.subord_type)
        adp_vals = self._collect_values(cas, self.adp_type)
        prep_vals = self._collect_values(cas, self.prep_type)
        postp_vals = self._collect_values(cas, self.postp_type)
        relpron_vals = self._collect_values(cas, self.relpron_type)
        perspron_vals = self._collect_values(cas, self.perspron_type)

        REF_TEXT_SIZE = 1000
        doc_length = sum(token_vals) if token_vals else 1  # Schutz vor Division durch 0

        def per_1k(vals):
            return round(REF_TEXT_SIZE * (sum(vals) / doc_length), 2) if doc_length > 0 else 0.0

        self._add_feature(cas, "Conjunctions_per_1k_tokens", per_1k(conj_vals))
        self._add_feature(cas, "Subordinators_per_1k_tokens", per_1k(subord_vals))
        self._add_feature(cas, "Adpositions_per_1k_tokens", per_1k(adp_vals))
        self._add_feature(cas, "Prepositions_per_1k_tokens", per_1k(prep_vals))
        self._add_feature(cas, "Postpositions_per_1k_tokens", per_1k(postp_vals))
        self._add_feature(cas, "Relative_pronouns_per_1k_tokens", per_1k(relpron_vals))
        self._add_feature(cas, "Personal_pronouns_per_1k_tokens", per_1k(perspron_vals))

        return True