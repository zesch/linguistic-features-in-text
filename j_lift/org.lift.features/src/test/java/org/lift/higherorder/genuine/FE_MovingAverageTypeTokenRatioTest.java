package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;


class FE_MovingAverageTypeTokenRatioTest {

	@Test
	void movingAverageTypeTokenRatioTest() throws Exception{
		
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test and this is an example.");
        engine.process(jcas);
        
        FE_MovingAverageTypeTokenRatio extractor = new FE_MovingAverageTypeTokenRatio();
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        //Note: This test is applied to sliding_size = 6
        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
                () -> FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_MATTR_OF_SLIDING_WINDOW_SIZE_6", 0.08165, features, 0.00001),	
                () -> FeatureTestUtil.assertFeatures("AVERAGE_MATTR_OF_SLIDING_WINDOW_SIZE_6", 0.93333, features, 0.00001)
        		);
        
	}

}
