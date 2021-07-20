package org.lift.structures;

import java.io.IOException;
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
    
    private final String NAME = "Connectives";
    
    public void initialize(UimaContext context)
            throws ResourceInitializationException
    {
        super.initialize(context);

		try {
			// if list file is not set, try to load default for language
			if (listFilePath == "" || listFilePath == null) {
				Path path = Paths.get("src/main/resources", "connectives", "connectives" + "_" + language + ".txt");
				if (Files.notExists(path)) {
					throw new ResourceInitializationException(new Throwable("Cannot load list of connectives for language: " + language));
				}
				listFilePath = path.toString();
			}
			
			listSet = readList(listFilePath);
			
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
    }
    
	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{

		if (useLemmas) {
			for (Lemma lemma : JCasUtil.select(jcas, Lemma.class)) {
				if (listSet.contains(lemma.getValue())) {
					Structure s = new Structure(jcas, lemma.getBegin(), lemma.getEnd());
					s.setName(NAME);
					s.addToIndexes();
				}
			}	
		}
		else {
			for (Token token : JCasUtil.select(jcas, Token.class)) {
				if (listSet.contains(token.getCoveredText())) {
					Structure s = new Structure(jcas, token.getBegin(), token.getEnd());
					s.setName(NAME);
					s.addToIndexes();
				}
			}			
		}
	}
}