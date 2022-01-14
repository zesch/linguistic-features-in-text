package org.lift.structures;

import static org.dkpro.core.api.featurepath.FeaturePathFactory.select;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Map.Entry;

import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.collection.CollectionReaderDescription;
import org.apache.uima.fit.factory.CollectionReaderFactory;
import org.apache.uima.fit.pipeline.JCasIterable;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.io.xmi.XmiReader;
import org.junit.jupiter.api.Test;
import org.lift.api.Configuration.Language;
import org.lift.preprocessing.PreprocessingConfiguration;
import org.lift.preprocessing.TestUtils;
import org.lift.type.Structure;

public class SE_NominalizationTest {

	@Test
	public void nominalization_test() throws Exception {

		String rutaPath = "src/main/resources/nominalization_de.ruta";
		String structureName = "Nominalization";
		String featurePath = Structure.class.getName() + "/" + structureName;
		SEL_RutaFile se = new SEL_RutaFile(rutaPath, structureName);

		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				XmiReader.class,
				XmiReader.PARAM_SOURCE_LOCATION, "src/test/resources/xmi/news_de.txt.xmi"
		);
		for (JCas jcas : new JCasIterable(reader)) {
			se.process(jcas);
		
            for (Entry<AnnotationFS, String> entry : select(jcas.getCas(), featurePath)) {
            	System.out.println(entry.getKey().getCoveredText());
            }
		}
	}
	
	/* commented out because it seems to take very long
	@Test
	public void adhoc_document_nominalization() throws Exception {

		String filePath = "src/main/resources/nominalization_de.ruta";
		String structureName = "Nominalization";
		String featurePath = Structure.class.getName() + "/" + structureName;
		SEL_RutaFile se = new SEL_RutaFile(filePath, structureName);

		// TODO add some more test cases
		String nominalizations = "Bildung";
		String noNominalizations = "Energie Familie";
		JCas jcas = TestUtils.getJCasForString(
				nominalizations + " " + noNominalizations,
				new PreprocessingConfiguration(Language.German)
		);
		se.process(jcas);
		
		assertEquals(1, JCasUtil.select(jcas, Structure.class).size());
        
		for (Entry<AnnotationFS, String> entry : select(jcas.getCas(), featurePath)) {
        	System.out.println(entry.getKey().getCoveredText());
        }
	}
	*/
}
