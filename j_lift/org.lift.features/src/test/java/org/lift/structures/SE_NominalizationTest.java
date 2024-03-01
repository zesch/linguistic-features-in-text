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

public class SE_NominalizationTest {

	@Test
	public void nominalization_test() throws Exception {

		AnalysisEngine engine = createEngine(
				SE_Nominalizations.class,
				SE_Nominalizations.PARAM_LANGUAGE, "de"
		);
		
		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				XmiReader.class,
				XmiReader.PARAM_SOURCE_LOCATION, "src/test/resources/xmi/news_de.txt.xmi"
		);
		
		String featurePath = Structure.class.getName() + "/" + new SE_Nominalizations().getStructureName();
		for (JCas jcas : new JCasIterable(reader)) {
			engine.process(jcas);
		
            for (Entry<AnnotationFS, String> entry : select(jcas.getCas(), featurePath)) {
            	System.out.println(entry.getKey().getCoveredText());
            }
		}
	}
}
