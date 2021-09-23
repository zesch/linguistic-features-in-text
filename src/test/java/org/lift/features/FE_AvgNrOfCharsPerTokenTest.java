package org.lift.features;


import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.higherorder.FE_AvgNrOfCharsPerToken;

public class FE_AvgNrOfCharsPerTokenTest {

	@Test
	public void tokenLengthFeatureExtractorTest()
			throws Exception
	{
		AnalysisEngineDescription description= createEngineDescription(createEngineDescription(BreakIteratorSegmenter.class), createEngineDescription(OpenNlpPosTagger.class));
		AnalysisEngine engine = createEngine(description);

		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Sie ist gut.");
		engine.process(jcas);

		FE_AvgNrOfCharsPerToken extractor = new FE_AvgNrOfCharsPerToken();
		Set<Feature> features = extractor.extract(jcas);

		Assertions.assertAll(
				() -> assertEquals(2, features.size()),
				() -> FeatureTestUtil.assertFeatures(FE_AvgNrOfCharsPerToken.STANDARD_DEVIATION_OF_CHARS_PER_TOKEN, 0.0, features, 0.00001),
				() -> FeatureTestUtil.assertFeatures(FE_AvgNrOfCharsPerToken.AVG_NR_OF_CHARS_PER_TOKEN, 3.0, features, 0.00001)
				);
	}
	
}
