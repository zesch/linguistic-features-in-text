package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.higherorder.genuine.FE_FiniteVerbRatio;

public class FE_FiniteVerbRatioTest {
	
	public static final String FN_FINITE_VERB_RATIO = "FiniteVerbRatio";
	
	@Test
	public void finiteVerbRatioTest_de_noTagset() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(MateLemmatizer.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Ich m�chte ein Beispiel testen.");
		engine.process(jcas);
		
		FE_FiniteVerbRatio extractor = new FE_FiniteVerbRatio();
		
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				() -> FeatureTestUtil.assertFeatures(FN_FINITE_VERB_RATIO, 0.666666, features, 0.0001)
				);
		
	}
	
	@Test
	public void finiteVerbRatioTest_en_noTagset() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("I want to test an example.");
		engine.process(jcas);
		
		FE_FiniteVerbRatio extractor = new FE_FiniteVerbRatio();
		
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				() -> FeatureTestUtil.assertFeatures(FN_FINITE_VERB_RATIO, 0.5, features, 0.0001)
				);		
	}	
	
}
