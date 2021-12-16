package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
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
		
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
		SEL_Regex fe = new SEL_Regex(",");
		fe.process(jcas);
		
		String expectedStructureName = "REGEXP_,";
		int expectedStructureBegin = 5;
		int expectedStructureEnd = 6;
		
		for (Structure s : JCasUtil.select(jcas, Structure.class)) {
			Assertions.assertAll("Assert annotated Structure is as expected",
					() -> Assertions.assertEquals(expectedStructureName, s.getName()),
					() -> Assertions.assertEquals(expectedStructureBegin, s.getBegin()),
					() -> Assertions.assertEquals(expectedStructureEnd, s.getEnd())
					);
		}
	}
	
}
