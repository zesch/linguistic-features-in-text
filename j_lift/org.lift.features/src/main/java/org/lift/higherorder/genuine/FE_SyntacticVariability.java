package org.lift.higherorder.genuine;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.apache.commons.lang3.StringUtils;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.api.frequency.util.FrequencyDistribution;
import org.lift.api.Feature;
import org.lift.api.FeatureType;
import org.lift.api.LiftFeatureExtrationException;
import org.lift.features.FeatureExtractor_ImplBase;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.PennTree;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.constituent.Constituent;

public class FE_SyntacticVariability 
	extends FeatureExtractor_ImplBase
{

	public static final String SYNTAX_TYPE_RATIO_POSLEVEL = "SyntaxTypeRatioPosLevel";
	public static final String SYNTAX_TYPE_RATIO_PHRASELEVEL = "SyntaxTypeRatioPhraseLevel";
	public static final String SYNTAX_TYPE_RATIO_SENTENCELEVEL = "SyntaxTypeRatioSentenceLevel";
	public static final String PAIRWISE_SYNTACTIC_SIMILARITY_PHRASELEVEL = "pairwiseSyntacticSimilarityPhraseLevel";
	public static final String PAIRWISE_SYNTACTIC_SIMILARITY_POSLEVEL = "pairwiseSyntacticSimilarityPosLevel";
	public static final String PAIRWISE_SYNTACTIC_SIMILARITY_SENTENCELEVEL = "pairwiseSyntacticSimilaritySentenceLevel";
	
	public enum Level {
		pos,
		phrase,
		sentence
	}

	@Override
	public Set<Feature> extract(JCas jcas) throws LiftFeatureExtrationException {
		FrequencyDistribution<String> fdPosLevel = new FrequencyDistribution<String>();
		FrequencyDistribution<String> fdPhraseLevel = new FrequencyDistribution<String>();
		FrequencyDistribution<String> fdSentenceLevel = new FrequencyDistribution<String>();

		double similarityPosLevel = 0;
		double similarityPhraseLevel = 0;
		double similaritySentenceLevel = 0;

		List<PennTree> trees = new ArrayList<PennTree>(JCasUtil.select(jcas, PennTree.class));

		for (int i = 0; i < trees.size(); i++) {
			fdPhraseLevel.inc(getStringRepresentation(trees.get(i), Level.phrase));
			fdPosLevel.inc(getStringRepresentation(trees.get(i), Level.pos));
			fdSentenceLevel.inc(getStringRepresentation(trees.get(i), Level.sentence));

			if (i < trees.size() - 1) {
				similarityPhraseLevel += this.compare(getStringRepresentation(trees.get(i), Level.phrase),
						getStringRepresentation(trees.get(i + 1), Level.phrase));
				similarityPosLevel += this.compare(getStringRepresentation(trees.get(i), Level.pos),
						getStringRepresentation(trees.get(i + 1), Level.pos));
				similaritySentenceLevel += this.compare(getStringRepresentation(trees.get(i), Level.sentence),
						getStringRepresentation(trees.get(i + 1), Level.sentence));
			}
		}

		if (trees.size() > 1) {
			// -1 because we count pairs (last sentence has no partner)
			similarityPhraseLevel = similarityPhraseLevel / (trees.size() - 1);
			similarityPosLevel = similarityPosLevel / (trees.size() - 1);
			similaritySentenceLevel = similaritySentenceLevel / (trees.size() - 1);
		}

		Set<Feature> featList = new HashSet<Feature>();
		featList.add(new Feature(SYNTAX_TYPE_RATIO_PHRASELEVEL, getRatio(fdPhraseLevel), FeatureType.NUMERIC));
		featList.add(new Feature(SYNTAX_TYPE_RATIO_POSLEVEL, getRatio(fdPosLevel), FeatureType.NUMERIC));
		featList.add(new Feature(SYNTAX_TYPE_RATIO_SENTENCELEVEL, getRatio(fdSentenceLevel), FeatureType.NUMERIC));
		featList.add(
				new Feature(PAIRWISE_SYNTACTIC_SIMILARITY_PHRASELEVEL, similarityPhraseLevel, FeatureType.NUMERIC));
		featList.add(new Feature(PAIRWISE_SYNTACTIC_SIMILARITY_POSLEVEL, similarityPosLevel, FeatureType.NUMERIC));
		featList.add(
				new Feature(PAIRWISE_SYNTACTIC_SIMILARITY_SENTENCELEVEL, similaritySentenceLevel, FeatureType.NUMERIC));

		return featList;
	}

	private double compare(String stringRepresentation, String stringRepresentation2) {
		if (stringRepresentation.equals(stringRepresentation2)) {
			return 1.0;
		}
		return 0;
	}

	private double getRatio(FrequencyDistribution<String> fd) {
		// Normalization on total count of words
		if (fd.getN() > 0) {
			return (double) fd.getB() / fd.getN();
		} else {
			return 0.0;
		}
	}

	private String getStringRepresentation(PennTree tree, Level level) {
		List<String> representation = new ArrayList<String>();
		if (level.equals(Level.pos)) {
			for (Token t : JCasUtil.selectCovered(Token.class, tree)) {
				representation.add(t.getPos().getPosValue());
			}
		} else if (level.equals(Level.phrase)) {
			for (Constituent c : JCasUtil.selectCovered(Constituent.class, tree)) {
				representation.add(c.getConstituentType());
			}
		} else {
			for (Constituent c : JCasUtil.selectCovered(Constituent.class, tree)) {
				if (c.getConstituentType().equals("S")) {
					representation.add("S");
				}
			}
		}
		return StringUtils.join(representation, " ");
	}

	@Override
	public String getPublicName() {
		return "SyntacticVariability";
	}

}
