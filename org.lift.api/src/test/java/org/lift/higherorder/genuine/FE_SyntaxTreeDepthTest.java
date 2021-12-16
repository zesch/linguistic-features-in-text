package org.lift.higherorder.genuine;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;

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

public class FE_SyntaxTreeDepthTest {

	@Test
	public void syntaxTreeDepthFeatureExtractorTest_DE()
	        throws Exception
	  {
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
        jcas.setDocumentText("Dies ist ein Satz, der immer verschachltelt und lanweilig zu lesen. Er ist dafür kurz."
        		);
        engine.process(jcas);

        FE_SyntaxTreeDepth extractor = new FE_SyntaxTreeDepth("de");
        Set<Feature> features = extractor.extract(jcas);

        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.AVG_SYNTAX_TREE_DEPTH, 3.5, features, 0.0001),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.TOTAL_SYNTAX_TREE_DEPTH, 7.0, features, 0.0001)
        		);
    }
	
	@Test
	public void syntaxTreeDepthFeatureExtractorTest_EN()
	        throws Exception
	    {
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
	        jcas.setDocumentText("This is a sentence that is nested and boring to read. But it is short.");
	        engine.process(jcas);

	        FE_SyntaxTreeDepth extractor = new FE_SyntaxTreeDepth("en");
	        Set<Feature> features = extractor.extract(jcas);

	        Assertions.assertAll(
	        		() -> assertEquals(2, features.size()),
	        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.AVG_SYNTAX_TREE_DEPTH, 6.0, features, 0.0001),
	        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.TOTAL_SYNTAX_TREE_DEPTH, 12.0, features, 0.0001)
	        		);
	    }
	
}
