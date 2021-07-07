package org.lift.structures;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma;

/**
 * counts the appearance of the specified connectives
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma"})
public class ConnectivesAnnotator
	extends ListBasedAnnotator_ImplBase
{

	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{

		for (Lemma lemma : JCasUtil.select(jcas, Lemma.class)) {
			if (listSet.contains(lemma.getValue().toLowerCase())) {
				Structure s = new Structure(jcas, lemma.getBegin(), lemma.getEnd());
				s.setName("Connectives");
				s.addToIndexes();
			}
		}
	}
}