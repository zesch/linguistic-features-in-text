package org.lift.structures;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * counts the appearance of the specified connectives
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class SE_Connectives
	extends ListBasedAnnotator_ImplBase
{

	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{
		// TOOD are there languages where we need to use lemmas?
		for (Token token : JCasUtil.select(jcas, Token.class)) {
			if (listSet.contains(token.getCoveredText())) {
				Structure s = new Structure(jcas, token.getBegin(), token.getEnd());
				s.setName("Connectives");
				s.addToIndexes();
			}
		}
	}
}