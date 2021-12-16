package org.lift.preprocessing;

import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;

import de.tudarmstadt.ukp.dkpro.core.api.anomaly.type.GrammarAnomaly;
import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;
import de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.PennTree;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.chunk.Chunk;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.constituent.Constituent;
import de.tudarmstadt.ukp.dkpro.core.api.syntax.type.dependency.Dependency;

public class Analyzer extends JCasAnnotator_ImplBase {


	@Override
	public void process(JCas aJCas) throws AnalysisEngineProcessException {
		String id = "no Id";
		if (JCasUtil.exists(aJCas, DocumentMetaData.class)){
			DocumentMetaData meta = JCasUtil.selectSingle(aJCas, DocumentMetaData.class);
			id = meta.getDocumentId();
		}
		System.out.println("Analyzing text "+id+": "
				+ JCasUtil.select(aJCas, Sentence.class).size()+ " sentences, "
				+ JCasUtil.select(aJCas, Token.class).size()+ " tokens, "
				+ JCasUtil.select(aJCas, Lemma.class).size()+ " lemmata, "
				+ JCasUtil.select(aJCas, GrammarAnomaly.class).size()+ " grammar anomalies, "
				+ JCasUtil.select(aJCas, Chunk.class).size()+ " chunks, "
				+ JCasUtil.select(aJCas, NamedEntity.class).size()+ " NEs, "
				+ JCasUtil.select(aJCas, PennTree.class).size()+ " trees, "
				+ JCasUtil.select(aJCas, Constituent.class).size()+ " constituents, "
				+ JCasUtil.select(aJCas, Dependency.class).size()+ " dependencies."				
				);
	}


}
