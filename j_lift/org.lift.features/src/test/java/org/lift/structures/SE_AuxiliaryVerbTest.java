package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Collection;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.Structure;

class SE_AuxiliaryVerbTest {

	@Test
	void auxiliaryVerbTestEnglish() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription auxiliaryVerb = createEngineDescription(SE_AuxiliaryVerb.class,
				SE_AuxiliaryVerb.PARAM_LANGUAGE, "en");
		AnalysisEngineDescription description = createEngineDescription(segmenter, auxiliaryVerb);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("This is a test. We have tested it.");
		engine.process(jcas);
		Collection<Structure> structures = JCasUtil.select(jcas, Structure.class);

		for (Structure s : structures) {
			System.out.println(s);
		}
		Assertions.assertAll(
				// 12 words and 1 phrase
				() -> assertEquals(2, structures.size()),
				() -> assertEquals("AuxiliaryVerb", structures.iterator().next().getName()));
	}

	@Test
	void auxiliaryVerbTestGerman() throws Exception {
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription auxiliaryVerb = createEngineDescription(SE_AuxiliaryVerb.class,
				SE_AuxiliaryVerb.PARAM_LANGUAGE, "de");
		AnalysisEngineDescription description = createEngineDescription(segmenter, auxiliaryVerb);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Das ist ein Test. Wir haben es getestet.");
		engine.process(jcas);
		
		Collection<Structure> structures = JCasUtil.select(jcas, Structure.class);

		Assertions.assertAll(
				// 12 words and 1 phrase
				() -> assertEquals(2, structures.size()),
				() -> assertEquals("AuxiliaryVerb", structures.iterator().next().getName()));
	}

}
