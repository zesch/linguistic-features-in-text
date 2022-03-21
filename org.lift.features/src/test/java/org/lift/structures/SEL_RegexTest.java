package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class SEL_RegexTest {

	@Test
	public void SELRegex_test()
		throws Exception
	{
		
		AnalysisEngine engine = createEngine(
				SEL_Regex.class,
				SEL_Regex.PARAM_REGEXP, ","
		);
		
        JCas jcas = engine.newJCas();
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
		engine.process(jcas);
		
		for (Structure s : JCasUtil.select(jcas, Structure.class)) {
			Assertions.assertAll("Assert annotated Structure is as expected",
					() -> Assertions.assertEquals("RegExp_,", s.getName()),
					() -> Assertions.assertEquals(5, s.getBegin()),
					() -> Assertions.assertEquals(6, s.getEnd())
			);
		}
	}
	
}
