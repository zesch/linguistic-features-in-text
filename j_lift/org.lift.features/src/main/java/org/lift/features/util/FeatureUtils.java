package org.lift.features.util;

import java.util.List;

public class FeatureUtils {
	
	public static double getAverage(List<Double> ttrs) {
        double sum = 0.0;

        for (double value : ttrs) {
            sum += value;
        }

        return sum / ttrs.size();
    }

    public static double getStandardDeviation(List<Double> ttrs, double average) {
        double sumSquaredDiff = 0.0;

        for (double value : ttrs) {
            double diff = value - average;
            sumSquaredDiff += diff * diff;
        }

        double variance = sumSquaredDiff / ttrs.size();
        return Math.sqrt(variance);
    }
}
