package org.lift.features;

import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Predicate;

import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.featurepath.FeaturePathException;
import org.dkpro.core.api.featurepath.FeaturePathFactory;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

/**
 * Counts structures
 */

@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class FE_GenericCounter 
	extends FeatureExtractor_ImplBase
{
	
	private final String featurePath;
	private final Predicate<String> isFeature;

	public FE_GenericCounter(String featurePath, Predicate<String> isFeature) {
		super(featurePath + "_counter", FE_GenericCounter.class.getName() + "__" + featurePath);
		
		this.featurePath = featurePath;
		this.isFeature = isFeature;
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) 
			throws LiftFeatureExtrationException
	{		
		int nrOfFeature = 0;
		int overallCount = 0;
		
        try {
            for (Entry<AnnotationFS, String> entry: FeaturePathFactory.select(jcas.getCas(), featurePath)) {
    			if (isFeature.test(entry.getValue())) {
    				nrOfFeature++;
    			}
    			overallCount++;
            }
        } catch (FeaturePathException e) {
            throw new LiftFeatureExtrationException(e);
        }

		//Normalization on total count of words
		double ratio = (double) nrOfFeature / overallCount;
		
		return new Feature(getInternalName(), ratio, FeatureType.NUMERIC).asSet();
	}
}

