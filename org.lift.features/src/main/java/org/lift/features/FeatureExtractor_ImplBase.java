package org.lift.features;

import org.lift.api.FeatureExtractor;
import org.lift.api.FeatureExtractorAndAnnotator;

public abstract class FeatureExtractor_ImplBase 
	extends FeatureExtractorAndAnnotator
{

	protected String publicName;
	protected String internalName;
	
	protected String cleanName(String name) {
	    StringBuilder sb = new StringBuilder();
	    if(!Character.isJavaIdentifierStart(name.charAt(0))) {
	        sb.append("_");
	    }
	    for (char c : name.toCharArray()) {
	        if(!Character.isJavaIdentifierPart(c)) {
	            sb.append("_");
	        } else {
	            sb.append(c);
	        }
	    }
	    return sb.toString();
	}
	
	@Override
	public String getInternalName() {
		return cleanName(getClass().getName());
	}
}