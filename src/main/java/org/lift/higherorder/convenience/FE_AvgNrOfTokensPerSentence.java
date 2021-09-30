package org.lift.higherorder.convenience;

import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FEL_AvgAnnotationRatio;
import org.lift.features.FeatureExtractor_ImplBase;


import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Calculates the average number of Token per Sentence.
 * Uses {@link FEL_AvgAnnotationRatio}.
 */
public class FE_AvgNrOfTokensPerSentence extends FeatureExtractor_ImplBase {

	public FE_AvgNrOfTokensPerSentence() {
		super("TOKEN_PER_SENTENCE", FEL_AvgAnnotationRatio.class.getName() + "__" + "TOKEN_PER_SENTENCE");
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		String dividendFeaturePath = Token.class.getName();
		String divisorFeaturePath = Sentence.class.getName();
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
		
		return extractor.extract(jcas);
	}

}
