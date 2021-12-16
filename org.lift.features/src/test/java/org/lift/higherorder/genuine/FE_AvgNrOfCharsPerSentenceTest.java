package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.util.FeatureTestUtil;
import org.lift.higherorder.genuine.FE_AvgNrOfCharsPerSentence;

public class FE_AvgNrOfCharsPerSentenceTest {

	@Test
	public void avgNrOfCharsPerSentenceFeatureExtractorTest() throws ResourceInitializationException, AnalysisEngineProcessException, LiftFeatureExtrationException {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);

        JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);
        

        FE_AvgNrOfCharsPerSentence extractor = new FE_AvgNrOfCharsPerSentence();
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));

        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
                () -> FeatureTestUtil.assertFeatures(FE_AvgNrOfCharsPerSentence.AVG_NR_OF_CHARS_SENTENCE, 15.0, features, 0.00001),
                () -> FeatureTestUtil.assertFeatures(FE_AvgNrOfCharsPerSentence.STANDARD_DEVIATION_OF_CHARS_PER_SENTENCE, 0, features, 0.00001)		
        		);
	}
	
}
