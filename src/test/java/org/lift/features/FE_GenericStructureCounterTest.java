package org.lift.features;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.fit.component.NoOpAnnotator;
import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.structures.SEL_RutaFile;
import org.lift.type.Structure;

import de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token;

public class FE_GenericStructureCounterTest {

	@Test
	public void countFE_test()
		throws Exception
	{
		
		String structureName = "comma";
		AnalysisEngine engine = createEngine(NoOpAnnotator.class);

        JCas jcas = engine.newJCas();
        engine.process(jcas);
        jcas.setDocumentText("test ,");

        Token t1 = new Token(jcas, 0, 4);
        t1.addToIndexes();
        
        Token t2 = new Token(jcas, 5, 6);
        t2.addToIndexes();
        
        Structure s1 = new Structure(jcas, t2.getBegin(), t2.getEnd());
        s1.setName(structureName);
        s1.addToIndexes();
        
		FEL_GenericStructureCounter fe = new FEL_GenericStructureCounter(structureName);
		
		Set<Feature> features = fe.extract(jcas);
		
		Assertions.assertAll(
		        () -> assertEquals(1, features.size()),
		        () -> FeatureTestUtil.assertFeatures(fe.getInternalName(), 0.5, features, 0.00001)
				);

        System.out.println(features);
	}
	
	@Test
	public void countNominalization_test() throws Exception {
	AnalysisEngine engine = createEngine(NoOpAnnotator.class);



	JCas jcas = engine.newJCas();
	engine.process(jcas);

	jcas.setDocumentText("test Freiheit");



	Token t1 = new Token(jcas, 0, 4);
	t1.addToIndexes();

	Token t2 = new Token(jcas, 5, 9);
	t2.addToIndexes();

	String filePath = "src/main/resources/nominalization_de.ruta";
	String expectedStructureName = "Nominalization";
	SEL_RutaFile se = new SEL_RutaFile(filePath, expectedStructureName);
	se.process(jcas);

	FEL_GenericStructureCounter fe = new FEL_GenericStructureCounter(expectedStructureName);

	Set<Feature> features = fe.extract(jcas);

	Assertions.assertAll(
	() -> assertEquals(1, features.size()),
	() -> FeatureTestUtil.assertFeatures(fe.getInternalName(), 0.5, features, 0.00001)
	);



	System.out.println(features);
	}
}
