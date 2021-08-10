package org.lift.features;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.jcas.tcas.Annotation;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

public class FE_AvgAnnotationRatio extends FeatureExtractor_ImplBase{
	
	private final String dividendFeaturePath;
	private final String divisorFeaturePath;

	public FE_AvgAnnotationRatio(String dividendFeaturePath, String divisorFeaturePath) {
		super(dividendFeaturePath + "_PER_" + divisorFeaturePath, FE_AvgAnnotationRatio.class.getName() + "__" + dividendFeaturePath + "_PER_" + divisorFeaturePath);
		this.dividendFeaturePath = dividendFeaturePath;
		this.divisorFeaturePath = divisorFeaturePath;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Class<? extends Annotation> dividendClass = null;
		Class<? extends Annotation> divisorClass = null;
		try {
			dividendClass = Class.forName(dividendFeaturePath).asSubclass(Annotation.class);
			divisorClass = Class.forName(divisorFeaturePath).asSubclass(Annotation.class);
		} catch (ClassNotFoundException e) {
			throw new LiftFeatureExtrationException(e);
		}
		
		Set<Feature> featureSet = new HashSet<Feature>();
		Collection<? extends Annotation> dividends = JCasUtil.select(jcas, dividendClass);
		Collection<? extends Annotation> divisors = JCasUtil.select(jcas, divisorClass);
		double numDividends = dividends.size();
		double numDivisors = divisors.size();
		
		double avgSize = numDividends / numDivisors;
		
		double varianceSum = 0;
		for (Annotation divis : divisors) {
			double dividendSize = JCasUtil.selectCovered(jcas, dividendClass, divis).size();
			double deviation = dividendSize - avgSize;
			varianceSum += Math.pow(deviation, 2);
		}
		double stndDeviation = Math.sqrt(varianceSum/numDivisors);
		
		featureSet.add(new Feature("FN_" +  buildBaseFeatureString(dividendClass, divisorClass), avgSize, FeatureType.NUMERIC));
		featureSet.add(new Feature("STANDARD_DEVIATION_OF_" + buildBaseFeatureString(dividendClass, divisorClass), stndDeviation, FeatureType.NUMERIC));
		return featureSet;
	}
	
	private String buildBaseFeatureString(Class<?> dividend, Class<?> divisor) {
		return (dividend.getSimpleName() + "_PER_" + divisor.getSimpleName()).toUpperCase();
	}

}
