package org.lift.features;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.Assert.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.junit.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_GenericCounterTest {

	@Test
	public void countFE_test()
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
        
		FE_GenericCounter fe = new FE_GenericCounter(
				Token.class.getName(),
				f  -> f.equals(",")
		);
		
		Set<Feature> features = fe.extract(jcas);
        assertEquals(1, features.size());
        FeatureTestUtil.assertFeatures(fe.getInternalName(), 0.5, features, 0.00001);
        System.out.println(features);
	}
}
