package org.lift.features;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SEL_Regex;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FEL_AvgStructureRatioTest {

	@Test
	public void avgStructureRation_test() throws ResourceInitializationException, AnalysisEngineProcessException, LiftFeatureExtrationException {
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test a b");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
        Token t3 = new Token(jcas, 7, 8);
        t3.addToIndexes();
        
        SEL_Regex fe1 = new SEL_Regex("a");
        SEL_Regex fe2 = new SEL_Regex("b");
        fe1.process(jcas);
        fe2.process(jcas);
        String dividendStructureName = "REGEXP_a";
        String divisorStructureName = "REGEXP_b";
        
		FEL_AvgStructureRatio extractor = new FEL_AvgStructureRatio(dividendStructureName, divisorStructureName);
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				() -> FeatureTestUtil.assertFeatures("FN_" + dividendStructureName + "_PER_" + divisorStructureName, 1, features, 0.0001)
				);
	}
}
