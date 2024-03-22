package org.lift.higherorder.genuine;

import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngine;
import static org.apache.uima.fit.factory.AnalysisEngineFactory.createEngineDescription;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;

import org.apache.uima.analysis_engine.AnalysisEngine;
import org.apache.uima.analysis_engine.AnalysisEngineDescription;
import org.apache.uima.jcas.JCas;
import org.dkpro.core.matetools.MateLemmatizer;
import org.dkpro.core.matetools.MateMorphTagger;
import org.dkpro.core.tokit.BreakIteratorSegmenter;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.api.Configuration.Language;

class FE_MorphologicalFeaturesTest {

	@Test
	void morphologicalFeaturesTest() throws Exception {
		
		AnalysisEngineDescription segmenter = createEngineDescription(BreakIteratorSegmenter.class);
		AnalysisEngineDescription lemmatizer  = createEngineDescription(
				MateLemmatizer.class,
				MateLemmatizer.PARAM_LANGUAGE, Language.German.code);
		AnalysisEngineDescription morphTagger = createEngineDescription(
				MateMorphTagger.class, MateMorphTagger.PARAM_LANGUAGE, Language.German.code);
		AnalysisEngineDescription description = createEngineDescription(segmenter,lemmatizer,morphTagger);
		AnalysisEngine engine = createEngine(description);
		JCas jcas = engine.newJCas();
		jcas.setDocumentLanguage("en");
		jcas.setDocumentText("Wir brauchen ein Beispiel, das viele finite Verben enthält");
		engine.process(jcas);
		
		FE_MorphologicalFeatures extractor = new FE_MorphologicalFeatures();
		Set<Feature> features = extractor.extract(jcas);
		Assertions.assertAll(
				() -> assertEquals(6, features.size()),
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_1_PERSON_SG_RATIO,0.0000,features, 0.0001),
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_2_PERSON_SG_RATIO,0.0000,features, 0.0001),
				// enthält -> 3.Person Singular
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_3_PERSON_SG_RATIO,0.5,features, 0.0001),
				// brauchen -> 1.Person Plural
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_1_PERSON_PL_RATIO,0.5,features, 0.0001),
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_2_PERSON_PL_RATIO,0.0000,features, 0.0001),
				() -> FeatureTestUtil.assertFeatures(FE_MorphologicalFeatures.FINITE_VERB_3_PERSON_PL_RATIO,0.0000,features, 0.0001)
				);
	}

}
