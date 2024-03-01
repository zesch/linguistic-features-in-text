package org.lift.util;

import java.io.InputStream;
import java.net.URISyntaxException;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.uima.resource.ResourceInitializationException;
import org.lift.api.StructureExtractor;

public class ResourceUtils {

	public static InputStream getSharedResourceAsStream(Class<? extends StructureExtractor> cls, String path) 
			throws ResourceInitializationException 
	{
//		// make sure path starts with "/"
//		if (!path.startsWith("/")) {
//			path = "/" + path;
//		}
		
		// make sure path does not start with "/"
		if (path.startsWith("/")) {
			path = path.substring(1);
		}
		System.out.println(path);
		
		InputStream is = cls.getClassLoader().getResourceAsStream(path);
		if (is == null) {
			throw new ResourceInitializationException(
					new Throwable("Cannot load resource from: " + path)
			);
		}

		return is;
	}
	
	public static Path getSharedResourceAsPath(Class<? extends StructureExtractor> cls, String path) 
			throws ResourceInitializationException 
	{
		// make sure path does not start with "/"
		if (path.startsWith("/")) {
			path = path.substring(1);
		}
		System.out.println(path);
		
		URL url = cls.getClassLoader().getResource(path);
		Path file;
		try {
			file = Paths.get(url.toURI());
		} catch (URISyntaxException e) {
			throw new ResourceInitializationException(
					new Throwable("Cannot load resource from: " + path)
			);
		}

		return file;
	}

}
