package org.lift.higherorder.genuine;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.apache.commons.io.FileUtils;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.features.util.FeatureUtils;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

/**
 * filter for instances of POS classes
 *
 * @author vietphe
 */
public class FE_POSFilter extends FeatureExtractor_ImplBase {

	private int nrOfPOSInstance;
	private String languageCode;

	public FE_POSFilter(int nrOfPOSInstance, String languageCode) {
		this.nrOfPOSInstance = nrOfPOSInstance;
		this.languageCode = languageCode;
	}

	static Set<String> readList(String listFilePath) throws IOException {

		Set<String> listSet = new HashSet<String>();
		for (String line : FileUtils.readLines(new File(listFilePath), "UTF-8")) {
			listSet.add(line);
		}
		return listSet;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> features = new HashSet<>();
		// read all pos classes from extended text file
		Set<String> allPosTags = new HashSet<>();

		try {
			if (languageCode.equalsIgnoreCase("en")) {
				String file = "pos_tags/ptb_pos_tags.txt";
				InputStream is = FeatureUtils.getSharedResourceAsStream(this.getClass(), file);
				allPosTags = FeatureUtils.readList(is);
			} else if (languageCode.equalsIgnoreCase("de")) {
				String file = "pos_tags/stts_pos_tags.txt";
				InputStream is = FeatureUtils.getSharedResourceAsStream(this.getClass(), file);
				allPosTags = FeatureUtils.readList(is);
			}
		} catch (Exception e) {
			e.printStackTrace();
			System.out.println("An error occurred while reading the tagset file");
		}
		Collection<POS> poses = JCasUtil.select(jcas, POS.class);
		// Create a map to store lists of TTR values for each POS
		Map<String, List<Double>> posTTRMap = new HashMap<>();

		posTTRMap = findPOSWindows(poses.stream().collect(Collectors.toList()),
				allPosTags.stream().collect(Collectors.toList()), nrOfPOSInstance);
		Map<String, double[]> statisticsMap = FeatureUtils.calculateAverageAndStdDev(posTTRMap);
		for (String posTag : statisticsMap.keySet()) {
			features.add(new Feature("Avg_Window_Size_For_" + nrOfPOSInstance + "_" + posTag + "s",
					statisticsMap.get(posTag)[0], FeatureType.NUMERIC));
			features.add(new Feature("StdDev_Window_Size_For_" + nrOfPOSInstance + "_" + posTag + "s",
					statisticsMap.get(posTag)[1], FeatureType.NUMERIC));
		}
		return features;
	}

	// Function to find windows containing a specified number of POS instances
	public static Map<String, List<Double>> findPOSWindows(List<POS> poses, List<String> allPosTags,
			int nrOfPOSInstance) {
		Map<String, List<Double>> posTagStats = new HashMap<>();

		for (String posTag : allPosTags) {
			List<Double> windowSizes = new ArrayList<>();

			for (int i = 0; i < poses.size(); i++) {
				int count = 0;
				for (int j = i; j < poses.size(); j++) {
					if (poses.get(j).getPosValue().equalsIgnoreCase(posTag)) {
						count++;
					}
					if (count == nrOfPOSInstance) {
						windowSizes.add((double) (j - i + 1));
						break;
					}
				}
			}

			posTagStats.put(posTag, windowSizes);
		}

		return posTagStats;
	}

	@Override
	public String getPublicName() {
		return "POSFilter";
	}
}
