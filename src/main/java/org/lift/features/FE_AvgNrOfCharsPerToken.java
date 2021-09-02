package org.lift.features;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Extracts the average number of characters per sentence
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token",
		"de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS" })
public class FE_AvgNrOfCharsPerToken extends FeatureExtractor_ImplBase {

	public static final String AVG_NR_OF_CHARS_PER_TOKEN = "avgNumCharsToken";
    public static final String STANDARD_DEVIATION_OF_CHARS_PER_TOKEN = "standardDevCharsPerToken";
    
	public FE_AvgNrOfCharsPerToken() {
		super("AvgNrOfCharsPerToken", FE_AvgNrOfCharsPerToken.class.getName());
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureList = new HashSet<Feature>();

		Collection<Token> tokens = JCasUtil.select(jcas, Token.class);
		double numOfTokens = 0;
		double tempSize = 0;

		for (Token token : tokens) {
			if (token.getPos() == null) {
				System.err.println("No POS for token " + token.getCoveredText() + " in essay "
						+ jcas.getDocumentText().substring(0, 100));
			} else {
				if (!token.getPos().getPosValue().equals("$.") && !token.getPos().getPosValue().equals(".")) {
					tempSize += token.getCoveredText().length();
					numOfTokens++;
				}
			}
		}
		double avgSize = tempSize / numOfTokens;

		tempSize = 0;
		for (Token token : tokens) {
			if (token.getPos() == null) {
				System.err.println("No POS for token " + token.getCoveredText() + " in essay "
						+ jcas.getDocumentText().substring(0, 100));
			} else {
				if (!token.getPos().getPosValue().equals("$.") && !token.getPos().getPosValue().equals(".")) {
					double tempAdd = token.getCoveredText().length() - avgSize;
					tempSize += Math.pow(tempAdd, 2);
				}
			}
		}

		double stndDeviation = Math.sqrt(tempSize / numOfTokens);
		featureList.add(new Feature(AVG_NR_OF_CHARS_PER_TOKEN, avgSize, FeatureType.NUMERIC));
		featureList.add(new Feature(STANDARD_DEVIATION_OF_CHARS_PER_TOKEN, stndDeviation, FeatureType.NUMERIC));
		return featureList;

	}

}
