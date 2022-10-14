package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
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
import org.lift.type.Frequency;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma;
import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

/**
 * annotates for each token its frequency according to a provided dictionary
 */
@TypeCapability(inputs = {"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class SE_Frequencies
extends JCasAnnotator_ImplBase
{

	public static final String PARAM_LIST_FILE_PATH = "mapFilePath";
	@ConfigurationParameter(name = PARAM_LIST_FILE_PATH, mandatory = true)
	protected String mapFilePath;

	public static final String PARAM_USE_LEMMAS = "useLemmas";
	@ConfigurationParameter(name = PARAM_USE_LEMMAS, mandatory = true, defaultValue = "false")
	private boolean useLemmas;

	private final String NAME = "Frequencies";

	private final String sep = "\t";
	
	protected Map<String, Double> dict;
	
	public void initialize(UimaContext context)
			throws ResourceInitializationException
	{
		super.initialize(context);

		try {
			// if list file is not set, try to load default for language
			if (mapFilePath == "" || mapFilePath == null) {
				Path path = Paths.get(mapFilePath);
				if (Files.notExists(path)) {
					throw new ResourceInitializationException(new Throwable("Cannot load frequency dictionary"));
				}
				mapFilePath = path.toString();
			}

			dict = readMapping(mapFilePath);

		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
	}

	protected Map<String, Double> readMapping(String listFilePath) throws IOException {

		Map<String, Double> map = new HashMap<String, Double>();
		for (String line : FileUtils.readLines(new File(listFilePath), "UTF-8")) {
			String[] parts = line.split("\t");
			map.put(parts[0], Double.parseDouble(parts[1]));
		}
		return map;
	}

	@Override
	public void process(JCas jcas) 
			throws AnalysisEngineProcessException
	{

		if (useLemmas) {
			for (Lemma lemma : JCasUtil.select(jcas, Lemma.class)) {
				if (dict.containsKey(lemma.getValue())) {
					Frequency f = new Frequency(jcas, lemma.getBegin(), lemma.getEnd());
					f.setValue(dict.get(lemma.getValue()));
					f.addToIndexes();
				}
			}	
		}
		else {
			for (Token token : JCasUtil.select(jcas, Token.class)) {
				if (dict.containsKey(token.getCoveredText())) {
					Frequency f = new Frequency(jcas, token.getBegin(), token.getEnd());
					f.setValue(dict.get(token.getCoveredText()));
					f.addToIndexes();
				}
			}			
		}
	}
}