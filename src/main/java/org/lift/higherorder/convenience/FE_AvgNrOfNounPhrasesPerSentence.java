package org.lift.higherorder.convenience;

import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FEL_AvgAnnotationRatio;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC;

public class FE_AvgNrOfNounPhrasesPerSentence extends FeatureExtractor_ImplBase {

	public FE_AvgNrOfNounPhrasesPerSentence() {
		super("NC_PER_SENTENCE", FEL_AvgAnnotationRatio.class.getName() + "__" + "NC_PER_SENTENCE");
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		String dividendFeaturePath = NC.class.getName();
		String divisorFeaturePath = Sentence.class.getName();
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(dividendFeaturePath, divisorFeaturePath);
		
		return extractor.extract(jcas);
	}

}
