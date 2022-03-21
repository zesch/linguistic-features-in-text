package org.lift.higherorder.genuine;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

/**
 * Extracts the lexical and verb variation. The verb variation is calculatd as the ratio of verbtypes per overall verbs.
 * The lexical variation is calculated as the ratio of contentwordtypes per overall contentwords.
 * The JCas hast to be POS tagged.
 */
public class FE_LexicalVariation 
	extends FeatureExtractor_ImplBase
{
	
	public static final String FN_LEXICAL_VARIATION = "LexicalVariation";
	public static final String FN_VERB_VARIATION = "VerbVariation";
	

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		
		int numberOfContentWords = 0;
		Set<String> contentWordTypes = new HashSet<String>();

		int numberOfVerbs = 0;
		Set<String> verbTypes = new HashSet<String>();
		
		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			
			if (isContentWord(pos.getCoarseValue())){
				numberOfContentWords++;
				contentWordTypes.add(pos.getCoveredText().toLowerCase());
			}
			if (pos.getCoarseValue().equals("VERB")){
				numberOfVerbs++;
				verbTypes.add(pos.getCoveredText().toLowerCase());
			}
		}
		
		double lexicalVariation = (1.0*contentWordTypes.size())/numberOfContentWords;
		double verbVariation = (1.0*verbTypes.size())/numberOfVerbs;
		
		Set<Feature> features = new HashSet<Feature>();
		features.add(new Feature(FN_LEXICAL_VARIATION, lexicalVariation, FeatureType.NUMERIC));
		features.add(new Feature(FN_VERB_VARIATION, verbVariation, FeatureType.NUMERIC));
		return features;
	}
	
	private boolean isContentWord(String coarseValue) {
		if (coarseValue.equals("ADJ") || coarseValue.equals("VERB") || coarseValue.startsWith("N")){
			return true;
		} else {
			return false;
		}
	}

	@Override
	public String getPublicName() {
		return "LexicalVariation";
	}

}

