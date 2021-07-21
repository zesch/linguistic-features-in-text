package org.lift.features;

import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Counts structures
 */

@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class FE_GenericStructureCounter 
	extends FeatureExtractor_ImplBase
{
	
	private final String structureName;

	public FE_GenericStructureCounter(String structureName) {
		super(structureName + "_counter", FE_GenericStructureCounter.class.getName() + "_" + structureName);
		this.structureName = structureName;
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) 
			throws LiftFeatureExtrationException
	{		
		// TODO parameterize normalization?
		int overallCount = JCasUtil.select(jcas, Token.class).size();
		
		int nrOfFeature = 0;
    	for (Structure s : JCasUtil.select(jcas, Structure.class)) {
    		if (s.getName().equals(structureName)) {
    			nrOfFeature++;
    		}
        }

		//Normalization on total count of words
		double ratio = (double) nrOfFeature / overallCount;
		
		return new Feature(getInternalName(), ratio, FeatureType.NUMERIC).asSet();
	}
}

