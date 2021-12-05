package org.lift.higherorder.convenience;

import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.AnnotationExtractionInformation;
import org.lift.features.FEL_AnnotationRatio;
import org.lift.features.FeatureExtractor_ImplBase;


import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Calculates the average number of Token per Sentence.
 * Uses {@link FEL_AvgAnnotationRatio}.
 */
public class FE_AvgNrOfTokensPerSentence extends FeatureExtractor_ImplBase {

	public FE_AvgNrOfTokensPerSentence() {
		super("TOKEN_PER_SENTENCE", FEL_AnnotationRatio.class.getName() + "__" + "TOKEN_PER_SENTENCE");
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		AnnotationExtractionInformation dividendFeaturePath = new AnnotationExtractionInformation(Token.class.getName());
		AnnotationExtractionInformation divisorFeaturePath = new AnnotationExtractionInformation(Sentence.class.getName());
		FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeaturePath, divisorFeaturePath);
		
		return extractor.extract(jcas);
	}

}
