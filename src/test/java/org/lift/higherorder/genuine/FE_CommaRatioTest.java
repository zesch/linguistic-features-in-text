package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.higherorder.genuine.FE_CommaRatio;
import org.lift.higherorder.genuine.FE_CommaRatioAlternative;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_CommaRatioTest {

	@Test
	public void nrOfCommasTest()
		throws Exception
	{
		
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
		FE_CommaRatio fe = new FE_CommaRatio();
		Set<Feature> features = fe.extract(jcas);
		
		Assertions.assertAll(
		        () -> assertEquals(1, features.size()),
		        () -> FeatureTestUtil.assertFeature(fe.getInternalName(), 0.5, features.iterator().next(), 0.00001)
				);
	}
	
	@Test
	public void nrOfCommasAlternativeTest() throws Exception {
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
        FE_CommaRatioAlternative fe = new FE_CommaRatioAlternative();
		Set<Feature> features = fe.extract(jcas);

		Assertions.assertAll(
				() -> assertEquals(2, features.size()),
		        () -> FeatureTestUtil.assertFeatures("NORMALIZED_" + fe.getInternalName(), 0.5, features, 0.00001),
		        () -> FeatureTestUtil.assertFeatures("FN_NR_OF_" + fe.getInternalName(), 1, features)
				);
	}
	
}
