package org.lift.higherorder.genuine;

public enum ReadabilityConfiguration {

	KINCAID("kincaid"),
	ARI("ari"),
	COLEMAN_LIAU("coleman_liau"),
	FLESH("flesch"),
	FOG("fog"),
	LIX("lix"),
	SMOG("smog");

	private String stringValue;
	
	ReadabilityConfiguration(String stringValue) {
		this.stringValue = stringValue;
	}
	
	public String getStringValue() {
		return stringValue;
	}
}
