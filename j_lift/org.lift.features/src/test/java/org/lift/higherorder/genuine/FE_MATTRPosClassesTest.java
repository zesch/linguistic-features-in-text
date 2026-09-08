package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

class FE_MATTRPosClassesTest {

	@Test
	void mATTRPosClassesTestEnglish() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "en");	
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test and this is an example.");
		engine.process(jcas);
		
		FE_MATTRPosClasses extractor = new FE_MATTRPosClasses(6,"en");
		Set<Feature> features = extractor.extract(jcas);
		
		//Note: This test is applied to sliding_size = 6
        Assertions.assertAll(
        		() -> assertEquals(72, features.size()),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_DT_WindowSize_6", 0.93333, features, 0.00001),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_DT_WindowSize_6", 0.13333, features, 0.00001),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_NN_WindowSize_6", 1.0, features, 1.0),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_NN_WindowSize_6", 0.0, features, 0.00001),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_VBZ_WindowSize_6", 0.9, features, 0.00001),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_VBZ_WindowSize_6", 0.2, features, 0.00001)      
        		);
	}
	
	@Test
	void mATTRPosClassesTestGerman() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "de");	
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Das ist ein Test. Wir haben es getestet.");
		engine.process(jcas);
		
		FE_MATTRPosClasses extractor = new FE_MATTRPosClasses(6,"de");
		Set<Feature> features = extractor.extract(jcas);
		
		//Note: This test is applied to window size = 6
        Assertions.assertAll(
        		() -> assertEquals(102, features.size()),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_PDS_WindowSize_6", 1, features, 0.00001),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_PDS_WindowSize_6", -1, features, 0.00001),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_NN_WindowSize_6", 1.0, features, 1.0),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_NN_WindowSize_6", 0.0, features, 0.00001),
                () -> FeatureTestUtil.assertFeatures("Avg_MATTR_Of_VAFIN_WindowSize_6", 1.0, features, 0.00001),	
                () -> FeatureTestUtil.assertFeatures("StdDev_MATTR_Of_VAFIN_WindowSize_6", 0.0, features, 0.00001)      
        		);
	}

}
