from collections import Counter, defaultdict
from typing import List, Dict, Set, Tuple

from cassis import Cas
from py_lift.dkpro import T_SENT, T_TOKEN, T_DEP
from py_lift.extractors import FEL_BaseExtractor

# ------ STTS / Tiger Annahmen ------

# finite Verben (breit gefasst)
FINITE_VERBS_STTS_BROAD = [
    "VVFIN", "VVIMP",
    "VMFIN", "VMIMP",
    "VAFIN", "VAIMP",
]

# nicht-finite Verben
NONFINITE_VERBS_STTS_BROAD = [
    "VVPP", "VAPP", "VMPP",
    "VVINF", "VAINF", "VMINF", "VVIZU",
]

ALL_VERB_TAGS_STTS = FINITE_VERBS_STTS_BROAD + NONFINITE_VERBS_STTS_BROAD

# finite Modal/Aux für Verbklammern
FINITE_MOD_AUX_STTS = ["VMFIN", "VAFIN"]

# Modalverben (hier: alle STTS-Tags, die mit VM beginnen – ggf. anpassen)
MODAL_VERB_TAGS = [
    "VMFIN", "VMINF", "VMIMP", "VMPP"
]

# Lexikalische Nomen (TIGER)
LEXICAL_NOUN_TAGS = ["NN", "NE"]

# Subjektrelationen (TIGER)
SUBJECT_DEPRELS = {"sb", "ep"}  # in .lower()

# Koordination (TIGER)
COORDINATOR_REL = "cd"
CONJUNCT_REL = "cj"

# Konjunktion für Share_of_conj_uses_without_left_clause
DEFAULT_CONJ_LEMMA = "und"



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


class FE_CountCategoryAnnotator:
    """
    Zählt für jede Kategorie (z.B. Konjunktionen, Subordinatoren, Adpositionen, ...)
    die passenden Tokens und schreibt eine
    org.lift.type.FeatureAnnotationNumeric-Annotation mit
    name=<Kategorie> und value=<Anzahl> ins CAS.
    """

    CATEGORY_SPECS = [
        ("ConjunctionCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["KON"]}),
        ("SubordinatorCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["KOUI", "KOUS"]}),
        ("AdpositionCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["APPR", "APPRART", "APPO", "APZR"]}),
        ("PrepositionCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["APPR", "APPRART"]}),
        ("PostpositionCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["APPO"]}),
        ("RelativePronounCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["PRELAT", "PRELS"]}),
        ("PersonalPronounCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         {"pos.PosValue": ["PPER", "PRF"]}),
        ("TokenCount",
         "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
         None),
    ]

    def __init__(self, strict: bool = False):
        self.strict = strict

    def _get_feature_value(self, fs, path: str):
        obj = fs
        for part in path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                return None
        return obj

    def extract(self, cas: Cas) -> bool:
        F = cas.typesystem.get_type("org.lift.type.FeatureAnnotationNumeric")

        for count_type, token_type, filter_dict in self.CATEGORY_SPECS:
            count = 0
            for tok in cas.select(token_type):
                if filter_dict is None:
                    count += 1
                else:
                    for feat, allowed in filter_dict.items():
                        value = self._get_feature_value(tok, feat)
                        if value not in allowed:
                            break
                    else:
                        # alle Features haben gepasst
                        count += 1

            print('Counter test -------------------------------------------------------------')
            print(count_type + ' - ' + str(count))
            fs = F(name=count_type, value=float(count), begin=0, end=0)
            cas.add(fs)

        return True
    # Ende Klasse

class FE_Per1kTokenStats(FEL_BaseExtractor):
    """
    Extraktor für X_per_1k_tokens für verschiedene Kategorien.

    Erwartet im CAS bereits org.lift.type.FeatureAnnotationNumeric mit:
      - name="TokenCount"
      - name="ConjunctionCount"
      - name="SubordinatorCount"
      - name="AdpositionCount"
      - name="PrepositionCount"
      - name="PostpositionCount"
      - name="RelativePronounCount"
      - name="PersonalPronounCount"
    """

    FEATURE_SPECS = [
        ("Conjunctions_per_1k_tokens", "ConjunctionCount"),
        ("Subordinators_per_1k_tokens", "SubordinatorCount"),
        ("Adpositions_per_1k_tokens", "AdpositionCount"),
        ("Prepositions_per_1k_tokens", "PrepositionCount"),
        ("Postpositions_per_1k_tokens", "PostpositionCount"),
        ("Relative_pronouns_per_1k_tokens", "RelativePronounCount"),
        ("Personal_pronouns_per_1k_tokens", "PersonalPronounCount"),
    ]

    def __init__(self, token_feature_name: str = "TokenCount", strict: bool = False):
        super().__init__(strict=strict)
        self.token_feature_name = token_feature_name

    def _get_numeric_feature(self, cas: Cas, feature_name: str, default: float = 0.0) -> float:
        for fa in cas.select("org.lift.type.FeatureAnnotationNumeric"):
            if getattr(fa, "name", None) == feature_name:
                try:
                    return float(fa.value)
                except (TypeError, ValueError):
                    return default
        if self.strict:
            raise ValueError(f"FeatureAnnotationNumeric mit name='{feature_name}' nicht gefunden")
        return default

    def extract(self, cas: Cas) -> bool:
        REF_TEXT_SIZE = 1000.0

        # Gesamtzahl Tokens aus FeatureAnnotationNumeric "TokenCount"
        token_count = self._get_numeric_feature(cas, self.token_feature_name, default=0.0)
        if token_count <= 0:
            token_count = 1.0  # Schutz vor Division durch 0

        for out_name, count_name in self.FEATURE_SPECS:
            count_value = self._get_numeric_feature(cas, count_name, default=0.0)
            per_1k = REF_TEXT_SIZE * (count_value / token_count)
            value = round(per_1k, 2)

            # schreibt eine org.lift.type.FeatureAnnotationNumeric mit name=out_name, value=value
            self._add_feature(cas, out_name, value)

        return True




class FE_LG_DocumentStats(FEL_BaseExtractor):
    """
    Berechnet dokumentweite lexikalisch-grammatische Kennzahlen und
    schreibt sie als org.lift.type.FeatureAnnotationNumeric in den CAS.

    Erzeugte Features (name-Feld der FeatureAnnotationNumeric):

      - Share_of_conj_uses_without_left_clause
      - Proportion_S_without_finite_verb
      - Proportion_of_modal_verbs_out_of_all_verbs
      - Proportion_S_without_verb
      - Proportion_of_missing_verbal_brackets
      - Proportion_of_switched_brackets
      - Proportion_of_canonical_brackets
      - Proportion_of_brackets_with_empty_midfields
      - Proportion_of_Subj_Vfin_Inversions
      - Proportion_of_subjectless_finite_verbs
      - Proportion_of_coordination_between_verbs
      - Average_Size_Of_Lexical_NP

    Annahme: STTS-POS + Tiger-ähnliche Dependenzlabels (s.o.).
    """

    def __init__(self, strict: bool = False):
        super().__init__(strict=strict)

    # ---------- Hilfsfunktionen ----------

    def _get_pos(self, tok) -> str | None:
        pos = getattr(tok, "pos", None)
        if pos is None:
            return None
        return getattr(pos, "PosValue", None)

    def _get_lemma_or_form(self, tok) -> str | None:
        # Lemma falls vorhanden, sonst Oberflächenform
        lemma_fs = getattr(tok, "lemma", None)
        lemma = getattr(lemma_fs, "value", None)
        if lemma:
            return str(lemma).lower()
        try:
            return tok.get_covered_text().lower()
        except Exception:
            return None

    def _subtree_size(self, root_tok, deps_by_governor: Dict, sent_tokens: Set) -> int:
        """
        Größe des Dependenzunterbaums (root + alle Nachkommen), beschränkt auf Tokens im Satz.
        """
        visited = {root_tok}
        queue = [root_tok]
        while queue:
            cur = queue.pop(0)
            for dep in deps_by_governor.get(cur, []):
                child = dep.Dependent
                if child in sent_tokens and child not in visited:
                    visited.add(child)
                    queue.append(child)
        return len(visited)

    # ---------- Hauptlogik ----------

    def extract(self, cas: Cas) -> bool:
        view = cas  # wir arbeiten auf der Default-View

        sentences = sorted(view.select(T_SENT), key=lambda s: (s.begin, s.end))
        tokens_all = sorted(view.select(T_TOKEN), key=lambda t: (t.begin, t.end))
        deps_all = list(view.select(T_DEP))

        if not sentences:
            # kein Satz annotiert – nichts zu tun
            return False

        # Caches
        pos_cache = {tok: self._get_pos(tok) for tok in tokens_all}
        lemma_cache = {tok: self._get_lemma_or_form(tok) for tok in tokens_all}

        deps_by_governor: Dict[object, list] = defaultdict(list)
        deps_by_dependent: Dict[object, list] = defaultdict(list)
        for dep in deps_all:
            deps_by_governor[dep.Governor].append(dep)
            deps_by_dependent[dep.Dependent].append(dep)

        # "Registry"-ähnliche Sammler
        finite_verb_counts: List[int] = []
        total_verb_counts: List[int] = []
        modal_verb_counts: List[int] = []
        sent_lengths: List[int] = []
        verbal_bracket_cands: List[int] = []
        subj_position_values: List[int] = []        # 1: Subj nach Vfin, -1: Subj vor Vfin
        subjectless_finite_verbs = 0
        coordination_is_between_verbs: List[bool] = []
        lex_np_sizes: List[int] = []
        conj_rel_counter: Counter[str] = Counter()

        # Token-Satz-Zuordnung effizienter machen
        n_tokens = len(tokens_all)
        token_idx = 0

        for sent in sentences:
            # Tokens im Satz
            sent_tokens: List[object] = []
            while token_idx < n_tokens and tokens_all[token_idx].end <= sent.begin:
                token_idx += 1
            j = token_idx
            while j < n_tokens and tokens_all[j].begin < sent.end:
                sent_tokens.append(tokens_all[j])
                j += 1

            if not sent_tokens:
                # leerer Satz – überspringen
                continue

            sent_token_set = set(sent_tokens)
            idx_of_token = {tok: i + 1 for i, tok in enumerate(sent_tokens)}

            sent_lengths.append(len(sent_tokens))

            # --- Verbzählungen pro Satz ---
            finite_count = sum(
                1
                for tok in sent_tokens
                if pos_cache.get(tok) in FINITE_VERBS_STTS_BROAD
            )
            finite_verb_counts.append(finite_count)

            verb_count = sum(
                1
                for tok in sent_tokens
                if pos_cache.get(tok) in ALL_VERB_TAGS_STTS
            )
            total_verb_counts.append(verb_count)

            modal_count = sum(
                1
                for tok in sent_tokens
                if pos_cache.get(tok) in MODAL_VERB_TAGS
            )
            modal_verb_counts.append(modal_count)

            # --- Lexikalische NPs ---
            for tok in sent_tokens:
                if pos_cache.get(tok) in LEXICAL_NOUN_TAGS:
                    size = self._subtree_size(tok, deps_by_governor, sent_token_set)
                    lex_np_sizes.append(size)

            # --- Subjektposition & subjectless finite verbs ---
            for tok in sent_tokens:
                if pos_cache.get(tok) in FINITE_VERBS_STTS_BROAD:
                    children_deps = [
                        d for d in deps_by_governor.get(tok, [])
                        if d.Dependent in sent_token_set
                    ]
                    subj_children = [
                        d.Dependent for d in children_deps
                        if (d.DependencyType or "").lower() in SUBJECT_DEPRELS
                    ]
                    if not subj_children:
                        subjectless_finite_verbs += 1
                        continue

                    v_idx = idx_of_token[tok]
                    rel_pos = 0
                    for subj_tok in subj_children:
                        s_idx = idx_of_token.get(subj_tok)
                        if s_idx is None:
                            continue
                        if s_idx > v_idx:
                            rel_pos = 1
                            break
                        elif s_idx < v_idx:
                            rel_pos = -1
                            break
                    if rel_pos != 0:
                        subj_position_values.append(rel_pos)

            # --- Verbklammer-Kandidaten ---
            for tok in sent_tokens:
                if pos_cache.get(tok) in FINITE_MOD_AUX_STTS:
                    children_deps = [
                        d for d in deps_by_governor.get(tok, [])
                        if d.Dependent in sent_token_set
                    ]
                    inf_children = [
                        d.Dependent for d in children_deps
                        if pos_cache.get(d.Dependent) in NONFINITE_VERBS_STTS_BROAD
                    ]
                    for inf_tok in inf_children:
                        v_idx = idx_of_token[tok]
                        inf_idx = idx_of_token[inf_tok]
                        if inf_idx > v_idx:
                            if inf_idx - v_idx == 1:
                                verbal_bracket_cands.append(0)  # leeres Mittelfeld
                            else:
                                verbal_bracket_cands.append(1)  # nicht-leeres Mittelfeld
                        else:
                            verbal_bracket_cands.append(-1)     # non-finite vor finite

            # --- Konjunktions-Relationen für DEFAULT_CONJ_LEMMA ---
            for tok in sent_tokens:
                lemma = lemma_cache.get(tok)
                if lemma == DEFAULT_CONJ_LEMMA:
                    for dep in deps_by_dependent.get(tok, []):
                        if dep.Governor in sent_token_set:
                            conj_rel_counter[dep.DependencyType or ""] += 1

            # --- Koordination zwischen Verben ---
            for dep in deps_all:
                if dep.Dependent not in sent_token_set:
                    continue
                rel = (dep.DependencyType or "").lower()
                if rel != COORDINATOR_REL:
                    continue
                conj_tok = dep.Dependent
                gov_tok = dep.Governor
                if gov_tok not in sent_token_set:
                    continue
                gov_pos = pos_cache.get(gov_tok)
                if gov_pos not in ALL_VERB_TAGS_STTS:
                    coordination_is_between_verbs.append(False)
                else:
                    child_deps = [
                        d2 for d2 in deps_by_governor.get(conj_tok, [])
                        if d2.Dependent in sent_token_set
                    ]
                    found = any(
                        (d2.DependencyType or "").lower() == CONJUNCT_REL
                        and pos_cache.get(d2.Dependent) in ALL_VERB_TAGS_STTS
                        for d2 in child_deps
                    )
                    coordination_is_between_verbs.append(found)

        # ---------- Feature-Berechnung & Schreiben ----------

        n_sents = len(sent_lengths)

        # 1) Share_of_conj_uses_without_left_clause (Rel "ju" für "und")
        total_conj_uses = sum(conj_rel_counter.values())
        if total_conj_uses > 0:
            share_of_conj_uses_without_left_clause = round(
                conj_rel_counter.get("ju", 0) / total_conj_uses, 2
            )
        else:
            share_of_conj_uses_without_left_clause = 0.0

        self._add_feature(
            cas,
            "Share_of_conj_uses_without_left_clause",
            share_of_conj_uses_without_left_clause,
        )

        # 2) Proportion_S_without_finite_verb
        if n_sents > 0:
            no_fin_verb_count = finite_verb_counts.count(0)
            proportion_s_without_fin_verb = round(
                no_fin_verb_count / n_sents, 2
            )
        else:
            proportion_s_without_fin_verb = 0.0

        self._add_feature(
            cas,
            "Proportion_S_without_finite_verb",
            proportion_s_without_fin_verb,
        )

        # 3) Proportion_of_modal_verbs_out_of_all_verbs
        total_verbs = sum(total_verb_counts)
        if total_verbs > 0:
            proportion_modal_verbs_out_of_all_verbs = round(
                sum(modal_verb_counts) / total_verbs, 2
            )
        else:
            proportion_modal_verbs_out_of_all_verbs = 0.0

        self._add_feature(
            cas,
            "Proportion_of_modal_verbs_out_of_all_verbs",
            proportion_modal_verbs_out_of_all_verbs,
        )

        # 4) Proportion_S_without_verb
        if n_sents > 0:
            no_verb_count = total_verb_counts.count(0)
            proportion_s_without_verb = round(
                no_verb_count / n_sents, 2
            )
        else:
            proportion_s_without_verb = 0.0

        self._add_feature(
            cas,
            "Proportion_S_without_verb",
            proportion_s_without_verb,
        )

        # 5–8) Verbklammern
        bracket_ctr = Counter(verbal_bracket_cands)
        totcands = sum(bracket_ctr.values())
        if totcands == 0:
            proportion_of_missing_brackets = 0.00
            proportion_of_switched_brackets = 0.00
            proportion_of_standard_sequenced_brackets = 0.00
            proportion_of_brackets_with_empty_midfields = 0.00
        else:
            # 999 kommt hier nicht vor – entspricht dem Verhalten deines alten Codes
            proportion_of_missing_brackets = 0.00
            proportion_of_switched_brackets = round(
                bracket_ctr[-1] / totcands, 2
            )
            proportion_of_standard_sequenced_brackets = round(
                (bracket_ctr[0] + bracket_ctr[1]) / totcands, 2
            )
            if bracket_ctr[0] + bracket_ctr[1] > 0:
                proportion_of_brackets_with_empty_midfields = round(
                    bracket_ctr[0] / (bracket_ctr[0] + bracket_ctr[1]), 2
                )
            else:
                proportion_of_brackets_with_empty_midfields = 0.00

        self._add_feature(
            cas,
            "Proportion_of_missing_verbal_brackets",
            proportion_of_missing_brackets,
        )
        self._add_feature(
            cas,
            "Proportion_of_switched_brackets",
            proportion_of_switched_brackets,
        )
        self._add_feature(
            cas,
            "Proportion_of_canonical_brackets",
            proportion_of_standard_sequenced_brackets,
        )
        self._add_feature(
            cas,
            "Proportion_of_brackets_with_empty_midfields",
            proportion_of_brackets_with_empty_midfields,
        )

        # 9) Proportion_of_Subj_Vfin_Inversions
        if subj_position_values:
            n_after = subj_position_values.count(1)
            n_before = subj_position_values.count(-1)
            denom = n_before + n_after
            if denom > 0:
                share_of_s_vfin_inversions = round(n_after / denom, 2)
            else:
                share_of_s_vfin_inversions = 0.0
        else:
            share_of_s_vfin_inversions = 0.0

        self._add_feature(
            cas,
            "Proportion_of_Subj_Vfin_Inversions",
            share_of_s_vfin_inversions,
        )

        # 10) Proportion_of_subjectless_finite_verbs
        total_finite_verbs = subjectless_finite_verbs + len(subj_position_values)
        if total_finite_verbs > 0:
            proportion_of_subjectless_finite_verbs = round(
                subjectless_finite_verbs / total_finite_verbs, 2
            )
        else:
            proportion_of_subjectless_finite_verbs = 0.0

        self._add_feature(
            cas,
            "Proportion_of_subjectless_finite_verbs",
            proportion_of_subjectless_finite_verbs,
        )

        # 11) Proportion_of_coordination_between_verbs
        if coordination_is_between_verbs:
            n_true = coordination_is_between_verbs.count(True)
            share_of_verbal_coordinations = round(
                n_true / len(coordination_is_between_verbs), 2
            )
        else:
            share_of_verbal_coordinations = 0.0

        self._add_feature(
            cas,
            "Proportion_of_coordination_between_verbs",
            share_of_verbal_coordinations,
        )

        # 12) Average_Size_Of_Lexical_NP
        if lex_np_sizes:
            avg_lex_np_size = round(
                sum(lex_np_sizes) / len(lex_np_sizes), 2
            )
        else:
            avg_lex_np_size = 0.0

        self._add_feature(
            cas,
            "Average_Size_Of_Lexical_NP",
            avg_lex_np_size,
        )

        # 13) Average_Number_Of_Finite_Verbs
        if finite_verb_counts:
            avg_finite_verbs = round(
                sum(finite_verb_counts) / len(finite_verb_counts), 2
            )
        else:
            avg_finite_verbs = 0.0

        self._add_feature(
            cas,
            "Average_Number_Of_Finite_Verbs",
            avg_finite_verbs,
        )

        # 14) Average_Number_Of_Verbs
        if total_verb_counts:
            avg_total_verbs = round(
                sum(total_verb_counts) / len(total_verb_counts), 2
            )
        else:
            avg_total_verbs = 0.0

        self._add_feature(
            cas,
            "Average_Number_Of_Verbs",
            avg_total_verbs,
        )

        return True