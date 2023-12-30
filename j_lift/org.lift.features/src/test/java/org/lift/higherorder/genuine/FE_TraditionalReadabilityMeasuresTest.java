package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.lift.features.util.FeatureTestUtil.assertFeatures;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

import org.apache.commons.io.FileUtils;
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

public class FE_TraditionalReadabilityMeasuresTest {

	@Test
	public void FE_TraditionalReadabilityMeasuresTest() throws IOException, AnalysisEngineProcessException, ResourceInitializationException, LiftFeatureExtrationException {
		
		String testDocument = FileUtils.readFileToString(new File("src/test/resources/txt/test_document_en.txt"));
		
		AnalysisEngineDescription desc = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngine engine = createEngine(desc);

		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText(testDocument);
		engine.process(jcas);
		
		List<ReadabilityConfiguration> config = List.of(ReadabilityConfiguration.LIX, ReadabilityConfiguration.FOG);
		
		FE_TraditionalReadabilityMeasures extractor = new FE_TraditionalReadabilityMeasures(config);
		
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(2, features.size()),
				() -> assertFeatures("READABILITY_MEASURE_LIX", 5.0, features, 0.1),
				() -> assertFeatures("READABILITY_MEASURE_FOG", 10.56, features, 0.1)
				);
	}
	
	@Test
	public void FE_TraditionalReadabilityMeasuresConfigEmptyTest() throws IOException, AnalysisEngineProcessException, ResourceInitializationException, LiftFeatureExtrationException {
		
		String testDocument = FileUtils.readFileToString(new File("src/test/resources/txt/test_document_en.txt"));
		
		AnalysisEngineDescription desc = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngine engine = createEngine(desc);

		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText(testDocument);
		engine.process(jcas);
		
		List<ReadabilityConfiguration> config = new ArrayList<>();
		
		FE_TraditionalReadabilityMeasures extractor = new FE_TraditionalReadabilityMeasures(config);
		
		Set<Feature> features = extractor.extract(jcas);
		
		assertEquals(0, features.size());
	}
	
}
