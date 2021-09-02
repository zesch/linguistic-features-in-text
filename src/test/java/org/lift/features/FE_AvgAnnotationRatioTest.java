package org.lift.features;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.Assert.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.junit.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;



public class FE_AvgAnnotationRatioTest {
	
	@Test
	public void AvgAnnotationRatioFE_Test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        String dividendFeaturePath = Token.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));

        String baseString = "TOKEN_PER_SENTENCE";
        assertEquals(2, features.size());
        FeatureTestUtil.assertFeatures("FN_" + baseString, 5.0, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}

}
