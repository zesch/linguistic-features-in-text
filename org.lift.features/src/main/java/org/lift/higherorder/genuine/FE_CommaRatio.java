package org.lift.higherorder.genuine;

import java.util.Set;

import org.apache.uima.fit.descriptor.LanguageCapability;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Counts the number of commas
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
@LanguageCapability({ "de","en" })
public class FE_CommaRatio 
	extends FeatureExtractor_ImplBase
{
	
	@Override
	public Set<Feature> extract(JCas jcas) 
			throws LiftFeatureExtrationException
	{		
		int nrOfCommas = 0;
		int nrOfTokens = 0;
		for (Token token : JCasUtil.select(jcas, Token.class)) {
			if (token.getCoveredText().equals(",")) {
				nrOfCommas++;
			}
			nrOfTokens++;
		}

		//Normalization on total count of words
		double ratio = (double) nrOfCommas / nrOfTokens;
		return new Feature(getInternalName(), ratio, FeatureType.NUMERIC).asSet();
	}

	@Override
	public String getPublicName() {
		return "CommaRatio";
	}
}

