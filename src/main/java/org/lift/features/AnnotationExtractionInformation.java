package org.lift.features;

public class AnnotationExtractionInformation {

	private String featurePath;
	private String annotationType;
	
	public AnnotationExtractionInformation(String featurePath, String annotationValue) {
		this.featurePath = featurePath;
		this.annotationType = annotationValue;
	}
	
	public AnnotationExtractionInformation(String featurePath) {
		this.featurePath = featurePath;
	}

	public String getFeaturePath() {
		return featurePath;
	}

	public String getAnnotationValue() {
		return annotationType;
	}
	
}
