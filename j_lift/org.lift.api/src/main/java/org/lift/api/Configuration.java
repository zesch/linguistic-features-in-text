package org.lift.api;

public class Configuration {

	/**
	 * Shortcut for supported languages. Maps to 2 letter ISO language codes
	 */
	public enum Language {
	    English("en"),
	    German("de"),
	    Unknwon("en");	// we will use default configuration and hope for the best ...

	    public final String code;

	    private Language(String code) {
	        this.code = code;
	    }
	}
}
