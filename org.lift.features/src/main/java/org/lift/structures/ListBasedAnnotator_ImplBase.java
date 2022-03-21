package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.io.FileUtils;
import org.apache.uima.UimaContext;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.resource.ResourceInitializationException;
import org.lift.api.StructureExtractor;

public abstract class ListBasedAnnotator_ImplBase 
	extends StructureExtractor
{

	// we keep that parameter optional, as subclasses might implement loading of default lists
	public static final String PARAM_LIST_FILE_PATH = "listFilePath";
    @ConfigurationParameter(name = PARAM_LIST_FILE_PATH, mandatory = false)
    protected String listFilePath;
    
    // TODO shall we have a default here?
	public static final String PARAM_LANGUAGE = "language";
    @ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = false)
    protected String language;
    
    protected Set<String> listSet;

    public void initialize(UimaContext context)
        throws ResourceInitializationException
    {
        super.initialize(context);

		try {
			if (listFilePath != "" && listFilePath != null) {
				listSet = readList(listFilePath);
			}
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
    }
    
	static Set<String> readList(String listFilePath) throws IOException {
		
		Set<String> listSet = new HashSet<String>();
		for (String line : FileUtils.readLines(new File(listFilePath), "UTF-8")) {
			listSet.add(line);
		}
		return listSet;
	}
}