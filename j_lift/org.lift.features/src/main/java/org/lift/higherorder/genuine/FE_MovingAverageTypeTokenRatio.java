package org.lift.higherorder.genuine;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Moving Average Type-Token Ratio (MATTR) with Sliding Window Approach,
 * allow the adjustment of the window size parameter
 * Features are the average and the standard deviation.
 * 
 * @author vietphe
 */
public class FE_MovingAverageTypeTokenRatio extends FeatureExtractor_ImplBase{
	
	//TODO: adjust sliding size by number of tokens
	private static final int SLIDING_SIZE = 6;

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> features = new HashSet<Feature>();
		
		Collection<Token> ts = JCasUtil.select(jcas, Token.class);
		// copy the token collection to an array list
		List<Token> tokens = new ArrayList<>(ts);
		int tokenSize = tokens.size();
		// a map to contain the ttr values of all sliding windows
		Map<Integer,Double> ttrs = new HashMap<>();
		
		// if the length of the text is less than the sliding size
		if (tokenSize <= SLIDING_SIZE) { 
			List<String> words = new ArrayList<>();
			Set<String> differentWords = new HashSet<>();
			for (Token t : tokens) {
				words.add(t.getCoveredText().toLowerCase());
				differentWords.add(t.getCoveredText().toLowerCase());
			}
			ttrs.put(0, (double) differentWords.size()/words.size());
		} else {			
			int stepper = 0;		
			while ((stepper+SLIDING_SIZE) <= tokenSize) {
				List<String> words = new ArrayList<>();
				Set<String> differentWords = new HashSet<>();
				for (int i = stepper; i <= stepper+SLIDING_SIZE-1; i++) {
					words.add(tokens.get(i).getCoveredText().toLowerCase());
					differentWords.add(tokens.get(i).getCoveredText().toLowerCase());
				}
				ttrs.put(stepper, (double) differentWords.size()/words.size());
				stepper++;
			}
		}								
		double average = calculateAverage(ttrs);
		double standardDeviation = calculateStandardDeviation(ttrs, average);
		features.add(
				new Feature("AVERAGE_MATTR_OF_SLIDING_WINDOW_SIZE_" + SLIDING_SIZE, 
						average, 
						FeatureType.NUMERIC)
				);
		features.add(
				new Feature("STANDARD_DEVIATION_MATTR_OF_SLIDING_WINDOW_SIZE_" + SLIDING_SIZE, 
						standardDeviation, 
						FeatureType.NUMERIC)
				);
		return features;
	}

	@Override
	public String getPublicName() {		
		return "MovingAverageTypeTokenRatio";
	}
	
	private static double calculateAverage(Map<Integer, Double> ttrs) {
        double sum = 0.0;

        for (double value : ttrs.values()) {
            sum += value;
        }

        return sum / ttrs.size();
    }

    private static double calculateStandardDeviation(Map<Integer, Double> ttrs, double average) {
        double sumSquaredDiff = 0.0;

        for (double value : ttrs.values()) {
            double diff = value - average;
            sumSquaredDiff += diff * diff;
        }

        double variance = sumSquaredDiff / ttrs.size();
        return Math.sqrt(variance);
    }

}
