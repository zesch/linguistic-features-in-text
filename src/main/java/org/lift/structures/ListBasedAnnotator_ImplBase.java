package org.lift.structures;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Set;

import org.apache.commons.io.FileUtils;
import org.apache.uima.UimaContext;
import org.apache.uima.fit.component.JCasAnnotator_ImplBase;
import org.apache.uima.fit.descriptor.ConfigurationParameter;
import org.apache.uima.resource.ResourceInitializationException;

public abstract class ListBasedAnnotator_ImplBase 
	extends JCasAnnotator_ImplBase
{

	public static final String PARAM_LIST_FILE_PATH = "listFilePath";
    @ConfigurationParameter(name = PARAM_LIST_FILE_PATH, mandatory = false, defaultValue = "")
    private String listFilePath;
    
    // TODO shall we have a default here?
	public static final String PARAM_LANGUAGE = "language";
    @ConfigurationParameter(name = PARAM_LANGUAGE, mandatory = false, defaultValue = "de")
    private String language;
    
    protected Set<String> listSet;

    public void initialize(UimaContext context)
        throws ResourceInitializationException
    {
        super.initialize(context);

		try {
			// if list file is not set, try to load default for language
			if (listFilePath == "" || listFilePath == null) {
				Path path = Paths.get("src/main/resources", "connectives", "connectives" + "_" + language + ".txt");
				System.out.println(path.toString());
				if (Files.notExists(path)) {
					throw new ResourceInitializationException(new Throwable("Cannot initialize annotator for " + language));
				}
				listFilePath = path.toString();
			}
			
			listSet = readList(listFilePath);
			
		} catch (IOException e) {
			throw new ResourceInitializationException(e);
		}
    }
    
	private Set<String> readList(String listFilePath) throws IOException {
		
		Set<String> listSet = new HashSet<String>();
		for (String line : FileUtils.readLines(new File(listFilePath), "UTF-8")) {
			listSet.add(line);
		}
		return listSet;
	}
}