package org.lift.structures;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.jcas.JCas;

public class SEL_RutaScript 
	extends SEL_Ruta 
{
	public static final String PARAM_RUTA_SCRIPT = "rutaScript";
	@ConfigurationParameter(name = PARAM_RUTA_SCRIPT, mandatory = false)
	protected String rutaScript;

	public static final String PARAM_STRUCTURE_NAME = "structureName";
	@ConfigurationParameter(name = PARAM_STRUCTURE_NAME, mandatory = false)
	protected String structureName;	
	
	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		String script = 
		"IMPORT org.lift.type.Structure FROM desc.type.LiFT;\n"
		+ rutaScript
		+ "-> CREATE(Structure, \"name\"=\"" + structureName + "\")};";

		getRutaEngine(script).process(jcas);	
	}

	@Override
	public String getPublicStructureName() {
		return structureName;
	}
}
