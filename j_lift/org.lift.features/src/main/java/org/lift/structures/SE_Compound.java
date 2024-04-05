package org.lift.structures;

import java.util.Collection;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.api.StructureExtractor;
import org.lift.type.Structure;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Compound;

/**
 * annotate compounds as structures,
 * currently only implemented for German
 * @author Viet Phe
 */
public class SE_Compound extends StructureExtractor {

	@Override
	public String getPublicStructureName() {
		return "Compound";
	}

	@Override
	public void process(JCas aJCas) throws AnalysisEngineProcessException {

		Collection<Compound> compounds = JCasUtil.select(aJCas, Compound.class);
		for (Compound compound : compounds) {
			Structure s = new Structure(aJCas, compound.getBegin(), compound.getEnd());
			s.setName(getPublicStructureName());
			s.addToIndexes();
			System.out.println(compound.getCoveredText());
		}
	}
}