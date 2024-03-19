package org.lift.io;

import java.util.LinkedHashSet;
import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.LiftFeatureExtrationException;

public class FeatureSetBuilder {

	public static Set<Feature> buildFeatureSet(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureSet = new LinkedHashSet<Feature>();
		return featureSet;
	}
}
