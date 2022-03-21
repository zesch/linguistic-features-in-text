package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class SEL_RutaScriptTest {

	@Test
	public void SELRutaScript_test()
		throws Exception
	{
        String rutaScript = "IMPORT de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token FROM desc.type.LexicalUnits;" +
        		"Token{REGEXP(\",\")";
        String structureName = "comma";
        
		AnalysisEngine engine = createEngine(
				SEL_RutaScript.class,
				SEL_RutaScript.PARAM_RUTA_SCRIPT, rutaScript,
				SEL_RutaScript.PARAM_STRUCTURE_NAME, structureName
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
					() -> Assertions.assertEquals(structureName, s.getName()),
					() -> Assertions.assertEquals(5, s.getBegin()),
					() -> Assertions.assertEquals(6, s.getEnd())
					);
		}
	}
	
}
