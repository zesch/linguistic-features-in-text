package org.lift.api;

import org.apache.uima.fit.component.JCasAnnotator_ImplBase;

public abstract class StructureExtractor 
	extends JCasAnnotator_ImplBase
{

	public abstract String getPublicStructureName();
	
	public String getStructureName() {
		return this.getClass().getName() + "/" + getPublicStructureName();
	};

}