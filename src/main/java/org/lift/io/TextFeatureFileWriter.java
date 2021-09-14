package org.lift.io;

import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.api.LiftFeatureExtrationException;

public class TextFeatureFileWriter {

	public static void writeFeatureFile(Map<String, String> idTextMap, String languageCode, String filePath) throws AnalysisEngineProcessException, ResourceInitializationException, FileNotFoundException, LiftFeatureExtrationException {
		List<JCas> casList = preprocessTexts(idTextMap, languageCode);
		CasFeatureFileWriter.writeFeatureFile(filePath, casList);
	}
	
	private static List<JCas> preprocessTexts(Map<String, String> idTextMap, String langaugeCode) throws AnalysisEngineProcessException, ResourceInitializationException {
		List<JCas> casList = new ArrayList<>();
		for (String id : idTextMap.keySet()) {
			JCas cas = TextPreprocessor.preprocess(id, idTextMap.get(id), langaugeCode);
			casList.add(cas);
		}
		
		return casList;
	}
	
}
