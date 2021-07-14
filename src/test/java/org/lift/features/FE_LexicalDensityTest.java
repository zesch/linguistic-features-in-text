package org.lift.features;

import static org.lift.features.util.FeatureTestUtil.assertFeature;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.apache.uima.cas.TypeSystem;
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
        List<Feature> features = new ArrayList<Feature>(extractor.extract(jcas));

        Assert.assertEquals(1, features.size());

        Iterator<Feature> iter = features.iterator();
        Feature f = iter.next();
        System.out.println(f.toString());
        assertFeature(FE_LexicalDensity.FN_LD, 0.47159, f, 0.00001);
        break;
        
		}
        
    }
	
	
}
	
