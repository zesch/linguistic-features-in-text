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

public class SEL_Regex extends JCasAnnotator_ImplBase {
	
	private String regexp;
	
	public SEL_Regex(String regexp) {
		this.regexp = regexp;
	}

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {
		String structureName = "REGEXP_" + regexp;
		String rutaScript = 
		"IMPORT org.lift.type.Structure FROM desc.type.LiFT;" +
		"IMPORT de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token FROM desc.type.LexicalUnits;" +
		"Token{REGEXP(\"" + regexp + "\")-> CREATE(Structure, \"name\"=\"" + structureName + "\")};";

		try {
			Pair<AnalysisEngineDescription, TypeSystemDescription> descs = RutaUtil.initRutaFE(rutaScript);
			AnalysisEngine ae = UIMAFramework.produceAnalysisEngine(descs.getKey());

			ae.process(jcas);			
		} catch (InvalidXMLException | ResourceInitializationException | IOException | RecognitionException
				| URISyntaxException e) {
			throw new AnalysisEngineProcessException();
		}
	}

}