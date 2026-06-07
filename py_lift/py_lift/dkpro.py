T_ANOMALY      = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SpellingAnomaly'
T_DEP          = "de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency"
T_LEMMA        = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma"
T_MORPH        = "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.morph.Morpheme"
T_POS          = "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS"
T_RWSE         = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.RWSE'
T_SENT         = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"
T_SUGGESTION   = 'de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.SuggestedAction'
T_TOKEN        = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"

T_STRUCTURE    = 'org.lift.type.Structure'
T_FEATURE      = 'org.lift.type.FeatureAnnotationNumeric'
T_TREE         = 'org.lift.type.TreeStructure'

# Custom / dakoda layers used by the stage-annotation integration.
# T_POS above is the STTS (fine) POS layer; T_UPOS is the Universal POS layer.
T_UPOS         = "custom.UniversalDependencies.POS"
T_TOPOFIELD    = "custom.syntaxdot.topofield"
T_UDEP         = "org.dakoda.syntax.UDependency"
T_STAGE        = "org.dakoda.Stage"
T_STAGED_VERB  = "org.dakoda.StagedVerb"
