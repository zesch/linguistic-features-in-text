package org.lift.higherorder.genuine;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.Set;

import org.apache.uima.jcas.JCas;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.lift.api.Configuration.Language;
import org.lift.api.Feature;
import org.lift.features.util.FeatureTestUtil;
import org.lift.preprocessing.PreprocessingConfiguration;
import org.lift.preprocessing.TestUtils;

public class FE_SyntaxTreeDepthTest {

	@Test
	public void syntaxTreeDepthFeatureExtractorTest_DE()
        throws Exception
	{
		String document = "Dies ist ein Satz, der immer verschachltelt und lanweilig zu lesen. Er ist dafür kurz.";
		JCas jcas = TestUtils.getJCasForString(document, new PreprocessingConfiguration(Language.German));

        FE_SyntaxTreeDepth extractor = new FE_SyntaxTreeDepth(Language.German);
        Set<Feature> features = extractor.extract(jcas);

        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.AVG_SYNTAX_TREE_DEPTH, 3.5, features, 0.0001),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.TOTAL_SYNTAX_TREE_DEPTH, 7.0, features, 0.0001)
        		);
    }
	
	@Test
	public void syntaxTreeDepthFeatureExtractorTest_EN()
        throws Exception
    {
		String document = "This is a sentence that is nested and boring to read. But it is short.";
		JCas jcas = TestUtils.getJCasForString(document, new PreprocessingConfiguration(Language.English));

        FE_SyntaxTreeDepth extractor = new FE_SyntaxTreeDepth(Language.English);
        Set<Feature> features = extractor.extract(jcas);

        Assertions.assertAll(
        		() -> assertEquals(2, features.size()),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.AVG_SYNTAX_TREE_DEPTH, 6.0, features, 0.0001),
        		() -> FeatureTestUtil.assertFeatures(FE_SyntaxTreeDepth.TOTAL_SYNTAX_TREE_DEPTH, 12.0, features, 0.0001)
        );
    }
}