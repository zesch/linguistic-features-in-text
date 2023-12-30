package org.lift.higherorder.genuine;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

/**
 * Calculates the lexical density by extracting the ratio of defined content words per overall POS tags.
 * The default defines adjectives, verbs and nouns as content words. The forwarded JCas has to be POS tagged.
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS" })
public class FE_LexicalDensity 
	extends FeatureExtractor_ImplBase
{

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
		features.add(new Feature(getInternalName(), ld, FeatureType.NUMERIC));

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

	@Override
	public String getPublicName() {
		return "LexicalDensity";
	}

}
