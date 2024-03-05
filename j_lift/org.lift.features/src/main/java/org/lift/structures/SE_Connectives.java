package org.lift.structures;

import static org.lift.util.ResourceUtils.getSharedResourceAsStream;

import java.io.InputStream;

import org.apache.uima.UimaContext;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * annotates where the connectives specified by the provided list appear in the document
 */
@TypeCapability(inputs = {"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class SE_Connectives
	extends ListBasedAnnotator_ImplBase
{

	public static final String PARAM_USE_LEMMAS = "useLemmas";
    @ConfigurationParameter(name = PARAM_USE_LEMMAS, mandatory = true, defaultValue = "false")
    private boolean useLemmas;
        
    public void initialize(UimaContext context)
            throws ResourceInitializationException
    {
        super.initialize(context);

		String file = "connectives/connectives" + "_" + language + ".txt";
		InputStream is = getSharedResourceAsStream(this.getClass(), file);
		listSet = readList(is);			
    }
    
	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{

		if (useLemmas) {
			for (Lemma lemma : JCasUtil.select(jcas, Lemma.class)) {
				if (listSet.contains(lemma.getValue())) {
					Structure s = new Structure(jcas, lemma.getBegin(), lemma.getEnd());
					s.setName(getStructureName());
					s.addToIndexes();
				}
			}	
		}
		else {
			for (Token token : JCasUtil.select(jcas, Token.class)) {
				if (listSet.contains(token.getCoveredText())) {
					Structure s = new Structure(jcas, token.getBegin(), token.getEnd());
					s.setName(getStructureName());
					s.addToIndexes();
				}
			}			
		}
	}

	@Override
	public String getPublicStructureName() {
		return "Connectives";
	}
}