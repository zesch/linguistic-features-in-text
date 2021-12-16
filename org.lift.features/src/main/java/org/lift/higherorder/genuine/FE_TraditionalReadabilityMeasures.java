package org.lift.higherorder.genuine;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.readability.measure.ReadabilityMeasures;
import org.dkpro.core.readability.measure.ReadabilityMeasures.Measures;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_TraditionalReadabilityMeasures extends FeatureExtractor_ImplBase {
	
	private List<ReadabilityConfiguration> readabilityConfigurations;

	public FE_TraditionalReadabilityMeasures(List<ReadabilityConfiguration> readabilityConfigurations) {
		super("TraditionalReadabilityMeasures", FE_TraditionalReadabilityMeasures.class.getName());
		this.readabilityConfigurations = readabilityConfigurations;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureSet = new HashSet<>();
		
		int nrOfSentences = JCasUtil.select(jcas,  Sentence.class).size();
		List<String> words = new ArrayList<String>();
		for (Token t : JCasUtil.select(jcas, Token.class)) {
			words.add(t.getCoveredText());
		}
		
		ReadabilityMeasures readability = new ReadabilityMeasures();
		String documentLanguage = jcas.getDocumentLanguage();
		if (documentLanguage != null) {
			readability.setLanguage(documentLanguage);
		}
		
		for(ReadabilityConfiguration config : readabilityConfigurations) {
			featureSet.add(extractReadabilityMeasure(config, words, nrOfSentences, readability));
		}
		
		return featureSet;
	}
	
	private Feature extractReadabilityMeasure(ReadabilityConfiguration configuration, List<String> words, int nrOfSentences,
			ReadabilityMeasures readability) throws LiftFeatureExtrationException {
		Measures measure = Measures.valueOf(configuration.getStringValue());
		return new Feature("READABILITY_MEASURE_" + configuration.toString(),
				readability.getReadabilityScore(measure, words, nrOfSentences), FeatureType.NUMERIC);
	}

}
