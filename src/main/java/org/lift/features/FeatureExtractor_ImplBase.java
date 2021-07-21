package org.lift.features;

import org.lift.api.FeatureExtractor;


public abstract class FeatureExtractor_ImplBase 
	implements FeatureExtractor
{

	protected String publicName;
	protected String internalName;
	
	public FeatureExtractor_ImplBase(String publicName, String internalName) {
		this.publicName = publicName;
		this.internalName = cleanName(internalName);
	}

	public String getPublicName() {
		return publicName;
	}

	public String getInternalName() {
		return internalName;
	}	

	private String cleanName(String name) {
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
}