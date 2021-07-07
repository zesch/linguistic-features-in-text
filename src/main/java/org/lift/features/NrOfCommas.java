package org.lift.features;

import java.util.Set;

import org.apache.uima.fit.descriptor.LanguageCapability;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.tc.api.exception.TextClassificationException;
import org.dkpro.tc.api.features.Feature;
import org.dkpro.tc.api.features.FeatureType;
import org.lift.api.FeatureExtractor_ImplBase;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Counts the number of commas
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
@LanguageCapability({ "de","en" })
public class NrOfCommas 
	extends FeatureExtractor_ImplBase
{

	public static final String NR_OF_COMMAS = "nrOfCommas";
	
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
		double ratio = (double) nrOfCommas/nrOfTokens;
		try {
			return new Feature(NR_OF_COMMAS, ratio, FeatureType.NUMERIC).asSet();
		} catch (TextClassificationException e) {
			throw new LiftFeatureExtrationException(e);
		}
	}
}

