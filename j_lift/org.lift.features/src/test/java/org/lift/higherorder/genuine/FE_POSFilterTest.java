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

class FE_POSFilterTest {

	@Test
	void mPosFilterTestEnglish() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a simple example sentence for calculating the pos filter.");
		engine.process(jcas);

		FE_POSFilter extractor = new FE_POSFilter(3, "en");
		Set<Feature> features = extractor.extract(jcas);

		// Note: This test is applied to 3 instances of every POS class
		Assertions.assertAll(() -> assertEquals(72, features.size()),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_3_DTs", 9, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_3_DTs", -1, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_3_NNs", 7.66667, features, 1.0),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_3_NNs", 1.49071, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_3_VBZs", -1, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_3_VBZs", -1, features, 0.00001));
	}

	@Test
	void mPosFilterTestGerman() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "de");
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Dies ist ein einfacher Beispielsatz zur Berechnung des POS-Filters.");
		engine.process(jcas);

		FE_POSFilter extractor = new FE_POSFilter(2, "de");
		Set<Feature> features = extractor.extract(jcas);

		// Note: This test is applied to 2 instances of every POS class
		Assertions.assertAll(() -> assertEquals(102, features.size()),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_2_ARTs", 7, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_2_ARTs", 0.8165, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_2_NNs", 4.57143, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_2_NNs", 1.39971, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("Avg_Window_Size_For_2_VAFINs", -1, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures("StdDev_Window_Size_For_2_VAFINs", -1, features, 0.00001));
	}
}
