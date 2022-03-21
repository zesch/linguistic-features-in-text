package org.lift.features;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SEL_Regex;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FEL_RatioTest {

	@Test
	public void structurePerStructureRatio_test() 
			throws Exception
	{
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
        
		AnalysisEngine fe1 = createEngine(
				SEL_Regex.class,
				SEL_Regex.PARAM_REGEXP, "a");      
		
		AnalysisEngine fe2 = createEngine(
				SEL_Regex.class,
				SEL_Regex.PARAM_REGEXP, "b"); 
		
		fe1.process(jcas);
        fe2.process(jcas);
        
		FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(
				Structure.class.getName(), "a",
				Structure.class.getName(), "b"
			);
		Set<Feature> features = extractor.extract(jcas);
		
		Assertions.assertAll(
				() -> assertEquals(1, features.size()),
				() -> FeatureTestUtil.assertFeature("FN_" + extractor.getInternalName(), 1, features.iterator().next(), 0.0001)
		);
	}
	
	@Test
	public void annotationPerAnnotationRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(
        		Token.class.getName(),
        		Sentence.class.getName()
        );
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeature("FN_" + extractor.getInternalName(), 5.0, features.iterator().next(), 0.0001)
        );
	}
	
	@Test
	public void annotationPerStructureRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);
        
		AnalysisEngine regexp = createEngine(
				SEL_Regex.class,
				SEL_Regex.PARAM_REGEXP, "a"
		);
        regexp.process(jcas);
        
        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(
        		Token.class.getName(), null,
        		Structure.class.getName(), "a");
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeature("FN_" + extractor.getInternalName(), 5.0, features.iterator().next(), 0.0001)
        );
	}
	
	@Test
	public void structurePerAnnotationRatio_test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);
        
		AnalysisEngine regexp = createEngine(
				SEL_Regex.class,
				SEL_Regex.PARAM_REGEXP, "a");
        regexp.process(jcas);
        
        FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(
        		Structure.class.getName(), "a",
        		Token.class.getName(), null
        );
        Set<Feature> features = extractor.extract(jcas);
        
        Assertions.assertAll(
        		() -> assertEquals(1, features.size()),
        		() -> FeatureTestUtil.assertFeature("FN_" + extractor.getInternalName(), 0.2, features.iterator().next(), 0.0001)
        );
	}
	
}
