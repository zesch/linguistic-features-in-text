package org.lift.features;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.frequency.util.FrequencyDistribution;
import org.lift.api.Feature;
import org.lift.api.FeatureExtractor;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_TypeTokenRatio 
	implements FeatureExtractor
{

	public static final String FN_TTR = "TypeTokenRatio";

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
		features.add(new Feature(FN_TTR, ttr, FeatureType.NUMERIC));

		return features;
	}
}