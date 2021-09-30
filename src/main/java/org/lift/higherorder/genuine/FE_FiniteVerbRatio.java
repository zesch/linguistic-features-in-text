package org.lift.higherorder.genuine;

import java.util.HashSet;
import java.util.Set;

import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

/**
 * Extracts the ratio of finite verbs per verbs. The forwarded JCas has to be tagged with the tagset "stts" for document language german,
 * and tagset "ptp" for document language english. The default language is english.
 */
public class FE_FiniteVerbRatio extends FeatureExtractor_ImplBase {

	public static final String FN_FINITE_VERB_RATIO = "FiniteVerbRatio";

	public FE_FiniteVerbRatio() {
		super("FiniteVerbRatio", FE_FiniteVerbRatio.class.getName());
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {

		String tagset = "ptb";
		if (jcas.getDocumentLanguage() != null) {
			String lang = jcas.getDocumentLanguage();
			if (lang.equals("de")) {
				tagset = "stts";
			} else if (lang.equals("en")) {
				tagset = "ptb";
			}
		} else {
			System.out.println("No Tagset or language specified! Assuming PennTreebank Tagset now!");
		}

		Set<String> finiteVerbTags = new HashSet<String>();
		if (tagset.equals("stts")) {
			finiteVerbTags.add("VAFIN");
			finiteVerbTags.add("VMFIN");
			finiteVerbTags.add("VVFIN");

		} else if (tagset.equals("ptb")) {
			finiteVerbTags.add("VBD");
			finiteVerbTags.add("VBP");
			finiteVerbTags.add("VBZ");
		}

		int numberOfVerbs = 0;
		int numberOfFiniteVerbs = 0;
		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			if (pos.getCoarseValue().equals("VERB")) {
				numberOfVerbs++;
				if (finiteVerbTags.contains(pos.getPosValue())) {
					numberOfFiniteVerbs++;
				}
			}
		}

		double finiteRatio = (1.0 * numberOfFiniteVerbs) / numberOfVerbs;

		Set<Feature> features = new HashSet<Feature>();
		features.add(new Feature(FN_FINITE_VERB_RATIO, finiteRatio, FeatureType.NUMERIC));

		return features;

	}

}
