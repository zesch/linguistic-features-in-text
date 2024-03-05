package org.lift.structures;

import static org.lift.util.ResourceUtils.getSharedResourceAsPath;

import java.nio.file.Path;

import org.apache.uima.UimaContext;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.fit.descriptor.TypeCapability;
import org.apache.uima.resource.ResourceInitializationException;

/**
 * annotates where the connectives specified by the provided list appear in the document
 */
@TypeCapability(inputs = {"de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token"})
public class SE_Nominalizations
	extends SEL_RutaScript
{
	
	public static final String PARAM_LANGUAGE = "lang";
	@ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = true)
	private String language;

	public void initialize(UimaContext context) 
			throws ResourceInitializationException
	{
		super.initialize(context);

		if (rutaScript == null) {

			if (language.equals("de")) {
				String file = "/nominalizations/nominalization_de.ruta";
				Path path = getSharedResourceAsPath(this.getClass(), file);
				rutaScript = path.toAbsolutePath().toString();
				structureName = getPublicStructureName();
			} 
			else {
				throw new ResourceInitializationException(
						new Throwable("No default nominalization file for language " + language)
				);
			}
		}
	}

	@Override
	public String getPublicStructureName() {
		return "Nominalizations";
	}
}