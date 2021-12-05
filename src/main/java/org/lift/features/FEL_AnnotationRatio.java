package org.lift.features;


import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.apache.uima.cas.text.AnnotationFS;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.tcas.Annotation;
import org.dkpro.core.api.featurepath.FeaturePathException;
import org.dkpro.core.api.featurepath.FeaturePathFactory;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

public class FEL_AnnotationRatio extends FeatureExtractor_ImplBase{
	
	private final AnnotationExtractionInformation dividendFeature;
	private final AnnotationExtractionInformation divisorFeature;

	public FEL_AnnotationRatio(AnnotationExtractionInformation dividendFeature, AnnotationExtractionInformation divisorFeature) {
		super(dividendFeature.getFeaturePath() + "_PER_" + divisorFeature.getFeaturePath(),
				FEL_AnnotationRatio.class.getName());
		this.dividendFeature = dividendFeature;
		this.divisorFeature = divisorFeature;
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		double numDividends = calculateAnnotationSize(jcas, dividendFeature);
		double numDivisors = calculateAnnotationSize(jcas, divisorFeature);
		
		double avgSize = numDividends / numDivisors;
		
		Set<Feature> featureSet = new HashSet<Feature>();
		featureSet.add(new Feature("FN_" +  buildBaseFeatureString(dividendFeature, divisorFeature), avgSize, FeatureType.NUMERIC));
		return featureSet;
	}
	
	private double calculateAnnotationSize(JCas jcas, AnnotationExtractionInformation information) throws LiftFeatureExtrationException {
		double size = 0;
		try {
			for (Entry<AnnotationFS, String> entry : FeaturePathFactory.select(jcas.getCas(), information.getFeaturePath())) {
				if(information.getAnnotationValue() == null || entry.getValue().equals(information.getAnnotationValue())) {
					size++;
				}
			}
		} catch (FeaturePathException e) {
            throw new LiftFeatureExtrationException(e);
        }
		return size;
	}
	
	String buildBaseFeatureString(AnnotationExtractionInformation dividendFeature, AnnotationExtractionInformation divisorFeature) throws LiftFeatureExtrationException {
		return (buildAnnotationString(dividendFeature) + "_PER_" + buildAnnotationString(divisorFeature)).toUpperCase();
	}
	
	private String buildAnnotationString(AnnotationExtractionInformation information) throws LiftFeatureExtrationException {
		if(information.getAnnotationValue() == null || information.getAnnotationValue().isEmpty()) {
			try {
				return Class.forName(information.getFeaturePath()).asSubclass(Annotation.class).getSimpleName();
			} catch (ClassNotFoundException e) {
				throw new LiftFeatureExtrationException(e);
			}
		} else {
			return information.getAnnotationValue();
		}
	}
	
}
