package org.lift.features.api;

import java.util.Set;

import org.apache.uima.jcas.JCas;

public abstract class FeatureExtractor_ImplBase 
	implements FeatureExtractor
{

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		return extract(jcas, null);
	}	

	@Override
	public Set<Feature> extract(String text) throws LiftFeatureExtrationException {
		throw new UnsupportedOperationException();
	}	
}