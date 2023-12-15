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

public class FE_TokensPerSentenceTest {

	@Test
	public void avgNrOfTokenPerSentenceTest() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        FE_TokensPerSentence extractor = new FE_TokensPerSentence();
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));

        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeature("FN_" + extractor.getInternalName(), 5.0, features.iterator().next(), 0.0001)
        );
	}
	
}
