package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

class FE_MATTRCoarseGrainedPosClassesTest {

	@Test
	void mATTRCoaseGrainedPOSTest() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test and this is an example.");
		engine.process(jcas);

		FE_MATTRCoarseGrainedPosClasses extractor = new FE_MATTRCoarseGrainedPosClasses(6);
		Set<Feature> features = extractor.extract(jcas);

		// Note: This test is applied to window size = 6
		Assertions.assertAll(() -> assertEquals(24, features.size()),
				() -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_DET_WindowSize_6", 0.93333, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_DET_WindowSize_6", 0.13333, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_NOUN_WindowSize_6", 1.0, features, 1.0),
				() -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_NOUN_WindowSize_6", 0.0, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_VERB_WindowSize_6", 0.9, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_VERB_WindowSize_6", 0.2, features, 0.00001));
	}
}
