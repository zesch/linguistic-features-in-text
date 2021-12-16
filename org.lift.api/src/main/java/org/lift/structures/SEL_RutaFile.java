package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

import org.apache.commons.io.FileUtils;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.jcas.JCas;

public class SEL_RutaFile extends JCasAnnotator_ImplBase {

	private String filePath;
	private String structureName;
	
	public SEL_RutaFile(String filePath, String structureName) {
		this.filePath = filePath;
		this.structureName = structureName;
	}
	
	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		String rutaScript;
		
		try {
			rutaScript = FileUtils.readFileToString(new File(filePath), StandardCharsets.UTF_8);
		} catch (IOException e) {
			throw new AnalysisEngineProcessException(e);
		}
		
		SEL_RutaScript fe = new SEL_RutaScript(rutaScript, structureName);
		fe.process(jcas);
	}

}
