package org.lift.features;

import static org.lift.features.util.FeatureTestUtil.assertFeatures;

import java.util.Set;

import org.apache.uima.collection.CollectionReaderDescription;
import org.apache.uima.fit.factory.CollectionReaderFactory;
import org.apache.uima.fit.pipeline.JCasIterable;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.io.xmi.XmiReader;
import org.junit.Assert;
import org.junit.Test;
import org.lift.api.Feature;

public class FE_LexicalDensityTest {

	@Test
    public void lexicalDensityFeatureExtractorTest_de() 
        throws Exception
    {
    	
		CollectionReaderDescription reader = CollectionReaderFactory.createReaderDescription(
				XmiReader.class,
				XmiReader.PARAM_LANGUAGE, "de",
				XmiReader.PARAM_SOURCE_LOCATION, "src/test/resources/xmi/news_de.txt.xmi",
				XmiReader.PARAM_TYPE_SYSTEM_FILE, "src/test/resources/xmi/TypeSystem.xml");
		
		for (JCas jcas : new JCasIterable(reader)) {

        FE_LexicalDensity extractor = new FE_LexicalDensity();
        Set<Feature> features = extractor.extract(jcas);

        Assert.assertEquals(1, features.size());
        System.out.println(features);

        assertFeatures(extractor.getInternalName(), 0.47159, features, 0.00001);
        break;
        
		}
        
    }
	
	
}
	
