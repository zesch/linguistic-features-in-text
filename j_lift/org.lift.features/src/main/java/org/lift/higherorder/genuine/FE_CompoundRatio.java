package org.lift.higherorder.genuine;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * extract compound ratio, normalised by number of tokens and nouns
 * currently only implemented for German
 * @author Viet Phe
 */
public class FE_CompoundRatio extends FeatureExtractor_ImplBase {

	public static final String AVG_NR_OF_COMPOUND_PER_NR_OF_TOKEN = "avgNumCompoundPerNumToken";
	public static final String AVG_NR_OF_COMPOUND_PER_NR_OF_NOUN = "avgNumCompoundPerNumNoun";

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {

		Set<Feature> features = new HashSet<Feature>();
		int tokenSize = JCasUtil.select(jcas, Token.class).size();
		int nrOfCompound = 0;
		int nrOfNoun = 0;
		for (Structure s : JCasUtil.select(jcas, Structure.class)) {
			if (s.getName().equals("Compound")) {
				nrOfCompound++;
			}
		}
		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			if (pos.getCoarseValue().equals("NOUN")) {
				nrOfNoun++;
			}
		}
		features.add(new Feature(AVG_NR_OF_COMPOUND_PER_NR_OF_TOKEN, (double) nrOfCompound / tokenSize,
				FeatureType.NUMERIC));
		features.add(
				new Feature(AVG_NR_OF_COMPOUND_PER_NR_OF_NOUN, (double) nrOfCompound / nrOfNoun, FeatureType.NUMERIC));
		return features;
	}

	@Override
	public String getPublicName() {
		return "CompoundRatio";
	}
}