package org.lift.higherorder.genuine;

import java.io.InputStream;
import java.util.*;
import java.util.stream.Collectors;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.features.util.FeatureUtils;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

public class FE_MATTRCoarseGrainedPosClasses extends FeatureExtractor_ImplBase {

	private int windowSize;

	public FE_MATTRCoarseGrainedPosClasses(int windowSize) {
		this.windowSize = windowSize;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> features = new HashSet<>();
		// read all pos classes from extended text file
		Set<String> allCoarseGrainedPosTags = new HashSet<>();
		try {
			String file = "pos_tags/coarse_grained_pos_tags.txt";
			InputStream is = FeatureUtils.getSharedResourceAsStream(this.getClass(), file);
			allCoarseGrainedPosTags = FeatureUtils.readList(is);
		} catch (Exception e) {
			e.printStackTrace();
			System.out.println("An error occurred while reading the tagset file");
		}
		Collection<POS> poses = JCasUtil.select(jcas, POS.class);
		// Create a map to store lists of TTR values for each POS
		Map<String, List<Double>> posTTRMap = new HashMap<>();
		// Check if the window size is less than the size of the token list
		if (windowSize < poses.size()) {
			// Calculate TTR for multiple windows
			posTTRMap = calculateTTRForMultipleWindows(poses.stream().collect(Collectors.toList()),
					allCoarseGrainedPosTags.stream().collect(Collectors.toList()), windowSize);
		} else {
			// Calculate TTR for a single window
			posTTRMap = calculateTTRForSingleWindow(poses.stream().collect(Collectors.toList()),
					allCoarseGrainedPosTags.stream().collect(Collectors.toList()));
		}

		Map<String, double[]> statisticsMap = FeatureUtils.calculateAverageAndStdDev(posTTRMap);
		for (String tag : statisticsMap.keySet()) {
			features.add(new Feature("Avg_MATTR_Of_" + tag + "_WindowSize_" + windowSize, statisticsMap.get(tag)[0],
					FeatureType.NUMERIC));
			features.add(new Feature("StdDev_MATTR_Of_" + tag + "_WindowSize_" + windowSize, statisticsMap.get(tag)[1],
					FeatureType.NUMERIC));
		}
		return features;
	}

	private static Map<String, List<Double>> calculateTTRForSingleWindow(List<POS> posses, List<String> allPosTags) {
		// Create a map to store lists of TTR values for each POS
		Map<String, List<Double>> posTTRMap = new HashMap<>();

		// Initialize empty lists for each POS tag
		for (String pos : allPosTags) {
			posTTRMap.put(pos, new ArrayList<>());
		}
		// Create a map to group tokens by POS in the entire text
		Map<String, List<String>> posMap = new HashMap<>();

		for (POS p : posses) {
			String pos = p.getCoarseValue();
			String token = p.getCoveredText().toLowerCase(); // ignore case

			// Add token to the list for the corresponding POS
			posMap.putIfAbsent(pos, new ArrayList<>());
			posMap.get(pos).add(token);
		}

		// Calculate TTR for each POS in the entire text
		for (String pos : allPosTags) {
			List<String> tokens = posMap.getOrDefault(pos, Collections.emptyList());

			if (!tokens.isEmpty()) {
				// Use HashSet to find the number of unique types
				Set<String> types = new HashSet<>(tokens);
				double ttr = (double) types.size() / tokens.size();
				posTTRMap.get(pos).add(ttr);
			}
		}
		return posTTRMap;
	}

	private static Map<String, List<Double>> calculateTTRForMultipleWindows(List<POS> posses, List<String> allPosTags,
			int windowSize) {
		// Create a map to store lists of TTR values for each POS
		Map<String, List<Double>> posTTRMap = new HashMap<>();

		// Initialise empty lists for each POS tag
		for (String pos : allPosTags) {
			posTTRMap.put(pos, new ArrayList<>());
		}
		for (int i = 0; i <= posses.size() - windowSize; i++) {
			List<POS> window = posses.subList(i, i + windowSize);
			Map<String, List<String>> posMap = new HashMap<>();

			for (POS p : window) {
				String pos = p.getCoarseValue();
				String token = p.getCoveredText().toLowerCase(); // ignore case
				posMap.putIfAbsent(pos, new ArrayList<>());
				posMap.get(pos).add(token);
			}
			for (String pos : allPosTags) {
				List<String> tokens = posMap.getOrDefault(pos, Collections.emptyList());

				if (!tokens.isEmpty()) {
					// Use HashSet to find the number of unique types
					Set<String> types = new HashSet<>(tokens);
					double ttr = (double) types.size() / tokens.size();
					posTTRMap.get(pos).add(ttr);
				}
			}
		}
		return posTTRMap;
	}

	@Override
	public String getPublicName() {
		return "MATTRCoarseGrainedPosClasses";
	}
}