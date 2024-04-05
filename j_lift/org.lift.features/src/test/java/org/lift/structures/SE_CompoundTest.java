package org.lift.structures;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.apache.uima.fit.factory.ExternalResourceFactory.createResourceDescription;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.Collection;
import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.fit.util.JCasUtil;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.decompounding.uima.annotator.CompoundAnnotator;
import org.dkpro.core.decompounding.uima.resource.AsvToolboxSplitterResource;
import org.dkpro.core.decompounding.uima.resource.SharedDictionary;
import org.dkpro.core.decompounding.uima.resource.SharedLinkingMorphemes;
import org.dkpro.core.decompounding.uima.resource.SharedPatriciaTries;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.type.Structure;

class SE_CompoundTest {

	@Test
	void compoundTest() throws Exception {

		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription compoundAnnotator = createEngineDescription(CompoundAnnotator.class,
				CompoundAnnotator.RES_SPLITTING_ALGO,
				createResourceDescription(AsvToolboxSplitterResource.class,
						AsvToolboxSplitterResource.PARAM_DICT_RESOURCE,
						createResourceDescription(SharedDictionary.class),
						AsvToolboxSplitterResource.PARAM_MORPHEME_RESOURCE,
						createResourceDescription(SharedLinkingMorphemes.class),
						AsvToolboxSplitterResource.PARAM_PATRICIA_TRIES_RESOURCE,
						createResourceDescription(SharedPatriciaTries.class)));
		AnalysisEngineDescription compound = createEngineDescription(SE_Compound.class);
		AnalysisEngineDescription description = createEngineDescription(segmenter, compoundAnnotator, compound);
		AnalysisEngine engine = createEngine(description);

		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("de");
		jcas.setDocumentText("Die Regenwettervorhersage verlangt nach Regenschutzkleidung.");
		engine.process(jcas);

		Collection<Structure> structures = JCasUtil.select(jcas, Structure.class);

		Assertions.assertAll(
				// 12 words and 1 phrase
				() -> assertEquals(2, structures.size()),
				() -> assertEquals("Compound", structures.iterator().next().getName()));
	}

}
