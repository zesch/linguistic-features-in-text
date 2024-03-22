package org.lift.higherorder.genuine;

import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FEL_GenericStructureCounter;
import org.lift.features.FeatureExtractor_ImplBase;
/**
 * Extracts the ratio of verbs are auxiliary verbs (to be / to have).
 * 
 * @author vietphe
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class FE_AvgNrOfAuxiliaryVerb 
	extends FeatureExtractor_ImplBase
{

	private FEL_GenericStructureCounter counter;
	
	public FE_AvgNrOfAuxiliaryVerb() {
		counter = new FEL_GenericStructureCounter("AuxiliaryVerb");
	}
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		
		return counter.extract(jcas);
		
	}

	@Override
	public String getPublicName() {
		return counter.getPublicName();
	}
	
	@Override
	public String getInternalName() {
		return counter.getInternalName();
	}
	
}
