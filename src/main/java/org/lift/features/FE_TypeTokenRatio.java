package org.lift.features;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.frequency.util.FrequencyDistribution;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Extracts the ratio of types per tokens.
 */
public class FE_TypeTokenRatio 
	extends FeatureExtractor_ImplBase
{

	public FE_TypeTokenRatio() {
		super("TypeTokenRatio", FE_TypeTokenRatio.class.getName());
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		FrequencyDistribution<String> fd = new FrequencyDistribution<String>();

		for (Token token : JCasUtil.select(jcas, Token.class)) {
			fd.inc(token.getCoveredText().toLowerCase());
		}
		double ttr = 0.0;
		if (fd.getN() > 0) {
			ttr = (double) fd.getB() / fd.getN();
		}

		Set<Feature> features = new HashSet<Feature>();
		features.add(new Feature(getInternalName(), ttr, FeatureType.NUMERIC));

		return features;
	}
}