package org.lift.higherorder.convenience;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

public class FE_AvgNrOfNounPhrasePerSentenceTest {

	@Test
	public void avgNrOfNounPhrasePerSentenceTest() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test in a sentence. This is a test in a sentence.");
        engine.process(jcas);
        
        FE_AvgNrOfNounPhrasesPerSentence extractor = new FE_AvgNrOfNounPhrasesPerSentence();
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        String baseString = "NC_PER_SENTENCE";
        
        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
                () -> FeatureTestUtil.assertFeatures("FN_" + baseString, 3.0, features, 0.0001),
                () -> FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001)
        		);     
	}
	
}
