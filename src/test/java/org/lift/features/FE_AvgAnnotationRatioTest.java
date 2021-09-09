package org.lift.features;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.Assert.assertEquals;

import java.util.HashSet;
import java.util.Set;

import org.junit.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_NOUN;
import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS_VERB;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.PC;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.VC;



public class FE_AvgAnnotationRatioTest {
	
	@Test
	public void avgAnnotationRatioFE_tokenPerSentence_Test() throws Exception {
		AnalysisEngine engine = createEngine(BreakIteratorSegmenter.class);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test. This is a test.");
        engine.process(jcas);

        String dividendFeaturePath = Token.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));

        String baseString = "TOKEN_PER_SENTENCE";
        assertEquals(2, features.size());
        FeatureTestUtil.assertFeatures("FN_" + baseString, 5.0, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_nounPhrasePerSentence_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test in a sentence. This is a test in a sentence.");
        engine.process(jcas);
        
        String dividendFeaturePath = NC.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "NC_PER_SENTENCE";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 3.0, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_verbPhrasePerSentence_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test in a sentence. This is a test in a sentence.");
        engine.process(jcas);
        
        String dividendFeaturePath = VC.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "VC_PER_SENTENCE";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 1.0, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_PrepositionalPhrasePerSentence_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test in a sentence. This is a test in a sentence.");
        engine.process(jcas);
        
        String dividendFeaturePath = PC.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "PC_PER_SENTENCE";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 1.0, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_NounPOSPerToken_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test and this a nice example.");
        engine.process(jcas);
        
        String dividendFeaturePath = POS_NOUN.class.getName();
        String divisorFeaturePath = Token.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "POS_NOUN_PER_TOKEN";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 0.2, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.4, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_VerbPOSPerToken_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test and this a nice example.");
        engine.process(jcas);
        
        String dividendFeaturePath = POS_VERB.class.getName();
        String divisorFeaturePath = Token.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "POS_VERB_PER_TOKEN";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 0.1, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.3, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_VerbPOSPerSentence_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test and this a nice example.");
        engine.process(jcas);
        
        String dividendFeaturePath = POS_VERB.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "POS_VERB_PER_SENTENCE";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 1, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}
	
	@Test
	public void avgAnnotationRatioFe_NounPOSPerSentence_Test() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(NoOpAnnotator.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger, lemmatizer);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("en");
        jcas.setDocumentText("This is a test and this a nice example.");
        engine.process(jcas);
        
        String dividendFeaturePath = POS_NOUN.class.getName();
        String divisorFeaturePath = Sentence.class.getName();
        FE_AvgAnnotationRatio extractor = new FE_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
        Set<Feature> features = new HashSet<Feature>(extractor.extract(jcas));
        
        assertEquals(2, features.size());
        String baseString = "POS_NOUN_PER_SENTENCE";
        FeatureTestUtil.assertFeatures("FN_" + baseString, 2, features, 0.0001);
        FeatureTestUtil.assertFeatures("STANDARD_DEVIATION_OF_" + baseString, 0.0, features, 0.0001);
	}

}
