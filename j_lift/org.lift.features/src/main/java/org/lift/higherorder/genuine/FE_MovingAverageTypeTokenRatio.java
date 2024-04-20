package org.lift.higherorder.genuine;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.features.util.FeatureUtils;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Moving Average Type-Token Ratio (MATTR) with Sliding Window Approach,
 * allow the adjustment of the window size parameter
 * Features are the average and the standard deviation.
 * 
 * @author vietphe
 */
public class FE_MovingAverageTypeTokenRatio extends FeatureExtractor_ImplBase{
	
	private int slidingSize;

	public FE_MovingAverageTypeTokenRatio(int slidingSize) {
		this.slidingSize = slidingSize;
	}
	
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> features = new HashSet<Feature>();
		
		Collection<Token> ts = JCasUtil.select(jcas, Token.class);
		// copy the token collection to an array list
		List<Token> tokens = new ArrayList<>(ts);
		int tokenSize = tokens.size();
		// a list to contain the ttr values of all sliding windows
		List<Double> ttrs = new ArrayList<>();
		
		// if the length of the text is less than the sliding size
		if (tokenSize <= slidingSize) { 
			List<String> words = new ArrayList<>();
			Set<String> differentWords = new HashSet<>();
			for (Token t : tokens) {
				words.add(t.getCoveredText().toLowerCase());
				differentWords.add(t.getCoveredText().toLowerCase());
			}
			ttrs.add((double) differentWords.size()/words.size());
		} else {			
			int stepper = 0;		
			while ((stepper+slidingSize) <= tokenSize) {
				List<String> words = new ArrayList<>();
				Set<String> differentWords = new HashSet<>();
				for (int i = stepper; i <= stepper+slidingSize-1; i++) {
					words.add(tokens.get(i).getCoveredText().toLowerCase());
					differentWords.add(tokens.get(i).getCoveredText().toLowerCase());
				}
				ttrs.add((double) differentWords.size()/words.size());
				stepper++;
			}
		}								
		double average = FeatureUtils.getAverage(ttrs);
		double standardDeviation = FeatureUtils.getStandardDeviation(ttrs, average);
		features.add(
				new Feature("AVERAGE_MATTR_OF_SLIDING_WINDOW_SIZE_" + slidingSize, 
						average, 
						FeatureType.NUMERIC)
				);
		features.add(
				new Feature("STANDARD_DEVIATION_MATTR_OF_SLIDING_WINDOW_SIZE_" + slidingSize, 
						standardDeviation, 
						FeatureType.NUMERIC)
				);
		return features;
	}

	@Override
	public String getPublicName() {		
		return "MovingAverageTypeTokenRatio";
	}
}
