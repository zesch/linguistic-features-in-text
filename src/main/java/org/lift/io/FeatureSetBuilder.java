package org.lift.io;

import java.util.LinkedHashSet;
import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FEL_AvgAnnotationRatio;
import org.lift.higherorder.FE_AvgNrOfCharsPerSentence;
import org.lift.higherorder.FE_AvgNrOfCharsPerToken;
import org.lift.higherorder.FE_LexicalDensity;
import org.lift.higherorder.FE_LexicalVariation;
import org.lift.higherorder.FE_NrOfChars;
import org.lift.higherorder.FE_TypeTokenRatio;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.NC;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.PC;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.VC;
import edu.stanford.nlp.patterns.surface.Token;

public class FeatureSetBuilder {

	public static Set<Feature> buildFeatureSet(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureSet = new LinkedHashSet<Feature>();
		featureSet.addAll(getAvgNrOfCharsPerSentence(jcas));
		featureSet.addAll(getAfgNrOfCharsPerToken(jcas));
		featureSet.addAll(getAvgNrOfTokenPerSentence(jcas));
		featureSet.addAll(getNrOfChars(jcas));
		featureSet.addAll(getNounPhrasesPerSentence(jcas));
		featureSet.addAll(getVerbPhrasesPerSentence(jcas));
		featureSet.addAll(getPrepositionalPhrasePerSentence(jcas));
		featureSet.addAll(getLexicalDensity(jcas));
		featureSet.addAll(getLexicalVariation(jcas));
		featureSet.addAll(getTypeTokenRatio(jcas));
		
		return featureSet;
	}
	
	private static Set<Feature> getAvgNrOfCharsPerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FE_AvgNrOfCharsPerSentence extractor = new FE_AvgNrOfCharsPerSentence();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getAfgNrOfCharsPerToken(JCas jcas) throws LiftFeatureExtrationException {
		FE_AvgNrOfCharsPerToken extractor = new FE_AvgNrOfCharsPerToken();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getAvgNrOfTokenPerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(Token.class.getName(), Sentence.class.getName());
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getNrOfChars(JCas jcas) throws LiftFeatureExtrationException {
		FE_NrOfChars extractor = new FE_NrOfChars();
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getNounPhrasesPerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(NC.class.getName(), Sentence.class.getName());
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getVerbPhrasesPerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(VC.class.getName(), Sentence.class.getName());
		return extractor.extract(jcas);
	}
	
	private static Set<Feature> getPrepositionalPhrasePerSentence(JCas jcas) throws LiftFeatureExtrationException {
		FEL_AvgAnnotationRatio extractor = new FEL_AvgAnnotationRatio(PC.class.getName(), Sentence.class.getName());
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
