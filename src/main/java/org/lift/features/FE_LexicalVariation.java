package org.lift.features;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

public class FE_LexicalVariation extends FeatureExtractor_ImplBase {
	
	public static final String FN_LEXICAL_VARIATION = "LexicalVariation";
	public static final String FN_VERB_VARIATION = "VerbVariation";
	
	public FE_LexicalVariation() {
		super("LexicalVariation", FE_LexicalVariation.class.getName());			
	}

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

}

