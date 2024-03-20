package org.lift.higherorder.genuine;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.morph.MorphologicalFeatures;


/**
 * Which proportion of the finite verbs belongs to which person (1st/2nd/3rd
 * person Sg/Pl)
 * currently only for German
 * 
 * @author vietphe
 */
public class FE_MorphologicalFeatures extends FeatureExtractor_ImplBase {

	public static final String FINITE_VERB_1_PERSON_SG_RATIO = "finiteVerb1PersonSingularRatio";
	public static final String FINITE_VERB_2_PERSON_SG_RATIO = "finiteVerb2PersonSingularRatio";
	public static final String FINITE_VERB_3_PERSON_SG_RATIO = "finiteVerb3PersonSingularRatio";
	public static final String FINITE_VERB_1_PERSON_PL_RATIO = "finiteVerb1PersonPluralRatio";
	public static final String FINITE_VERB_2_PERSON_PL_RATIO = "finiteVerb2PersonPluralRatio";
	public static final String FINITE_VERB_3_PERSON_PL_RATIO = "finiteVerb3PersonPluralRatio";

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		Set<Feature> featureList = new HashSet<Feature>();
		Collection<MorphologicalFeatures> morphologicalFeatures = JCasUtil.select(jcas, MorphologicalFeatures.class);

		int nrOfFiniteVerb1PersonSg = 0;
		int nrOfFiniteVerb2PersonSg = 0;
		int nrOfFiniteVerb3PersonSg = 0;
		int nrOfFiniteVerb1PersonPl = 0;
		int nrOfFiniteVerb2PersonPl = 0;
		int nrOfFiniteVerb3PersonPl = 0;
		int nrOfOtherFiniteVerb = 0;
		for (MorphologicalFeatures m : morphologicalFeatures) {		
			
			String value = m.getValue(); // value form: "number=pl|person=1|tense=pres|mood=ind"
			// extract morphological features
			if (value.contains("tense") && value.contains("mood")) {
				String[] detailsValue = value.split("\\|");
				String number = detailsValue[0].split("=")[1];
				String person = detailsValue[1].split("=")[1];
				if (number.equals("sg") && person.equals("1")) {
					nrOfFiniteVerb1PersonSg++;
				}else if (number.equals("sg") && person.equals("2")) {
					nrOfFiniteVerb2PersonSg++;
				}else if (number.equals("sg") && person.equals("3")) {
					nrOfFiniteVerb3PersonSg++;
				}else if (number.equals("pl") && person.equals("1")) {
					nrOfFiniteVerb1PersonPl++;
				}else if (number.equals("pl") && person.equals("2")) {
					nrOfFiniteVerb2PersonPl++;
				}else if (number.equals("pl") && person.equals("3")) {
					nrOfFiniteVerb3PersonPl++;
				}else {
					nrOfOtherFiniteVerb++;
				}
			}
		}
		int nrOfAllFiniteVerbs = nrOfFiniteVerb1PersonSg + nrOfFiniteVerb2PersonSg + nrOfFiniteVerb3PersonSg
				+ nrOfFiniteVerb1PersonPl + nrOfFiniteVerb2PersonPl 
				+ nrOfFiniteVerb3PersonPl+nrOfOtherFiniteVerb;

		featureList.add(new Feature(FINITE_VERB_1_PERSON_SG_RATIO,
				(double) nrOfFiniteVerb1PersonSg / nrOfAllFiniteVerbs, FeatureType.NUMERIC));
		featureList.add(new Feature(FINITE_VERB_2_PERSON_SG_RATIO,
				(double) nrOfFiniteVerb2PersonSg / nrOfAllFiniteVerbs, FeatureType.NUMERIC));
		featureList.add(new Feature(FINITE_VERB_3_PERSON_SG_RATIO,
				(double) nrOfFiniteVerb3PersonSg / nrOfAllFiniteVerbs, FeatureType.NUMERIC));
		featureList.add(new Feature(FINITE_VERB_1_PERSON_PL_RATIO,
				(double) nrOfFiniteVerb1PersonPl / nrOfAllFiniteVerbs, FeatureType.NUMERIC));
		featureList.add(new Feature(FINITE_VERB_2_PERSON_PL_RATIO,
				(double) nrOfFiniteVerb2PersonPl / nrOfAllFiniteVerbs, FeatureType.NUMERIC));
		featureList.add(new Feature(FINITE_VERB_3_PERSON_PL_RATIO,
				(double) nrOfFiniteVerb3PersonPl / nrOfAllFiniteVerbs, FeatureType.NUMERIC));

		return featureList;

	}

	@Override
	public String getPublicName() {
		return "MorphologicalFeatures";
	}

}
