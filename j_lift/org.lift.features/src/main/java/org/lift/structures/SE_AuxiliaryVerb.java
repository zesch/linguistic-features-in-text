package org.lift.structures;

import static org.lift.util.ResourceUtils.getSharedResourceAsStream;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.uima.UimaContext;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * Annotates auxiliary verbs based on a list of possible auxiliary verbs
 * 
 * @author vietphe
 */
@TypeCapability(inputs = {
		"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.POS" 
})
public class SE_AuxiliaryVerb
	extends ListBasedAnnotator_ImplBase
{

	public static final String PARAM_LANGUAGE = "lang";
	@ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = true)
	private String language;
	
	public void initialize(UimaContext context) 
			throws ResourceInitializationException
	{
		super.initialize(context);
		String file = "auxiliary_verbs/auxiliary_verbs_" + language + ".txt";
		InputStream is = getSharedResourceAsStream(this.getClass(), file);
		listSet = readList(is);	
	}

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {

		for (Token t : JCasUtil.select(jcas, Token.class)) {
			if (listSet.contains(t.getCoveredText().toLowerCase())) {
				Structure s = new Structure(jcas, t.getBegin(), t.getEnd());
				s.setName(getPublicStructureName());
				s.addToIndexes();
			}
		}
	}

	@Override
	public String getPublicStructureName() {
		return "AuxiliaryVerb";
	}
}