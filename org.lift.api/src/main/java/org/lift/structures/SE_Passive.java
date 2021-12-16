package org.lift.structures;

import java.io.IOException;
import java.net.URISyntaxException;

import org.antlr.runtime.RecognitionException;
import org.apache.commons.lang3.tuple.Pair;
import org.apache.uima.UIMAFramework;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.apache.uima.resource.metadata.TypeSystemDescription;
import org.apache.uima.util.InvalidXMLException;
import org.lift.structures.ruta.RutaUtil;

public class SE_Passive 
	extends JCasAnnotator_ImplBase
{

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		
		
		
	}
}