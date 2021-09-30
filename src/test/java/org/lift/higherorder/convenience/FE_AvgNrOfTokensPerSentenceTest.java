package org.lift.higherorder.convenience;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

public class FE_AvgNrOfTokensPerSentenceTest {

	@Test
	public void avgNrOfTokenPerSentenceTest() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        FE_AvgNrOfTokensPerSentence extractor = new FE_AvgNrOfTokensPerSentence();
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));

        String baseString = "TOKEN_PER_SENTENCE";
        
        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
        		() -> FeatureTestUtil.assertFeatures("FN_" + baseString, 5.0, features, 0.0001),
        		() -> FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001)
        		);
	}
	
}
