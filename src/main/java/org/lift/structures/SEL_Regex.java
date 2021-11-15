package org.lift.structures;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.jcas.JCas;

public class SEL_Regex extends JCasAnnotator_ImplBase {
	
	private String regexp;
	
	public SEL_Regex(String regexp) {
		this.regexp = regexp;
	}

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		String rutaScript = "IMPORT de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token FROM desc.type.LexicalUnits;"
				+ "Token{REGEXP(\"" + regexp + "\")";
		String structureName = "REGEXP_" + regexp;

		SEL_RutaScript fe = new SEL_RutaScript(rutaScript, structureName);
		fe.process(jcas);
	}

}
