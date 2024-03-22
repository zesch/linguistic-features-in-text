package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SE_AuxiliaryVerb;

class FE_AvgNrOfAuxiliaryVerbTest {

	@Test
	void avgNrOfAuxiliaryVerbTestEnglish() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription auxiliaryVerb = createEngineDescription(SE_AuxiliaryVerb.class,
				SE_AuxiliaryVerb.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription description = createEngineDescription(segmenter, auxiliaryVerb);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		
		// 10 tokens
		jcas.setDocumentText("This is a test. We have tested it.");
		engine.process(jcas);
		
		FE_AvgNrOfAuxiliaryVerb extractor = new FE_AvgNrOfAuxiliaryVerb();
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				// "is", "have" are auxiliary verbs -> 2/10
				() -> FeatureTestUtil.assertFeatures("FN_"+extractor.getInternalName(), 0.2, features, 0.0001));
	}
	@Test
	void avgNrOfAuxiliaryVerbTestGerman() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription auxiliaryVerb = createEngineDescription(SE_AuxiliaryVerb.class,
				SE_AuxiliaryVerb.PARAM_LANGUAGE, "de");
		AnalysisEngineDescription description = createEngineDescription(segmenter, auxiliaryVerb);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		
		// 10 tokens
		jcas.setDocumentText("Das ist ein Test. Wir haben es getestet.");
		engine.process(jcas);
		
		FE_AvgNrOfAuxiliaryVerb extractor = new FE_AvgNrOfAuxiliaryVerb();
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				// "ist", "haben" are auxiliary verbs -> 2/10
				() -> FeatureTestUtil.assertFeatures("FN_"+extractor.getInternalName(), 0.2, features, 0.0001));
	}

}
