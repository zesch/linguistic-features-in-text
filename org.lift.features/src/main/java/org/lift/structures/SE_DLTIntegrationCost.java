package org.lift.structures;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;

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
 * 
 */
@TypeCapability(inputs = { "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token" })
public class SE_DLTIntegrationCost extends ListBasedAnnotator_ImplBase {

	public static final String PARAM_LANGUAGE = "lang";
	@ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = true)
	private String language;
	//TODO anpassen auf dependency 
	public static final String PARAM_DEP_REL_LABELS = "dependencyRelationLabels";
	@ConfigurationParameter(name = PARAM_DEP_REL_LABELS, mandatory = false, defaultValue = "dummy")
	private String depRelLabels;
	private String listConfig;
	// TODO less hacky way of circumventing ListBasedAnnotator_ImplBase's assumption that only one list matters
	private String listFilePathAdv;
	private String listFilePathObj;
	private Set<String> listSetObj;
	private Set<String> listSetAdv;

	private final String NAME = "DLTIntegrationCost";

	public void initialize(UimaContext context) throws ResourceInitializationException {
		super.initialize(context);

		//TODO: Read from config deprel_mappings
		// probably useless switch, but it allows to work with non-ud
		switch (language) {
		case "en":
		case "de":
		default:
			// allows to make language specific resource name for non UD cases, see SE_FiniteVerb 
			depRelLabels = "ud";
			listConfig = "_" + depRelLabels; 
			break;
		}

		try {
			// read object dependency labels
			Path pathObj = Paths.get("src/main/resources", "ud_dependency_relation",
					"object_dependency_relation" + listConfig + ".txt");
			if (Files.notExists(pathObj)) {
				throw new ResourceInitializationException(new Throwable(
						"Cannot load list of object dependency labels from path " + pathObj.toString()));
			}
			listFilePathObj = pathObj.toString();
			listSetObj = readList(listFilePathObj);

			// read sentence adverb dependency labels
			Path pathAdv= Paths.get("src/main/resources", "ud_dependency_relation",
					"sentence_adverb_dependency_relation" + listConfig + ".txt");
			if (Files.notExists(pathObj)) {
				throw new ResourceInitializationException(new Throwable(
						"Cannot load list of object dependency labels from path " + pathObj.toString()));
			}
			listFilePathObj = pathObj.toString();
			listSetObj = readList(listFilePathObj);

		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
	}

	@Override
	public void process(JCas jcas) throws AnalysisEngineProcessException {

		for (POS pos : JCasUtil.select(jcas, POS.class)) {
			if (listSet.contains(pos.getPosValue())) {
				Structure s = new Structure(jcas, pos.getBegin(), pos.getEnd());
				s.setName(NAME);
				s.addToIndexes();
			}
		}

	}
}