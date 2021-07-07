package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.io.FileUtils;
import org.apache.uima.UimaContext;
import org.apache.uima.analysis_engine.AnalysisEngineProcessException;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma;

/**
 * Counts the appearance of the specified connectives, checks if they appear at
 * first position of a S in a penntree constituent
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token", 
		"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma"})
public class ConnectivesAnnotator
	extends JCasAnnotator_ImplBase
{

	public static final String PARAM_CONNECTIVES_FILE_PATH = "connectivesFilePath";
    @ConfigurationParameter(name = PARAM_CONNECTIVES_FILE_PATH, mandatory = true)
    private String connectivesFilePath;

	private Set<String> connectives;

    public void initialize(UimaContext context)
        throws ResourceInitializationException
    {
        super.initialize(context);

		try {
			connectives = getConnectives(connectivesFilePath);
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
    }

	private Set<String> getConnectives(String connectivesFile) throws IOException {
		
		Set<String> connectives = new HashSet<String>();
		for (String line : FileUtils.readLines(new File(connectivesFile), "UTF-8")) {
			connectives.add(line);
		}
		return connectives;
	}

	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{

		for (Lemma lemma : JCasUtil.select(jcas, Lemma.class)) {
			if (connectives.contains(lemma.getValue().toLowerCase())) {
				Structure s = new Structure(jcas, lemma.getBegin(), lemma.getEnd());
				s.setName("ConnectivesDe");
				s.addToIndexes();
			}
		}
	}
}