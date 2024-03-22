package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Collection;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.corenlp.CoreNlpLemmatizer;
import org.dkpro.core.corenlp.CoreNlpPosTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.CEFR;

class SE_EVPLevelTest {

	@Test
	void phrasesAnnotatorTest() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription tagger = createEngineDescription(CoreNlpPosTagger.class,
				CoreNlpPosTagger.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription lemmatizer = createEngineDescription(CoreNlpLemmatizer.class);
		AnalysisEngineDescription evpLevel = createEngineDescription(SE_EVPLevel.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, tagger, lemmatizer, evpLevel);
		AnalysisEngine engine = createEngine(description);
		
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test. This kind of test should include a phrase.");
		engine.process(jcas);

		Collection<CEFR> cefrs = JCasUtil.select(jcas, CEFR.class);
		
		Assertions.assertAll(
				// 12 words and 1 phrase
		        () -> assertEquals(13, cefrs.size()),
		        () -> assertEquals("A1", cefrs.iterator().next().getLevel())
		);	
	}

}
