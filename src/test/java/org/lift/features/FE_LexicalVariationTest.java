package org.lift.features;

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

public class FE_LexicalVariationTest {

	@Test
	public void lexicalVariationTest_de() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(MateLemmatizer.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Das ist ein Test und das ist ein Beispiel.");
		engine.process(jcas);
		
		FE_LexicalVariation extractor = new FE_LexicalVariation();
		
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(2, features.size()),
				() -> FeatureTestUtil.assertFeatures(FE_LexicalVariation.FN_LEXICAL_VARIATION, 0.75, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures(FE_LexicalVariation.FN_VERB_VARIATION, 0.5, features, 0.0001)	
				);
	}
	
	@Test
	public void lexicalVariationTest_en() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test and this is an example.");
		engine.process(jcas);
		
		FE_LexicalVariation extractor = new FE_LexicalVariation();
		
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(2, features.size()),
				() -> FeatureTestUtil.assertFeatures(FE_LexicalVariation.FN_LEXICAL_VARIATION, 0.75, features, 0.0001),
				() -> FeatureTestUtil.assertFeatures(FE_LexicalVariation.FN_VERB_VARIATION, 0.5, features, 0.0001)
				);	
	}	
	
}
