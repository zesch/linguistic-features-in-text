package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.FEL_GenericStructureCounter;
import org.lift.features.util.FeatureTestUtil;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class SEL_RegexIT {

	@Test
	public void SELRegex_test()
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
        
		SEL_Regex fe = new SEL_Regex(",");
		fe.process(jcas);
		
		String structureName = "REGEXP_,";
		FEL_GenericStructureCounter extractor = new FEL_GenericStructureCounter(structureName);
		Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
		
		Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeatures("org_lift_features_FEL_GenericStructureCounter_REGEXP__", 0.5, features, 0.0001)
        		);
	}
	
}
