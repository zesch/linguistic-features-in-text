package org.lift.higherorder.convenience;

import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.AnnotationExtractionInformation;
import org.lift.features.FEL_AnnotationRatio;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC;

public class FE_AvgNrOfNounPhrasesPerSentence extends FeatureExtractor_ImplBase {

	public FE_AvgNrOfNounPhrasesPerSentence() {
		super("NC_PER_SENTENCE", FEL_AnnotationRatio.class.getName() + "__" + "NC_PER_SENTENCE");
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		AnnotationExtractionInformation dividendFeaturePath = new AnnotationExtractionInformation(NC.class.getName());
		AnnotationExtractionInformation divisorFeaturePath = new AnnotationExtractionInformation(Sentence.class.getName());
		FEL_AnnotationRatio extractor = new FEL_AnnotationRatio(dividendFeaturePath, divisorFeaturePath);
		
		return extractor.extract(jcas);
	}

}
