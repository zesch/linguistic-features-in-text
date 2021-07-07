package org.lift.structures.ruta;

import org.apache.commons.lang3.tuple.Pair;
import org.apache.uima.UIMAFramework;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.cas.CAS;
import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.fit.util.CasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.metadata.TypeSystemDescription;

public class RutaExample {

	public static void main(String[] args) 
			throws Exception
	{
		String rutaScript = "DECLARE MyType; W{-> MyType};";

		Pair<AnalysisEngineDescription, TypeSystemDescription> descs = RutaUtil.initRutaFE(rutaScript);
				
		AnalysisEngine ae = UIMAFramework.produceAnalysisEngine(descs.getKey());
		JCas jCas = JCasFactory.createJCas(descs.getValue());
		jCas.setDocumentText("This is my document.");
		ae.process(jCas);
		
		CAS cas = jCas.getCas();
		for (AnnotationFS each : CasUtil.select(cas, cas.getTypeSystem().getType("Anonymous.MyType"))) {
			System.out.println(each.getCoveredText());
		}
	}
}
