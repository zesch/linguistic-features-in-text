package org.lift.higherorder.genuine;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.frequency.util.FrequencyDistribution;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.features.util.NGramUtils;

import com.googlecode.jweb1t.JWeb1TSearcher;

public class FE_TrigramCounter 
	extends FeatureExtractor_ImplBase
{
	
	String web1tFilePath;

	public FE_TrigramCounter(String web1FilePath) {
		this.web1tFilePath = web1FilePath;
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		File web1tFile = new File(System.getenv("DKPRO_HOME") + web1tFilePath);
		JWeb1TSearcher searcher = null;
		try {
			searcher = new JWeb1TSearcher(web1tFile, 3, 3);
		} catch (IOException e) {
			throw new LiftFeatureExtrationException(e.getMessage());
		}
		
		double min = Integer.MAX_VALUE;
		double max = Integer.MIN_VALUE;
		double average = 0;
		double count;
		
		FrequencyDistribution<String> freqDist = NGramUtils.getDocumentNgrams(jcas, false, false, 3, 3, new HashSet<String>(), Token.class);
		
		for(String key : freqDist.getKeys()) {
			key = key.replaceAll("_", " ");
			try {
				count = searcher.getFrequency(key);
				
				if(count == 0) {
					System.out.println("not found in web1t: " + key);
				}
			} catch (IOException e) {
				count = 0;
				e.printStackTrace();
			}
			
			if(min > count) {
				min = count;
			}
			
			if(max < count) {
				max = count;
			}
			
			average += count;
		}		
		double averageTrigramProb = average / freqDist.getKeys().size();

		Set<Feature> features = new HashSet<>();
		features.add(new Feature("MAXIMUM_TRIGRAM_COUNT", max, FeatureType.NUMERIC));
		features.add(new Feature("MINIMAL_TRIGRAM_COUNT", min, FeatureType.NUMERIC));
		features.add(new Feature("AVERAGE_TRIGRAM_COUNT", averageTrigramProb, FeatureType.NUMERIC));
		
		return features;
	}

	@Override
	public String getPublicName() {
		return "TrigramProbability";
	}
}
