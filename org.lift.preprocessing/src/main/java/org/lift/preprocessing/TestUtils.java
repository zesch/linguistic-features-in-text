package org.lift.preprocessing;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;

public class TestUtils {

	public static JCas getJCasForString(String document, PreprocessingConfiguration config) 
			throws ResourceInitializationException, AnalysisEngineProcessException 
	{
		AnalysisEngineDescription desc = config.getUimaEngineDescription();
		
		// TODO creating the engine is expensive, should probably cache in some way
		AnalysisEngine engine = createEngine(desc);

        JCas jcas = engine.newJCas();
        jcas.setDocumentText(document);
        engine.process(jcas);
        
        return jcas;
	}
}
