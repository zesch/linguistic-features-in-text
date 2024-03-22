package org.lift.higherorder.genuine;

import java.util.HashSet;
import java.util.Set;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.type.CEFR;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Extract the ratio of words and phrases with levels from A1 to C1 according to EVP
 * 
 * @author Viet Phe
 */
public class FE_EVPLevelRatio extends FeatureExtractor_ImplBase{
		
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		
		Set<Feature> features = new HashSet<Feature>();
		int tokenSize = JCasUtil.select(jcas, Token.class).size();

		int nrOfA1Words = 0;
		int nrOfA2Words = 0;
		int nrOfB1Words = 0;
		int nrOfB2Words = 0;
		int nrOfC1Words = 0;
		int nrOfC2Words = 0;
		
		int nrOfA1Phrases = 0;
		int nrOfA2Phrases = 0;
		int nrOfB1Phrases = 0;
		int nrOfB2Phrases = 0;
		int nrOfC1Phrases = 0;
		int nrOfC2Phrases = 0;
				
		for (CEFR f : JCasUtil.select(jcas, CEFR.class)) {
			if(f.getLevel().equals("A1")) {
				nrOfA1Words++;
			}else if(f.getLevel().equals("A2")) {
				nrOfA2Words++;
			}else if(f.getLevel().equals("B1")) {
				nrOfB1Words++;
			}else if(f.getLevel().equals("B2")) {
				nrOfB2Words++;
			}else if(f.getLevel().equals("C1")) {
				nrOfC1Words++;
			}else if(f.getLevel().equals("C2")) {
				nrOfC2Words++;
			}else if(f.getLevel().equals("PHRASE_A1")) {
				nrOfA1Phrases++;
			}else if(f.getLevel().equals("PHRASE_A2")) {
				nrOfA2Phrases++;
			}else if(f.getLevel().equals("PHRASE_B1")) {
				nrOfB1Phrases++;
			}else if(f.getLevel().equals("PHRASE_B2")) {
				nrOfB2Phrases++;
			}else if(f.getLevel().equals("PHRASE_C1")) {
				nrOfC1Phrases++;
			}else if(f.getLevel().equals("PHRASE_C2")) {
				nrOfC2Phrases++;
			}			
		}
				
		features.add( new Feature("A1Ratio", (double)nrOfA1Words/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("A2Ratio", (double)nrOfA2Words/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("B1Ratio", (double)nrOfB1Words/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("B2Ratio", (double)nrOfB2Words/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("C1Ratio", (double)nrOfC1Words/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("C2Ratio", (double)nrOfC2Words/tokenSize, FeatureType.NUMERIC));
		
		features.add( new Feature("A1PhraseRatio", (double)nrOfA1Phrases/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("A2PhraseRatio", (double)nrOfA2Phrases/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("B1PhraseRatio", (double)nrOfB1Phrases/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("B2PhraseRatio", (double)nrOfB2Phrases/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("C1PhraseRatio", (double)nrOfC1Phrases/tokenSize, FeatureType.NUMERIC));
		features.add( new Feature("C2PhraseRatio", (double)nrOfC2Phrases/tokenSize, FeatureType.NUMERIC));
			
		return features;
	}

	@Override
	public String getPublicName() {
		return "EVPLevelRatio";
	}

}
