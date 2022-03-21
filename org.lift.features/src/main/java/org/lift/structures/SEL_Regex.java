package org.lift.structures;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.jcas.JCas;

public class SEL_Regex 
	extends SEL_Ruta
{
	
	public static final String PARAM_REGEXP = "regexp";
	@ConfigurationParameter(name = PARAM_REGEXP, mandatory = true)
	private String regexp;
	
	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		
		String rutaScript = 
				"IMPORT org.lift.type.Structure FROM desc.type.LiFT;\n" +
				"IMPORT de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token FROM desc.type.LexicalUnits;\n" +
				"Token{REGEXP(\"" + regexp + "\")" +
				"-> CREATE(Structure, \"name\"=\"" + getPublicStructureName() + "\")};";
		
		getRutaEngine(rutaScript).process(jcas);			
	}

	@Override
	public String getPublicStructureName() {
		// TODO using the regexp as part of the name is a very bad idea
		return "RegExp_" + regexp;
	}


}