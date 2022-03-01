package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.dkpro.core.api.featurepath.FeaturePathFactory.select;

import java.util.Map.Entry;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.collection.CollectionReaderDescription;
import org.apache.uima.fit.factory.CollectionReaderFactory;
import org.apache.uima.fit.pipeline.JCasIterable;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.io.xmi.XmiReader;
import org.junit.jupiter.api.Test;
import org.lift.type.Structure;

public class SE_FiniteVerbTest {
		
	
	@Test
	public void finiteVerbTestGerman() throws Exception {

		// TODO SE should be able to provide its name
		// TODO SE should use internal name (package/class + FE)
		String structureName = "FiniteVerb";
		String featurePath = Structure.class.getName() + "/" + structureName;
		
		AnalysisEngine engine = createEngine(
				SE_FiniteVerb.class,
				SE_FiniteVerb.PARAM_LANGUAGE, "de");

		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				XmiReader.class,
				XmiReader.PARAM_SOURCE_LOCATION, "src/test/resources/xmi/news_de.txt.xmi"
		);
		for (JCas jcas : new JCasIterable(reader)) {
			engine.process(jcas);
		
			// TODO add real test
            for (Entry<AnnotationFS, String> entry : select(jcas.getCas(), featurePath)) {
            	System.out.println(entry.getKey().getCoveredText());
            }
		}
	}
}
