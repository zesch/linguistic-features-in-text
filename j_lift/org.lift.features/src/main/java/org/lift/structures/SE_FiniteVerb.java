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

import de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS;

/**
 * Annotates finite verbs based on a list of POS tags
 */
@TypeCapability(inputs = {
		"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.POS" 
})
public class SE_FiniteVerb
	extends ListBasedAnnotator_ImplBase
{

	public static final String PARAM_LANGUAGE = "lang";
	@ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = true)
	private String language;
	
	// TODO add documentation which tagsets are supported ...
	public static final String PARAM_TAGSET = "tagset";
	@ConfigurationParameter(name = PARAM_TAGSET, mandatory = false)
	private String tagset;

	public void initialize(UimaContext context) 
			throws ResourceInitializationException
	{
		super.initialize(context);

		if (tagset == null) {

			//TODO: Read from config tagset_mappings
			if (language.equals("en")) {
				tagset = "ptb";
			} 
			else if (language.equals("de")) {
				tagset = "stts";
			} 
			else {
				// TODO add better explanation what the user should do ...
				throw new ResourceInitializationException( new Throwable("No default tagset for language " + language));
			}
		}

		String file = "finite_verb_postags/finite_verb_postags" + "_" + language + "_" + tagset + ".txt";
		InputStream is = getSharedResourceAsStream(this.getClass(), file);
		listSet = readList(is);
	}

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {

		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			if (listSet.contains(pos.getPosValue())) {
				Structure s = new Structure(jcas, pos.getBegin(), pos.getEnd());
				s.setName(getStructureName());
				s.addToIndexes();
			}
		}
	}

	@Override
	public String getPublicStructureName() {
		return "FiniteVerb";
	}
}