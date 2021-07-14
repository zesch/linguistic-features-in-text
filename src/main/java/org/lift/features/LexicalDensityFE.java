package org.lift.features;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureExtractor;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS" })
public class LexicalDensityFE 
	implements FeatureExtractor
{
	
	public static final String FN_LD = "LexicalDensity";

	@Override
	public Set<Feature> extract(JCas jcas)
			throws LiftFeatureExtrationException {

		int numberOfContentWords = 0;

		int n=0;
		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			if (isContentWord(pos.getCoarseValue())){
				numberOfContentWords++;
			}
			n++;
		}

		double ld = (double) numberOfContentWords / n ;
		
		Set<Feature> features = new HashSet<Feature>();
		features.add(new Feature(FN_LD, ld, FeatureType.NUMERIC));

		return features;
	}

	// TODO: Are those all content words? What about adverbs?
	// TODO: make parametrizable
	private boolean isContentWord(String coarseValue) {
		if (coarseValue != null && (coarseValue.equals("ADJ") || coarseValue.equals("VERB") || coarseValue.startsWith("N"))){
			return true;
		} else {
			return false;
		}
	}

}
