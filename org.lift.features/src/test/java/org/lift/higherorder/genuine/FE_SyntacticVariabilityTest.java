package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.opennlp.OpenNlpChunker;
import org.dkpro.core.opennlp.OpenNlpPosTagger;
import org.dkpro.core.stanfordnlp.StanfordParser;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;

public class FE_SyntacticVariabilityTest {

	@Test 
	public void SyntacticVariablityTest_en() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
		AnalysisEngineDescription chunker = createEngineDescription(OpenNlpChunker.class);
		AnalysisEngineDescription constituentParser = createEngineDescription(StanfordParser.class, 
				StanfordParser.PARAM_LANGUAGE, "en",
				StanfordParser.PARAM_WRITE_PENN_TREE, true,
				StanfordParser.PARAM_WRITE_POS, false,
				StanfordParser.PARAM_PRINT_TAGSET,false,
				StanfordParser.PARAM_VARIANT, "pcfg");
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,chunker,lemmatizer,constituentParser);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test. This is a great testing. "
				+ "This is a test which has a lot to show.");
		engine.process(jcas);

		FE_SyntacticVariability extractor = new FE_SyntacticVariability();
        Set<Feature> features = extractor.extract(jcas);

        Assertions.assertAll(
        		() -> assertEquals(6, features.size()),
        		// 2 types of sentences (phraseLevel) in 3 sentences = 0.6666666666666666
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_PHRASELEVEL, 0.6666666666666666, features, 0.0001),	
        		// 3 types of sentences (POS) in 3 sentences = 1.0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_POSLEVEL, 1.0, features, 0.0001),
        		// 2 types of sentences (POS) in 3 sentences = 0.66666666666666
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_SENTENCELEVEL, 0.6666666666666666, features, 0.0001),
        		// 1 similar pair/ 2 pairs = 0.5 
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_PHRASELEVEL, 0.5, features, 0.0001),
        		// 0 similar pair/ 2 pairs = 0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_POSLEVEL, 0.0, features, 0.0001),
        		// 1 similar pair/ 2 pairs = 0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_SENTENCELEVEL, 0.5, features, 0.0001)
        		);
	}	
	
	@Test
	public void SyntacticVariablityTest_de() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription posTagger = createEngineDescription(OpenNlpPosTagger.class);
		AnalysisEngineDescription lemmatizer = createEngineDescription(MateLemmatizer.class);
		AnalysisEngineDescription constituentParser = createEngineDescription(StanfordParser.class, 
				StanfordParser.PARAM_LANGUAGE, "de",
				StanfordParser.PARAM_WRITE_PENN_TREE, true,
				StanfordParser.PARAM_WRITE_POS, false,
				StanfordParser.PARAM_PRINT_TAGSET,false,
				StanfordParser.PARAM_VARIANT, "pcfg");
		AnalysisEngineDescription description = createEngineDescription(segmenter,posTagger,lemmatizer,constituentParser);
		AnalysisEngine engine = createEngine(description);

        JCas jcas = engine.newJCas();
        jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Das ist ein Test. Das ist eine tolle Testung. Das ist ein Test, der viel zu zeigen hat.");
		engine.process(jcas);

		FE_SyntacticVariability extractor = new FE_SyntacticVariability();
        Set<Feature> features = extractor.extract(jcas);

        Assertions.assertAll(
        		() -> assertEquals(6, features.size()),
        		// 2 types of sentences (phraseLevel) in 3 sentences = 0.6666666666666666
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_PHRASELEVEL, 0.6666666666666666, features, 0.0001),	
        		// 3 types of sentences (POS) in 3 sentences = 1.0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_POSLEVEL, 1.0, features, 0.0001),
        		// 2 types of sentences (POS) in 3 sentences = 0.66666666666666
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.SYNTAX_TYPE_RATIO_SENTENCELEVEL, 0.6666666666666666, features, 0.0001),
        		// 1 similar pair/ 2 pairs = 0.5 
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_PHRASELEVEL, 0.5, features, 0.0001),
        		// 0 similar pair/ 2 pairs = 0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_POSLEVEL, 0.0, features, 0.0001),
        		// 1 similar pair/ 2 pairs = 0
        		() -> FeatureTestUtil.assertFeatures(FE_SyntacticVariability.PAIRWISE_SYNTACTIC_SIMILARITY_SENTENCELEVEL, 0.5, features, 0.0001)
        		);
	}
	
}
