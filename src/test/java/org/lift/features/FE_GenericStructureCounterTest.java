package org.lift.features;

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
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_GenericStructureCounterTest {

	@Test
	public void countFE_test()
		throws Exception
	{
		
		String structureName = "comma";
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
        Structure s1 = new Structure(jcas, t2.getBegin(), t2.getEnd());
        s1.setName(structureName);
        s1.addToIndexes();
        
		FE_GenericStructureCounter fe = new FE_GenericStructureCounter(structureName);
		
		Set<Feature> features = fe.extract(jcas);
		
		Assertions.assertAll(
		        () -> assertEquals(1, features.size()),
		        () -> FeatureTestUtil.assertFeatures(fe.getInternalName(), 0.5, features, 0.00001)
				);

        System.out.println(features);
	}
}
