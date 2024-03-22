package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SE_EVPLevel;

class FE_EVPLevelRatioTest {

	@Test
	void evpLevelRatioTest() throws Exception {

		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
		AnalysisEngineDescription evpLevel = createEngineDescription(SE_EVPLevel.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger, lemmatizer, evpLevel);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		// 14 tokens
		jcas.setDocumentText("This is a test. This kind of test should include a phrase.");
		engine.process(jcas);

		FE_EVPLevelRatio extractor = new FE_EVPLevelRatio();
		Set<Feature> features = extractor.extract(jcas);

		Assertions.assertAll(
				() -> assertEquals(12, features.size()),
				// "This, is, a, test, This, test, a" -> level A1 = 7/14
				() -> FeatureTestUtil.assertFeatures("A1Ratio", 0.5, features, 0.0001),
				// "should, include" -> level A2 = 2/14
				() -> FeatureTestUtil.assertFeatures("A2Ratio", 0.1428, features, 0.0001),
				// phrase -> level B1 = 1/14
				() -> FeatureTestUtil.assertFeatures("B1Ratio", 0.0714, features, 0.0001),
				// "kind", "of" belongs to "kind of" phrase has level B2 = 2/14
				() -> FeatureTestUtil.assertFeatures("B2Ratio", 0.1428, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("C1Ratio", 0, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("C2Ratio", 0, features, 0.0001),

				// "kind of" phrase -> B2 = 1/14
				() -> FeatureTestUtil.assertFeatures("B2PhraseRatio", 0.0714, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("A2PhraseRatio", 0, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("A1PhraseRatio", 0, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("B1PhraseRatio", 0, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("C1PhraseRatio", 0, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures("C2PhraseRatio", 0, features, 0.0001));

	}

}
