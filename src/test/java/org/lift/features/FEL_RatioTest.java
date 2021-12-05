package org.lift.features;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SEL_Regex;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FEL_RatioTest {

	@Test
	public void structurePerStructureRatio_test() throws ResourceInitializationException, AnalysisEngineProcessException, LiftFeatureExtrationException {
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
        
        AnnotationExtractionInformation dividendFeature = new AnnotationExtractionInformation(Structure.class.getName() + "/name", dividendStructureName);
        AnnotationExtractionInformation divisorFeature = new AnnotationExtractionInformation(Structure.class.getName() + "/name", divisorStructureName);
		FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeature, divisorFeature);
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				() -> FeatureTestUtil.assertFeatures("FN_" + extractor.buildBaseFeatureString(dividendFeature, divisorFeature), 1, features, 0.0001)
				);
	}
	
	@Test
	public void annotationPerAnnotationRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        AnnotationExtractionInformation dividendFeature = new AnnotationExtractionInformation(Token.class.getName());
        AnnotationExtractionInformation divisorFeature = new AnnotationExtractionInformation(Sentence.class.getName());
        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeature, divisorFeature);
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeatures("FN_" + extractor.buildBaseFeatureString(dividendFeature, divisorFeature), 5.0, features, 0.0001)
        		);
	}
	
	@Test
	public void annotationPerStructureRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);
        
        SEL_Regex fe1 = new SEL_Regex("a");
        fe1.process(jcas);
        
        String divisorStructureName = "REGEXP_a";

        AnnotationExtractionInformation dividendFeature = new AnnotationExtractionInformation(Token.class.getName());
        AnnotationExtractionInformation divisorFeature = new AnnotationExtractionInformation(Structure.class.getName() + "/name", divisorStructureName);
        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeature, divisorFeature);
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeatures("FN_" + extractor.buildBaseFeatureString(dividendFeature, divisorFeature), 5.0, features, 0.0001)
        		);
	}
	
	@Test
	public void structurePerAnnotationRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);
        
        SEL_Regex fe1 = new SEL_Regex("a");
        fe1.process(jcas);
        
        String divisorStructureName = "REGEXP_a";

        AnnotationExtractionInformation divisorFeature = new AnnotationExtractionInformation(Token.class.getName());
        AnnotationExtractionInformation dividendFeature = new AnnotationExtractionInformation(Structure.class.getName() + "/name", divisorStructureName);
        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeature, divisorFeature);
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeatures("FN_" + extractor.buildBaseFeatureString(dividendFeature, divisorFeature), 0.2, features, 0.0001)
        		);
	}
	
}
