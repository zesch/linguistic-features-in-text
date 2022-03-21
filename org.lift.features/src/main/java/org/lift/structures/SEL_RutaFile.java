package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

import org.apache.commons.io.FileUtils;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.jcas.JCas;

public class SEL_RutaFile 
	extends SEL_Ruta
{

	public static final String PARAM_RUTA_FILE = "rutaFile";
	@ConfigurationParameter(name = PARAM_RUTA_FILE, mandatory = true)
	private String filePath;

	// TODO cannot set structure name, as it is defined in rutafile, somewhat breakt the whole concept here
//	public static final String PARAM_STRUCTURE_NAME = "structureName";
//	@ConfigurationParameter(name = PARAM_STRUCTURE_NAME, mandatory = true)
//	private String structureName;	

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		String rutaScript;
		try {
			rutaScript = FileUtils.readFileToString(new File(filePath), StandardCharsets.UTF_8);
		} catch (IOException e) {
			throw new AnalysisEngineProcessException(e);
		}
		getRutaEngine(rutaScript).process(jcas);			
	}

	@Override
	public String getPublicStructureName() {
		return null;
	}
	

}
