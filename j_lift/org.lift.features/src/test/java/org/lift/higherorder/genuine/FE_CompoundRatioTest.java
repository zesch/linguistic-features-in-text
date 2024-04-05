package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.apache.uima.fit.factory.ExternalResourceFactory.createResourceDescription;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Set;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.decompounding.uima.annotator.CompoundAnnotator;
import org.dkpro.core.decompounding.uima.resource.AsvToolboxSplitterResource;
import org.dkpro.core.decompounding.uima.resource.SharedDictionary;
import org.dkpro.core.decompounding.uima.resource.SharedLinkingMorphemes;
import org.dkpro.core.decompounding.uima.resource.SharedPatriciaTries;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SE_Compound;

class FE_CompoundRatioTest {

	@Test
	void compoundRatioTest() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "de");
		AnalysisEngineDescription compoundAnnotator = createEngineDescription(CompoundAnnotator.class,
				CompoundAnnotator.RES_SPLITTING_ALGO,
				createResourceDescription(AsvToolboxSplitterResource.class,
						AsvToolboxSplitterResource.PARAM_DICT_RESOURCE,
						createResourceDescription(SharedDictionary.class),
						AsvToolboxSplitterResource.PARAM_MORPHEME_RESOURCE,
						createResourceDescription(SharedLinkingMorphemes.class),
						AsvToolboxSplitterResource.PARAM_PATRICIA_TRIES_RESOURCE,
						createResourceDescription(SharedPatriciaTries.class)));
		AnalysisEngineDescription compound = createEngineDescription(SE_Compound.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger, compoundAnnotator, compound);
		AnalysisEngine engine = createEngine(description);

		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		// 2 compounds, 6 tokens, 2 nouns
		jcas.setDocumentText("Die Regenwettervorhersage verlangt nach Regenschutzkleidung.");
		engine.process(jcas);

		FE_CompoundRatio extractor = new FE_CompoundRatio();
		Set<Feature> features = extractor.extract(jcas);

		Assertions.assertAll(() -> assertEquals(2, features.size()),
				() -> FeatureTestUtil.assertFeatures("avgNumCompoundPerNumToken", 0.3333, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("avgNumCompoundPerNumNoun", 1.0000, features, 0.0001));
	}

}
