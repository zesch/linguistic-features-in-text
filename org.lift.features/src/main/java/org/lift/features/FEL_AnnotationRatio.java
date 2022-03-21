package org.lift.features;

import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.featurepath.FeaturePathException;
import org.dkpro.core.api.featurepath.FeaturePathFactory;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

public class FEL_AnnotationRatio 
	extends FeatureExtractor_ImplBase
{
	private String dividendType;
	private String dividendFeature;
	private String divisorType;
	private String divisorFeature;
	
	public FEL_AnnotationRatio(String dividendType, String divisorType) {
		this.dividendType = dividendType;
		this.dividendFeature = null;
		this.divisorType = divisorType;
		this.divisorFeature = null;
	}
	
	public FEL_AnnotationRatio(String dividendType, String dividendFeature, String divisorType, String divisorFeature) {
		this.dividendType = dividendType;
		this.dividendFeature = dividendFeature;
		this.divisorType = divisorType;
		this.divisorFeature = divisorFeature;
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) 
			throws LiftFeatureExtrationException
	{
		double numDividends = calculateAnnotationSize(jcas, dividendType, dividendFeature);
		double numDivisors = calculateAnnotationSize(jcas, divisorType, divisorFeature);
		
		// TODO what to do about division by zero here?
		double avgSize = numDividends / numDivisors;
		
		Set<Feature> featureSet = new HashSet<Feature>();
		featureSet.add(new Feature("FN_" + getInternalName(), avgSize, FeatureType.NUMERIC));
		return featureSet;
	}
	
	private double calculateAnnotationSize(JCas jcas, String type, String feature) 
			throws LiftFeatureExtrationException
	{
		double size = 0;
		try {
			for (Entry<AnnotationFS, String> entry : FeaturePathFactory.select(jcas.getCas(), type)) {
				// if feature is null it means we can count any entry
				if(feature == null || entry.getValue().equals(feature)) {
					size++;
				}
			}
		} catch (FeaturePathException e) {
            throw new LiftFeatureExtrationException(e);
        }
		return size;
	}

	@Override
	public String getPublicName() {
		return this.cleanName(dividendType + "/" + dividendFeature + "_PER_" + divisorType + "/" + divisorFeature);
	}

	@Override
	public String getInternalName() {
		return "AnnotationRatio_" + getPublicName();
	}
}
