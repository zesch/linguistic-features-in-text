package org.lift.io;

import java.util.LinkedHashSet;
import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.higherorder.genuine.FE_CharsPerSentence;
import org.lift.higherorder.genuine.FE_CharsPerToken;
import org.lift.higherorder.genuine.FE_LexicalDensity;
import org.lift.higherorder.genuine.FE_LexicalVariation;
import org.lift.higherorder.genuine.FE_NrOfChars;
import org.lift.higherorder.genuine.FE_TypeTokenRatio;

public class FeatureSetBuilder {

	public static Set<Feature> buildFeatureSet(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureSet = new LinkedHashSet<Feature>();
		featureSet.addAll(getAvgNrOfCharsPerSentence(jcas));
		featureSet.addAll(getAfgNrOfCharsPerToken(jcas));
		featureSet.addAll(getNrOfChars(jcas));
		featureSet.addAll(getLexicalDensity(jcas));
		featureSet.addAll(getLexicalVariation(jcas));
		featureSet.addAll(getTypeTokenRatio(jcas));
		
		return featureSet;
	}
	
	private static Set<Feature> getAvgNrOfCharsPerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FE_CharsPerSentence extractor = new FE_CharsPerSentence();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getAfgNrOfCharsPerToken(JCas jcas) throws LiftFeatureExtrationException {
		FE_CharsPerToken extractor = new FE_CharsPerToken();
		return extractor.extract(jcas);
	}	
	
	private static Set<Feature> getNrOfChars(JCas jcas) throws LiftFeatureExtrationException {
		FE_NrOfChars extractor = new FE_NrOfChars();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getLexicalDensity(JCas jcas) throws LiftFeatureExtrationException {
		FE_LexicalDensity extractor = new FE_LexicalDensity();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getLexicalVariation(JCas jcas) throws LiftFeatureExtrationException {
		FE_LexicalVariation extractor = new FE_LexicalVariation();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getTypeTokenRatio(JCas jcas) throws LiftFeatureExtrationException {
		FE_TypeTokenRatio extractor = new FE_TypeTokenRatio();
		return extractor.extract(jcas);		
	}
	
	
}
