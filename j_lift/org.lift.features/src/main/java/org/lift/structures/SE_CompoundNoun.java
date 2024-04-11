package org.lift.structures;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.StructureExtractor;
import org.lift.type.Structure;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Compound;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * annotate compound nouns as structures,
 * currently only implemented for German 
 * the model excels in detecting compound nouns composed of nouns and nouns.
 * @author Viet Phe
 */
public class SE_CompoundNoun extends StructureExtractor {

	@Override
	public String getPublicStructureName() {
		return "CompoundNoun";
	}

	@Override
	public void process(JCas aJCas) throws AnalysisEngineProcessException {
		// a list to save all nouns
		List<Integer> nomens = new ArrayList<>();
		for (Token token : JCasUtil.select(aJCas, Token.class)) {
			if (token.getPos().getCoarseValue() != null && token.getPos().getCoarseValue().equals("NOUN"))
			nomens.add(token.getBegin());
		}
		Collection<Compound> compounds = JCasUtil.select(aJCas, Compound.class);
		for (Compound compound : compounds) {
			if (nomens.contains(compound.getBegin())){
				Structure s = new Structure(aJCas, compound.getBegin(), compound.getEnd());
				s.setName(getPublicStructureName());
				s.addToIndexes();
			}
				
		}
	}
}