package org.lift.structures;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Collection;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.CEFR;
import org.lift.features.util.TestBase;
import org.lift.features.util.TestBase.ParserType;

public class SE_FrequencyEVPTest {
	
	@Test
	public void test_SE_FrequencyEVP() throws Exception {
		
		AnalysisEngine engine = TestBase.getPreprocessingEngine("en",ParserType.noParser);
		JCas jcas = engine.newJCas();		
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("The test is ongoing");
		engine.process(jcas);
		
		SE_FrequencyEVP se = new SE_FrequencyEVP();
		se.initialize(null);
		se.process(jcas);
		
		for(CEFR s : JCasUtil.select(jcas, CEFR.class)) {
			System.out.println(s.toString());
		}
		Collection<CEFR> frequencies = JCasUtil.select(jcas, CEFR.class);
		Assertions.assertAll(
		        () -> assertEquals(4, frequencies.size()),
		        () -> assertEquals("A1", frequencies.iterator().next().getLevel())
				);
		
	}

}
