package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;

public class FE_TrigramCounterTest {
	
	@Test
	public void testTrigramProbabilty() throws ResourceInitializationException, AnalysisEngineProcessException, LiftFeatureExtrationException {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test and this is an example.");
		engine.process(jcas);
		
		String filePath = "/web1t/en/data";
		
		FE_TrigramCounter extractor = new FE_TrigramCounter(filePath);
		Set<Feature> features = extractor.extract(jcas);
		
		for (Feature feature : features) {
			System.out.println(feature.getName() + ": " + feature.getValue());
		}
		
		Assertions.assertEquals(3, features.size());
	}

}
