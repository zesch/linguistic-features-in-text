package org.lift.features.util;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.io.IOUtils;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.resource.ResourceInitializationException;

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

	public static Map<String, double[]> calculateAverageAndStdDev(Map<String, List<Double>> posTTRMap) {
		Map<String, double[]> statisticsMap = new HashMap<>();

		for (String pos : posTTRMap.keySet()) {
			List<Double> ttrList = posTTRMap.get(pos);
			double sum = 0.0;
			double mean = 0.0;
			double stdDev = 0.0;

			if (ttrList.isEmpty()) {
				mean = -1.0; // Set mean to -1 if TTR list is empty
				stdDev = -1.0; // Set standard deviation to -1 if TTR list is empty
			} else if (ttrList.size() == 1) {
				mean = ttrList.get(0); // If TTR list contains only one element, set mean to value of that element
				stdDev = -1.0; // Set standard deviation to -1 if TTR list contains only one element which is
								// -1
			} else {
				for (double ttr : ttrList) {
					sum += ttr;
				}
				mean = sum / ttrList.size();

				double sumSquaredDiffs = 0.0;
				for (double ttr : ttrList) {
					sumSquaredDiffs += Math.pow(ttr - mean, 2);
				}
				stdDev = Math.sqrt(sumSquaredDiffs / ttrList.size());
			}

			statisticsMap.put(pos, new double[] { mean, stdDev });
		}

		return statisticsMap;
	}

	public static Set<String> readList(InputStream is) throws ResourceInitializationException {
		try {
			return new HashSet<String>(IOUtils.readLines(is, StandardCharsets.UTF_8));
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
	}

	public static InputStream getSharedResourceAsStream(Class<? extends JCasAnnotator_ImplBase> cls, String path)
			throws ResourceInitializationException {
//		// make sure path starts with "/"
//		if (!path.startsWith("/")) {
//			path = "/" + path;
//		}

		// make sure path does not start with "/"
		if (path.startsWith("/")) {
			path = path.substring(1);
		}
		System.out.println(path);

		InputStream is = cls.getClassLoader().getResourceAsStream(path);
		if (is == null) {
			throw new ResourceInitializationException(new Throwable("Cannot load resource from: " + path));
		}

		return is;
	}
}