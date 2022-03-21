
package org.lift.higherorder.genuine;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;

/**
 * Extracts the ratio of characters per sentence.
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence"})
public class FE_AvgNrOfCharsPerSentence 
	extends FeatureExtractor_ImplBase
{

	public static final String AVG_NR_OF_CHARS_SENTENCE = "avgNumCharsPerSentence";
    public static final String STANDARD_DEVIATION_OF_CHARS_PER_SENTENCE = "standardDevCharsPerSentence";
    
    
	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureList = new HashSet<Feature>();
		Collection<Sentence> sentences = JCasUtil.select(jcas, Sentence.class);
		
		double nrOfSentences = sentences.size();
        double sumOfChars = 0;
        for(Sentence s:sentences){
        	double sentenceLength = s.getEnd()-s.getBegin();
        	sumOfChars+=sentenceLength;
        } 
        double avgSize = sumOfChars / nrOfSentences;
        
        double varianceSum = 0;
        for(Sentence s:sentences){
        	double sentenceLength = s.getEnd()-s.getBegin();
        	double deviation = sentenceLength-avgSize;
        	varianceSum+=Math.pow(deviation,2);
        }
        double stndDeviation = Math.sqrt(varianceSum/nrOfSentences);
        
        featureList.add(new Feature(AVG_NR_OF_CHARS_SENTENCE, avgSize, FeatureType.NUMERIC));
        featureList.add(new Feature(STANDARD_DEVIATION_OF_CHARS_PER_SENTENCE, stndDeviation, FeatureType.NUMERIC));
        
        return featureList;
	}


	@Override
	public String getPublicName() {
		return "AvgNrOfCharsPerSentence";
	}
}
